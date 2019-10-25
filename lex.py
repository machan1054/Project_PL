import re

source="""
func print(string) do
    if string != '' do
        pp(string)
    endif
endfunc
print('test')
num = 0x1F -> str
"""

regre = [
        [r'class', 'CLASS'],
        [r'endclass', 'ENDCLASS'],
        [r'func', 'FUNC'],
        [r'endfunc', 'ENDFUNC'],
        [r'do', 'DO'],
        [r'end', 'END'],
        [r'for', 'FOR'],
        [r'while', 'WHILE'],
        [r'endloop', 'ENDLOOP'],
        [r'if', 'IF'],
        [r'else', 'ELSE'],
        [r'endif', 'ENDIF'],
        [r'return', 'RETURN'],
        [r'continue', 'CONTINUE'],
        [r'break', 'BREAK'],
        [r'and', 'AND'],
        [r'or', 'OR'],
        [r'not', 'NOT'],
        [r'true', 'BOOL'],
        [r'false', 'BOOL'],
        [r"'.*'", 'STR'],
        [r'".*"', 'STR'],
        [r'0b[01]+', 'BIN'],
        [r'0o[0-7]+', 'OCT'],
        [r'0x[0-9A-Fa-f]+', 'HEX'],
        [r'[a-z][a-z0-9]*', 'ID'], 
        [r'0|[1-9][0-9]*', 'INT'],
        [r'-0|[1-9][0-9]*', 'INT'],
        [r'0|[1-9][0-9]*[eE][+-]{0,1}[0-9]+', 'INT'],
        [r'-0|[1-9][0-9]*[eE][+-]{0,1}[0-9]+', 'INT'],
        [r'([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)', 'FLOAT'],
        [r'-([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)', 'FLOAT'],
        [r'([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)[eE][+-]{0,1}[0-9]*', 'FLOAT'], 
        [r'-([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)[eE][+-]{0,1}[0-9]*', 'FLOAT'],
        [r',', 'COMMA'],
        [r'\^', 'CAR'],
        [r'<-', 'LAR'],
        [r'->', 'RAR'],
        [r'<', 'LCLS'],
        [r'>', 'RCLS'],
        [r'<=', 'LCLS_EQ'],
        [r'>=', 'RCLS_EQ'],
        [r'==', 'EQ2'],
        [r'=', 'EQ'],
        [r'!=', 'NOTEQ'],
        [r'\+=', 'ADDEQ'],
        [r'-=', 'SUBEQ'],
        [r'\*=', 'MULEQ'],
        [r'/=', 'DIVEQ'],
        [r'!', 'EX'],
        [r'@', 'AT'],
        [r'\?', 'QU'],
        [r'%', 'SUR'],
        [r'&', 'AMP'],
        [r'\|', 'VERT'],
        [r'&&', 'AMP2'],
        [r'\|\|', 'VERT2'],
        [r'\+\+', 'INC'],
        [r'--', 'DEC'],
        [r'\+', 'ADD'],
        [r'-', 'SUB'],
        [r'\*', 'MUL'],
        [r'/', 'DIV'],
        [r'\.', 'DOT'],
        [r'\(', 'LPAR'],
        [r'\)', 'RPAR'],
        [r'\n', 'LF'],
        ['[\ \?\t]', None],
        ['//.+', None],
        ['.', 'ERROR']
]  



def lex(s, line_n=1, row=1):
    result = []
    for r in regre:
        match = re.match(r[0], s)
        if match:
            result.append([r, match.group()])
    if len(result) != 0:
        length = [len(i[1]) for i in result]
        maxdata = result[length.index(max(length))]
        if maxdata:
            result3 = [maxdata[0][1], maxdata[1], (line_n, row)]
            row += len(maxdata[1])
            line2 = re.sub(r'^' + maxdata[0][0], '', s, count=1)
            result4 = []
            if result3[0] == 'LF':
                line_n += 1
                row = 1
            if result3[0]:
                result4.append(result3)
            if len(line2) != 0:
                result5 = lex(line2, line_n, row)
                if result5:
                    result4.extend(result5)
            
            return result4
    return []

