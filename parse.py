import lex
import sys

if len(sys.argv) != 2:
    exit

filename = sys.argv[1]
with open(filename, 'r') as f:
    source = f.read()


def main():
    lex_data = lex.lex(source)
    parse_data = parse(lex_data)
    with open('out.py', 'w') as f:
        f.write(parse_data)
    

err_fmt = 'File:"{}", line:{} in {}'

define_id = {
    'print': ['func', 'any'],
    'puts': ['func', 'any'],
    'input': ['func', 'any']
}

sub_list = {'printf': 'template.PL_PRINT'}

assignable_token = ['ID', 'INT', 'FLOAT', 'STR', 'BIN', 'OCT', 'HEX', 'BOOL']

this_token = []

class PL_SyntaxError(Exception):
    pass


class PL_NameError(Exception):
    pass


def operator_check(lex_data, mode='gen'):
    try:
        data = ''
        follow = None
        bracket = 0
        while True:
            if follow != 'oper':
                this_token = token = lex_data.__next__()
                if token[0] == 'LPAR':
                    data += '('
                    bracket += 1
                    continue
                if token[0] == 'ID':
                    sid = token[1]
                    data += token[1]
                    this_token = token = lex_data.__next__()
                    if token[0] == 'LPAR':
                        data += args_check(lex_data, 'call', sid)
                    if token[0] in ['ID', 'RPAR']:
                        return data, token
                elif token[0] in assignable_token:
                    data += 'template.PL_{}({})'.format(token[0], token[1])
                else:
                    raise PL_SyntaxError("invalid syntax")
            this_token = token = lex_data.__next__()
            follow = None
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
                this_token = token = lex_data.__next__()
                if token[0] == 'ID':
                    data += '.__{}__()'.format(token[1])
                    follow = 'oper'
            elif token[0] == 'RPAR':
                if bracket <= 0:
                    if mode == 'args':
                        break
                    else:
                        raise PL_SyntaxError('invalid syntax')
                data += ')'
                bracket -= 1
            elif token[0] == 'COMMA':
                if mode == 'args':
                    break
            elif token[0] in ['LF', 'ID']:
                break
        return data, token
    except StopIteration:
        return data
        

def args_check(lex_iter, mode, mainid):
    global this_token, define_id
    argc = 0
    data = '('
    while True:
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
        elif define_id[mainid][0] != 'func':
            raise PL_SyntaxError(mainid + 'is not callable')
        elif define_id[mainid][1] != 'any' and define_id[mainid][1] != argc:
            raise PL_SyntaxError(
                'too many or less argument(s): "' + mainid + '()"')
        return data
    elif mode == 'create':
        return data, argc


def parse(lex_list):
    global define_id, this_token
    result = 'import template\n'
    indent = 0
    lex_data = iter(lex_list)
    running_func = ['main']
    mode = [['module', '<main>']]
    this_token = token = lex_data.__next__()
    try:
        while True:
            data = ''
            data += '  ' * indent
            if token[0] == 'FUNC':       # 関数定義
                data += 'def '
                this_token = token = lex_data.__next__()
                if token[0] == 'ID':
                    mainid = token[1]
                    data += token[1]
                    this_token = token = lex_data.__next__()
                    if token[0] == 'LPAR':
                        temp, argc = args_check(lex_data, 'create', mainid)
                        data += temp
                    this_token = token = lex_data.__next__()
                    if token[0] == 'DO':
                        data += ':\n'
                        indent += 1
                        result += data
                        define_id[mainid] = ['func', argc]
                        mode.append(['func', mainid])
                        this_token = token = lex_data.__next__()
                        running_func.append(mainid)
                        continue             # 関数定義ここまで
            
            elif token[0] == 'ID':
                mainid = token[1]
                this_token = token = lex_data.__next__()
                if token[0] == 'LPAR':         # 関数呼び出し
                    if mainid in sub_list:
                        data += sub_list[mainid]
                    else:
                        data += mainid
                    data += args_check(lex_data, 'call', mainid)
                    data += '\n'
                    result += data
                    this_token = token = lex_data.__next__()
                    continue                  # 関数呼び出しここまで
                elif token[0] == 'EQ':        #代入
                    data += mainid + ' = '
                    temp, token = operator_check(lex_data)
                    data += temp + '\n'
                    result += data
                    continue
            elif token[0] == 'LF':
                this_token = token = lex_data.__next__()
                continue

            elif token[0] == 'ENDFUNC':       # 関数定義部終わり
                if mode[-1][0] == 'func':
                    indent -= 1
                    mode.pop(-1)
                    running_func.pop(-1)
                    this_token = token = lex_data.__next__()
                    continue

            raise PL_SyntaxError('invalid syntax')
    except StopIteration:
        return result
    except PL_SyntaxError as e:
        print(err_fmt.format(filename, this_token[2], running_func[-1]))
        print('  {}'.format(source.split('\n')[this_token[2][0]-1]))
        print('  ' + ' '*(this_token[2][1]-1) + '^')
        print('SyntaxError:', e)
        exit(1)
    except PL_NameError as e:
        print(err_fmt.format(filename, this_token[2], running_func[-1]))
        print('  {}'.format(source.split('\n')[this_token[2][0]]))
        print('  ' + ' '*(this_token[2][1]-1) + '^')
        print('NameError:', e)
        exit(1)



main()
