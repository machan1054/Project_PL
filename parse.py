import lex
import sys

    
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

filename = 'test.txt'
with open(filename, 'r') as f:
    source = f.read()

def main():
    
    lex_iter = lex.lex(source)
    parse_data = parse(lex_iter)
    with open('out.py', 'w') as f:
        f.write(parse_data)


this_token = []

class PL_Exception(Exception):
    pass

class PL_SyntaxError(PL_Exception):
    name = 'Syntax error'


class PL_NameError(PL_Exception):
    name = 'Name error'


class PL_TypeError(PL_Exception):
    name = 'Type error'


def print_err(e, running_func):
    print('File:"{}", line:{} in {}'.format(filename, this_token[2], running_func[-1]))
    print('  {}'.format(source.split('\n')[this_token[2][0]-1]))
    print('  ' + ' '*(this_token[2][1]-1) + '^')
    print(e.name + ' :', e)
    exit(1)


def operator_check(lex_iter, mode='normal', token=[None, None]):
    global this_token
    try:
        data = ''
        follow = 'oper' if mode == 'opstart' else None
        continue_Token = True
        minus = False
        pass_next = mode in ['func call', 'func create']
        bracket = 0
        argc = 0
        while True:
            if not follow:
                if not pass_next:
                    this_token = token = lex_iter.__next__()
                pass_next = False
                if token[0] == 'ID':
                    argc += 1
                    continue_Token = False
                    subid = token[1]
                    data += token[1]
                    this_token = token = lex_iter.__next__()
                    if token[0] == 'LPAR':
                        temp, token = operator_check(lex_iter, 'func call', token)
                        bracket += 1
                        data += temp
                        continue_Token = False
                elif token[0] == 'LPAR':
                    data += '('
                    bracket += 1
                    continue
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
                    break
            
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
                bracket -= 1
                data += ')'
                if bracket <= 0:
                    this_token = token = lex_iter.__next__()
                    break
                follow = 'oper'
                if mode in ['func call', 'fumc create'] and bracket <= 0:
                    mode = 'normal'
            elif token[0] == 'COMMA':
                data += ', '
                if mode == 'args':
                    break
                if mode in ['func call', 'fumc create']:
                    continue
            else:
                break
        if mode == 'func create':
            return data, token, argc
        else:
            return data, token
    except StopIteration:
        return data
        

def args_check(lex_iter, mode, mainid):
    global this_token, define_id
    data = '('
    argc = 0
    token=None
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
                        temp, token, argc = operator_check(lex_iter, 'func create', token)
                        data += temp
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
                    temp, token = operator_check(lex_iter, 'func call', token)
                    data += mainid + temp + '\n'
                    result += data
                    continue
                # 関数呼び出しここまで

                elif token[0] == 'ID':       # 引数が1個の関数の可能性？
                    if mainid in define_id:
                        if define_id[mainid][1] in ['ANY', 1]:
                            data += '{}({})'.format(mainid, token[1])
                            temp, token = operator_check(lex_iter, 'opstart', token)
                            data += temp + '\n'
                            result += data
                            continue


                elif token[0] == 'EQ':        #代入
                    data += mainid + ' = '
                    temp, token = operator_check(lex_iter, token=token)
                    data += temp + '\n'
                    result += data
                    continue
                # 代入ここまで
            
            elif token[0] == 'IF':  # if文
                data += 'if '
                temp, token = operator_check(lex_iter, token=token)
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
                    temp, token = operator_check(lex_iter, token=token)
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
                this_token = token = lex_iter.__next__()
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
                                mode.append(['LOOP', temp, token[2]])
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
                temp, token = operator_check(lex_iter, token=token)
                if token[0] == 'DO':
                    mode.append(['LOOP', temp, token[2]])
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
                if 'LOOP' in [i[0] for i in mode]:
                    indent -= 1
                    data = data[:-2] + '# endloop {}\n'.format(mode[-1][2][0])
                    result += data
                    mode.pop(-1)
                    token = lex_iter.__next__()
                    continue

            elif token[0] == 'BREAK':
                if 'LOOP' in [i[0] for i in mode]:
                    data += 'break\n'
                    result += data
                    token = lex_iter.__next__()
                    continue
            
            elif token[0] == 'CONTINUE':
                if 'LOOP' in [i[0] for i in mode]:
                    data += 'continue\n'
                    result += data
                    token = lex_iter.__next__()
                    continue
            
            elif token[0] == 'RETURN':
                if running_func == 'main':
                    data += 'exit'
                    token = lex_iter.__next__()
                    if token[0] in assignable_token:
                        data += '({})'.format(token[1])
                else:
                    data += 'return'
                    temp, token = operator_check(lex_iter, token=token)
                    data += ' ' + temp
                result += data + '\n'
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
    except PL_Exception as e:
        print_err(e, running_func)



main()
