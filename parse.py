import lex
import sys

if len(sys.argv) != 2:
    exit

filename = 'test.txt'
with open(filename, 'r') as f:
    source = f.read()


def main():
    lex_iter = lex.lex(source)
    parse_data = parse(lex_iter)
    with open('out.py', 'w') as f:
        f.write(parse_data)
    


define_id = {
    'print': ['FUNC', 'ANY'],
    'puts': ['FUNC', 'ANY'],
    'input': ['FUNC', 'ANY'],
    'type': ['FUNC', 1]
}

func_list = {'printf': 'template.PL_PRINT'}
type_list = {
    'int': 'pl_int',
    'str': 'pl_str',
    'float': 'pl_float',
    'list': 'pl_list',
    'dict': 'pl_dict',
    'py_int': 'int',
    'py_str': 'str',
    'py_float': 'float',
    'py_list': 'list',
    'py_dict': 'dict'
}

prop_list = {'use_py_type': False}

assignable_token = ['ID', 'INT', 'FLOAT', 'STR', 'BIN', 'OCT', 'HEX', 'BOOL']

this_token = []

class PL_SyntaxError(Exception):
    name = 'Syntax error'


class PL_NameError(Exception):
    name = 'Name error'


class PL_TypeError(Exception):
    name = 'Type error'


def print_err(e, running_func):
    print('File:"{}", line:{} in {}'.format(filename, this_token[2], running_func[-1]))
    print('  {}'.format(source.split('\n')[this_token[2][0]-1]))
    print('  ' + ' '*(this_token[2][1]-1) + '^')
    print(e.name + ' :', e)
    exit(1)


def operator_check(lex_iter, mode='normal'):
    global this_token
    try:
        data = ''
        follow = 'oper' if mode == 'opstart' else None
        continue_Token = True
        minus = False
        bracket = 0
        while True:
            if not follow:
                this_token = token = lex_iter.__next__()
                if token[0] == 'LPAR':
                    data += '('
                    bracket += 1
                    continue
                if token[0] == 'ID':
                    continue_Token = False
                    subid = token[1]
                    data += token[1]
                    this_token = token = lex_iter.__next__()
                    if token[0] == 'LPAR':
                        data += args_check(lex_iter, 'call', subid)
                        continue_Token = True
                elif token[0] in ['INT', 'FLOAT'] and minus:
                    if prop_list['use_py_type']:
                        data += ' -' + token[1]
                    else:
                        data += 'template.PL_{}(-{})'.format(token[0], token[1])
                    minus = False
                elif token[0] in assignable_token:
                    if prop_list['use_py_type']:
                        if token[0] == 'BOOL':
                            data += 'True' if token[1] == 'true' else 'False'
                        else:
                            data += token[1]
                    else:
                        data += 'template.PL_{}({})'.format(token[0], token[1])
                elif token[0] == 'ADD':
                    continue
                elif token[0] == 'SUB':
                    minus = True
                    continue
                else:
                    raise PL_SyntaxError("invalid syntax")
            if minus:
                raise PL_TypeError("bad operand type for unary -: {}".format(token[0]))
            if continue_Token:
                this_token = token = lex_iter.__next__()
            
            follow = None
            continue_Token = True
            if token[0] == 'ADD':
                data += ' + '
            elif token[0] == 'SUB':
                data += ' - '
            elif token[0] == 'MUL':
                data += ' * '
            elif token[0] == 'DIV':
                data += ' / '
            elif token[0] == 'DOT':
                data += '.'
            elif token[0] == 'EQ':
                data += ' = '
            elif token[0] == 'EQ2':
                data += ' == '
            elif token[0] == 'ADDEQ':
                data += ' += '
            elif token[0] == 'SUBEQ':
                data += ' -= '
            elif token[0] == 'MULEQ':
                data += ' *= '
            elif token[0] == 'DIVEQ':
                data += ' /= '
            elif token[0] == 'LCLS':
                data += ' < '
            elif token[0] == 'RCLS':
                data += ' > '
            elif token[0] == 'LCLS_EQ':
                data += ' <= '
            elif token[0] == 'RCLS_EQ':
                data += ' >= '
            elif token[0] == 'AMP':
                data += ' & '
            elif token[0] == 'VERT':
                data += ' | '
            elif token[0] == 'CAR':
                data += ' ^ '
            elif token[0] == 'OR':
                data += ' or '
            elif token[0] == 'AND':
                data += ' and '
            elif token[0] == 'NOT':
                data += ' not '
            elif token[0] == 'VERT2':
                data += ' or '
            elif token[0] == 'AMP2':
                data += ' and '
            elif token[0] == 'EX':
                data += ' not '
            elif token[0] == 'RAR':
                this_token = token = lex_iter.__next__()
                if token[0] == 'ID':
                    if token[1] in type_list and not prop_list['use_py_type']:
                        cast_type = type_list[token[1]]
                    else:
                        cast_type = token[1]
                    data += '.__{}__()'.format(cast_type)
                    follow = 'oper'
            elif token[0] == 'RPAR':
                if bracket <= 0:
                    if mode == 'args':
                        break
                    else:
                        raise PL_SyntaxError('invalid syntax')
                data += ')'
                bracket -= 1
                follow = 'oper'
            elif token[0] == 'COMMA':
                if mode == 'args':
                    break
            elif token[0] in ['LF', 'ID', 'DO']:
                break
        return data, token
    except StopIteration:
        return data
        

