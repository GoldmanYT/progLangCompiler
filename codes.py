from enum import Enum


class Code(Enum):
    PROG = 'prog'  # procedure15
    USING = 'using'  # using15
    CLASS = 'class'  # class15
    VAR = 'var'  # var15
    WHILE = 'while'  # while15
    TRUE = 'true'
    FALSE = 'false'
    FULLNAME = 'FIO'  # KuznetsovDA
    SEMI = ';'
    COLON = ':'
    DOT = '.'
    OP_PAR = '('
    CL_PAR = ')'
    OP_CUR_BR = '{'
    CL_CUR_BR = '}'
    ASS = 'ass'  # <-
    ADD = '+'  # + | -
    MULT = '*'  # * | /
    NOT = '!'
    AND = '&&'
    OR = '||'
    REL = 'rel'  # < | <= | = | >= | > | /=
    ID = 'id'  # identifier
    NUM = 'num'  # number
    SP = 'sp'  # space | tab | new line
    COM = 'com'  # commentary
    EOF = 'eof'  # end of file
    ERR = 'err'  # error
    GOTO = 'goto'
    IF = 'if'

    def get_lex_info(self):
        names = {
            Code.PROG: 'procedure15',
            Code.USING: 'using15',
            Code.CLASS: 'class15',
            Code.VAR: 'var15',
            Code.WHILE: 'while15',
            Code.FULLNAME: 'KuznetsovDA',
            Code.ASS: '<-',
            Code.ADD: 'аддитивная операция',
            Code.MULT: 'мультипликативная операция',
            Code.REL: 'операция отношения',
            Code.ID: 'идентификатор',
            Code.NUM: 'число',
        }

        if self in names:
            return names[self]

        return self.value
