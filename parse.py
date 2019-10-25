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

sub_list = {'print': 'template.PL_PRINT'}

assignable_token = ['ID', 'INT', 'FLOAT', 'STR', 'BIN', 'OCT', 'HEX', 'BOOL']

this_token = []

class PL_SyntaxError(Exception):
    pass


class PL_NameError(Exception):
    pass

def args_check(lex_iter, mode, mainid):
    global this_token, define_id
    argc = 0
    this_token = token = lex_iter.__next__()
    data = '('
    if mode == 'create':
        args_token = ['ID']
    else:
        args_token = assignable_token
    if token[0] in args_token:
        while token[0] in args_token:
            sid = token[1]
            data += token[1]
            argc += 1
            this_token = token = lex_iter.__next__()
            if token[0] == 'COMMA':
                data += ', '
                this_token = token = lex_iter.__next__()
                continue
            elif token[0] == 'RPAR':
                break
            elif token[0] == 'LPAR':
                data += args_check(lex_iter, 'call', sid)
                this_token = token = lex_iter.__next__()
                if token[0] == 'COMMA':
                    data += ', '
                    this_token = token = lex_iter.__next__()
                    continue
                elif token[0] == 'RPAR':
                    break
                else:
                    raise PL_SyntaxError("missing of ')'")
        else:
            raise PL_SyntaxError('invalid syntax')
    elif token[0] != 'RPAR':
        raise PL_SyntaxError("missing of ')'")
    data += ')'
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
    mode = [['module', '<main>']]
    try:
        while True:
            data = ''
            data += '  ' * indent
            this_token = token = lex_data.__next__()
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
                    continue                  # 関数呼び出しここまで
                elif token[0] == 'EQ':        #代入
                    data += mainid + ' = '
                    this_token = token = lex_data.__next__()
                    if token[0] == 'ID':
                        sid = token[1]
                        data += token[1]
                        this_token = token = lex_data.__next__()
                        if token[0] == 'LPAR':
                            data += args_check(lex_data, 'call', sid)
                        data += '\n'
                        result += data
                        continue
                    elif token[0] in assignable_token:
                        data += 'template.PL_{}({})\n'.format(token[0], token[1])
                        result += data
                        continue                  # 代入ここまで

            elif token[0] == 'ENDFUNC':       # 関数定義部終わり
                if mode[-1][0] == 'func':
                    indent -= 1
                    mode.pop(-1)
                    continue

            raise PL_SyntaxError(token)
    except StopIteration:
        return result
    except PL_SyntaxError as e:
        print(err_fmt.format(filename, this_token[2], mode[-1][1]))
        print('  {}'.format(source.split('\n')[this_token[2][0]-1]))
        print('  ' + ' '*(this_token[2][1]-1) + '^')
        print('SyntaxError:', e)
        exit(1)
    except PL_NameError as e:
        print(err_fmt.format(filename, this_token[2], mode[-1][1]))
        print('  {}'.format(source.split('\n')[this_token[2][0]]))
        print('  ' + ' '*(this_token[2][1]-1) + '^')
        print('NameError:', e)
        exit(1)



main()