def args_check(lex_iter, mode, mainid):
    global this_token, define_id
    data = '('
    argc = 0
    while True:
        argc += 1
        temp, token = operator_check(lex_iter, 'args')
        data += temp
        if token[0] == 'COMMA':
            data += ', '
        elif token[0] == 'RPAR':
            data += ')'
            break
    if mode == 'call':
        if not mainid in define_id:
            raise PL_NameError("name '" + mainid + "' is not defined")
        elif define_id[mainid][0] != 'FUNC':
            raise PL_SyntaxError(mainid + 'is not callable')
        elif define_id[mainid][1] != 'ANY' and define_id[mainid][1] != argc:
            raise PL_SyntaxError('too many or less argument(s): "' + mainid + '()"')
        return data
    elif mode == 'create':
        return data, argc


def parse(lex_list):
    global define_id, this_token, prop_list
    lex_iter = iter(lex_list)
    result = 'import template\n'
    indent = 0
    running_func = ['main']
    mode = [['module', '<main>']]
    comment_depth = 0
    this_token = token = lex_iter.__next__()
    try:
        while True:
            temp = ''
            mainid = ''
            subid = ''
            data = ''
            data += '  ' * indent
            this_token = token

            if token[0] == 'HASH':  # プロパティの設定
                this_token = token = lex_iter.__next__()
                if token[0] == 'ID':
                    mainid = token[1]
                    this_token = token = lex_iter.__next__()
                    if token[0] in ['COR', 'EQ'] and mainid in prop_list:
                        this_token = token = lex_iter.__next__()
                        if token[0] == 'BOOL':
                            temp = True if token[1] == 'true' else False
                            prop_list[mainid] = temp
                            token = lex_iter.__next__()
                            continue
                # プロパティの設定 ここまで

            elif token[0] == 'FUNC':       # 関数定義
                data += 'def '
                token = lex_iter.__next__()
                if token[0] == 'ID':
                    mainid = token[1]
                    data += token[1]
                    this_token = token = lex_iter.__next__()
                    if token[0] == 'LPAR':
                        temp, argc = args_check(lex_iter, 'create', mainid)
                        data += temp
                    this_token = token = lex_iter.__next__()
                    if token[0] == 'DO':
                        data += ':\n'
                        indent += 1
                        define_id[mainid] = ['FUNC', argc]
                        mode.append(['FUNC', mainid, token[2]])
                        running_func.append(mainid)
                        while True:
                            token = lex_iter.__next__()
                            if token[0] != 'LF':
                                break
                        if token[0] == 'ENDFUNC':
                            data += '  ' * indent + 'pass\n'
                        result += data
                        continue
                # 関数定義ここまで

            elif token[0] == 'ENDFUNC':       # 関数定義ブロック終わり
                if mode[-1][0] == 'FUNC':
                    temp = result.split('\n')
                    temp[-2] = '  '*indent + 'return ' + temp[-2][2*indent:]
                    result = '\n'.join(temp)
                    indent -= 1
                    result += '  '*indent + '# endfunc: {}\n'.format(mode[-1][1])
                    mode.pop(-1)
                    running_func.pop(-1)
                    token = lex_iter.__next__()
                    continue
                # 関数定義ブロック終わり ここまで
            
            elif token[0] == 'ID':
                mainid = token[1]
                this_token = token = lex_iter.__next__()
                if token[0] == 'LPAR':         # 関数呼び出し
                    if mainid in func_list:
                        data += func_list[mainid]
                    else:
                        data += mainid
                    data += args_check(lex_iter, 'call', mainid)
                    data += '\n'
                    result += data
                    token = lex_iter.__next__()
                    continue
                # 関数呼び出しここまで

                elif token[0] == 'ID':       # 引数が1個の関数の可能性？
                    if mainid in func_list:
                        if func_list[mainid][1] in ['ANY', 1]:
                            data += '{}({})'.format(mainid, token[1])
                            temp, token = operator_check(lex_iter, mode='opstart')
                            data += temp + '\n'
                            result += data
                            continue


                elif token[0] == 'EQ':        #代入
                    data += mainid + ' = '
                    temp, token = operator_check(lex_iter)
                    data += temp + '\n'
                    result += data
                    continue
                # 代入ここまで
            
            elif token[0] == 'IF':  # if文
                data += 'if '
                temp, token = operator_check(lex_iter)
                if token[0] == 'DO':
                    mainid = temp
                    mode.append(['IF', temp, token[2]])
                    data += temp + ': # {}\n'.format(token[2][0])
                    indent += 1
                    while True:
                        token = lex_iter.__next__()
                        if token[0] != 'LF':
                            break
                    if token[0] == 'ENDFUNC':
                        data += '  ' * indent + 'pass\n'
                    result += data
                    continue
                # if文ここまで
            
            elif token[0] == 'ELSIF':    # else if文
                if mode[-1][0] in ['IF', 'ELSIF']:
                    temp = mode[-1][2]
                    mode.pop(-1)
                    mode.append(['ELSIF', temp, temp])
                    data = data[:-2] + 'elif '
                    temp, token = operator_check(lex_iter)
                    if token[0] == 'DO':
                        data += temp + ':\n'
                        while True:
                            token = lex_iter.__next__()
                            if token[0] != 'LF':
                                break
                        if token[0] == 'ENDFUNC':
                            data += '  ' * indent + 'pass\n'
                        result += data
                        continue

            elif token[0] == 'ELSE':     # else文
                if mode[-1][0] in ['IF', 'ELSIF']:
                    temp = mode[-1][2]
                    mode.pop(-1)
                    mode.append(['ELSE', temp, temp])
                    this_token = token = lex_iter.__next__()
                    if token[0] == 'DO':
                        data = data[:-2] + 'else:\n'
                        while True:
                            token = lex_iter.__next__()
                            if token[0] != 'LF':
                                break
                        if token[0] == 'ENDIF':
                            data += '  ' * indent + 'pass\n'
                        result += data
                        continue

            elif token[0] == 'ENDIF':       # if文ブロック終わり
                if mode[-1][0] in ['IF', 'ELSIF', 'ELSE']:
                    indent -= 1
                    data = data[:-2] + '# endif {}\n'.format(mode[-1][2][0])
                    result += data
                    mode.pop(-1)
                    token = lex_iter.__next__()
                    continue
                # if文ブロック終わり ここまで

            elif token[0] == 'FOR':       # for文
                data += 'for '
                token = lex_iter.__next__()
                if token[0] == 'ID':
                    mainid = token[1]
                    data += mainid
                    this_token = token = lex_iter.__next__()
                    if token[0] == 'IN':
                        data += ' in '
                        this_token = token = lex_iter.__next__()
                        if token[0] == 'ID':
                            subid = token[1]
                            data += subid
                            this_token = token = lex_iter.__next__()
                            if token[0] == 'DO':
                                mode.append(['FOR', temp, token[2]])
                                data += temp + ': # {}\n'.format(token[2][0])
                                indent += 1
                                while True:
                                    token = lex_iter.__next__()
                                    if token[0] != 'LF':
                                        break
                                if token[0] == 'ENDLOOP':
                                    data += '  ' * indent + 'pass\n'
                                result += data
                                continue
                # for文ここまで

            elif token[0] == 'WHILE':      # while文
                data += 'while '
                temp, token = operator_check(lex_iter)
                if token[0] == 'DO':
                    mode.append(['WHILE', temp, token[2]])
                    data += temp + ': # {}\n'.format(token[2][0])
                    indent += 1
                    while True:
                        token = lex_iter.__next__()
                        if token[0] != 'LF':
                            break
                    if token[0] == 'ENDLOOP':
                        data += '  ' * indent + 'pass\n'
                    result += data
                    continue
                # while文ここまで

            elif token[0] == 'ENDLOOP':
                if mode[-1][0] in ['FOR', 'WHILE']:
                    indent -= 1
                    data = data[:-2] + '# endloop {}\n'.format(mode[-1][2][0])
                    result += data
                    mode.pop(-1)
                    token = lex_iter.__next__()
                    continue

            elif token[0] == 'LF':
                token = lex_iter.__next__()
                continue
            elif token[0] in assignable_token:
                token = lex_iter.__next__()
                continue

            raise PL_SyntaxError('invalid syntax')
    except StopIteration:
        return result
    except PL_SyntaxError as e:
        print_err(e, running_func)
    except PL_NameError as e:
        print_err(e, running_func)
    except PL_TypeError as e:
        print_err(e, running_func)



main()
