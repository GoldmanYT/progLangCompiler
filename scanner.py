from typing import Iterable
from attribute import Attribute
from category import Category
from char import Char
from codes import Code
from state import State
from identifier import Identifier
from tokens import Token
from collections import defaultdict

from type import Type
from typecode import TypeCode


class Scanner:
    VARIANT: str = '15'
    KEYWORDS: dict[str, Code] = {
        'procedure' + VARIANT: Code.PROG,
        Code.USING.value + VARIANT: Code.USING,
        Code.CLASS.value + VARIANT: Code.CLASS,
        Code.VAR.value + VARIANT: Code.VAR,
        Code.WHILE.value + VARIANT: Code.WHILE,
        Code.TRUE.value: Code.TRUE,
        Code.FALSE.value: Code.FALSE,
        'KuznetsovDA': Code.FULLNAME,
    }
    STATE_TABLE: dict[Char, dict[State, State]] = {
        Char.TAB: {
            State.INITIAL: State.SPACE,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.LF: {
            State.INITIAL: State.SPACE,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.SPACE: {
            State.INITIAL: State.SPACE,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.EXCL: {
            State.INITIAL: State.EXCL,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.AMP: {
            State.INITIAL: State.AMP,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.AMP_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.OP_PAR: {
            State.INITIAL: State.OP_PAR,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.CL_PAR: {
            State.INITIAL: State.CL_PAR,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.STAR: {
            State.INITIAL: State.STAR,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.PLUS: {
            State.INITIAL: State.PLUS,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.DASH: {
            State.INITIAL: State.DASH,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_DASH,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_DASH,
            State.DASH_DASH: State.DASH_DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH_DASH_DASH,
        },
        Char.DOT: {
            State.INITIAL: State.DOT,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_DOT,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.SLASH: {
            State.INITIAL: State.SLASH,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.COLON: {
            State.INITIAL: State.COLON,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.SEMICOLON: {
            State.INITIAL: State.SEMICOLON,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.LESS: {
            State.INITIAL: State.LESS,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.EQUALS: {
            State.INITIAL: State.EQUALS,
            State.SLASH: State.SLASH_EQUALS,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_EQUALS,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_EQUALS,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.GREATER: {
            State.INITIAL: State.GREATER,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.DIGIT: {
            State.INITIAL: State.DIGIT,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT,
            State.DIGIT_DOT: State.DIGIT_DOT_DIGIT,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.LETTER: {
            State.INITIAL: State.LETTER,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.OP_CUR_BR: {
            State.INITIAL: State.OP_CUR_BR,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.VERT_SLASH: {
            State.INITIAL: State.VERT_SLASH,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.VERT_SLASH_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.CL_CUR_BR: {
            State.INITIAL: State.CL_CUR_BR,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
        Char.EOF: {
            State.INITIAL: State.EOF,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.ERR_COMMENT_NOT_CLOSED,
            State.DASH_DASH_DASH: State.ERR_COMMENT_NOT_CLOSED,
        },
        Char.OTHER: {
            State.INITIAL: State.ERR_START,
            State.SLASH: State.SLASH_OTHER,
            State.AMP: State.ERR_AMP,
            State.VERT_SLASH: State.ERR_VERT_SLASH,
            State.LESS: State.LESS_OTHER,
            State.LETTER: State.LETTER_OTHER,
            State.GREATER: State.GREATER_OTHER,
            State.DIGIT: State.DIGIT_OTHER,
            State.DIGIT_DOT: State.ERR_NUMBER,
            State.DIGIT_DOT_DIGIT: State.DIGIT_DOT_DIGIT_OTHER,
            State.SPACE: State.SPACE_OTHER,
            State.DASH: State.DASH_OTHER,
            State.DASH_DASH: State.DASH_DASH,
            State.DASH_DASH_DASH: State.DASH_DASH,
        },
    }
    ERROR_MESSAGES = {
        State.ERR_START: 'Встречен неожиданный символ: "{lex}"',
        State.ERR_AMP: 'Встречено: "{lex}", ожидалось: "&"',
        State.ERR_VERT_SLASH: 'Встречено: "{lex}", ожидалось: "|"',
        State.ERR_NUMBER: 'Встречено: "{lex}", ожидалась цифра',
        State.ERR_COMMENT_NOT_CLOSED: 'Встречен конец файла, ожидалось: "--"',
    }
    SHIFT_BACK_TABLE: dict[State, int] = defaultdict(int, {
        State.SLASH_OTHER: 1,
        State.LESS_OTHER: 1,
        State.LETTER_OTHER: 1,
        State.GREATER_OTHER: 1,
        State.DIGIT_OTHER: 1,
        State.DIGIT_DOT_DIGIT_OTHER: 1,
        State.SPACE_OTHER: 1,
        State.DASH_OTHER: 1,
    })
    STATE_TO_TOKEN_PARAMS: dict[State, tuple] = {
        State.SEMICOLON: (Code.SEMI,),
        State.COLON: (Code.COLON,),
        State.DOT: (Code.DOT,),
        State.OP_PAR: (Code.OP_PAR,),
        State.CL_PAR: (Code.CL_PAR,),
        State.OP_CUR_BR: (Code.OP_CUR_BR,),
        State.CL_CUR_BR: (Code.CL_CUR_BR,),
        State.EXCL: (Code.NOT,),
        State.EQUALS: (Code.REL, Attribute.OP_EQ),
        State.PLUS: (Code.ADD, Attribute.OP_ADD),
        State.STAR: (Code.MULT, Attribute.OP_MULT),
        State.SLASH_OTHER: (Code.MULT, Attribute.OP_DIV),
        State.SLASH_EQUALS: (Code.REL, Attribute.OP_NE),
        State.AMP_AMP: (Code.AND,),
        State.VERT_SLASH_VERT_SLASH: (Code.OR,),
        State.LESS_OTHER: (Code.REL, Attribute.OP_LT),
        State.LESS_EQUALS: (Code.REL, Attribute.OP_LE),
        State.LESS_DASH: (Code.ASS,),
        State.LETTER_OTHER: (Code.ID,),
        State.GREATER_OTHER: (Code.REL, Attribute.OP_GT),
        State.GREATER_EQUALS: (Code.REL, Attribute.OP_GE),
        State.DIGIT_OTHER: (Code.NUM,),
        State.DIGIT_DOT_DIGIT_OTHER: (Code.NUM,),
        State.SPACE_OTHER: (Code.SP,),
        State.DASH_OTHER: (Code.ADD, Attribute.OP_SUB,),
        State.DASH_DASH_DASH_DASH: (Code.COM,),
        State.EOF: (Code.EOF,),
        State.ERR_START: (Code.ERR,),
        State.ERR_AMP: (Code.ERR,),
        State.ERR_VERT_SLASH: (Code.ERR,),
        State.ERR_NUMBER: (Code.ERR,),
        State.ERR_COMMENT_NOT_CLOSED: (Code.ERR,),
    }

    def __init__(self, code: str):
        self.code: str = code
        self.state: State = State.INITIAL
        self.pos: int = 0
        self.id_table: list[Identifier] = []
        self.restart()

        if not self.code.endswith(Char.EOF.value):
            self.code += Char.EOF.value

    @staticmethod
    def get_new_id_table(
            declared_identifiers: list[Identifier] = None
    ) -> list[Identifier]:

        id_table: list[Identifier] = []

        if declared_identifiers is None:
            for type_code in TypeCode:
                if type_code not in (TypeCode.NO_TYPE, TypeCode.STRUCT):
                    id_table.append(
                        Identifier(type_code.value, Category.TYPE_NAME, Type(id_table, type_code, len(type_code))))
        else:
            for identifier in declared_identifiers:
                if identifier.category == Category.TYPE_NAME:
                    id_table.append(identifier)

        return id_table

    def restart(self):
        self.state = State.INITIAL
        self.pos = 0
        self.id_table = self.get_new_id_table()

    def form_token(self, start: int) -> Token:
        token: Token = Token(*self.STATE_TO_TOKEN_PARAMS[self.state])
        token.start = start
        token.end = self.pos

        if token.code == Code.ERR:
            token.lex = self.ERROR_MESSAGES[self.state].format(lex=self.code[token.end - 1:token.end])
            return token

        if token.code not in (Code.NUM, Code.ID):
            return token

        token.lex = self.code[token.start:token.end]

        if token.lex in self.KEYWORDS:
            token.code = self.KEYWORDS[token.lex]
            token.lex = None
            return token

        identifier: Identifier | None = find_in_id_table(self.id_table, token.lex)
        if identifier is not None:
            token.attr = identifier
            return token

        if token.code == Code.NUM and self.state == State.DIGIT_OTHER:
            symbol = Identifier(token.lex, Category.CONST, Type(self.id_table, TypeCode.INTEGER, len(TypeCode.INTEGER)))
        elif token.code == Code.NUM and self.state == State.DIGIT_DOT_DIGIT_OTHER:
            symbol = Identifier(token.lex, Category.CONST, Type(self.id_table, TypeCode.FLOAT, len(TypeCode.FLOAT)))
        else:
            symbol = Identifier(token.lex)

        token.attr = len(self.id_table)
        self.id_table.append(symbol)

        return token

    def __iter__(self) -> Iterable[Token]:
        while self.pos < len(self.code):
            yield self.get_next_token(ignore_commentary=True)

    def get_tokens(self) -> list[Token]:
        token = None
        tokens: list[Token] = []

        while token is None or token.code != Code.EOF:
            token = self.get_next_token()
            tokens.append(token)

        return tokens

    def get_next_token(self, ignore_commentary: bool = False) -> Token:
        start = self.pos

        while self.pos < len(self.code):
            char: Char = Char.get_char_class(self.code[self.pos])
            self.state: State = self.STATE_TABLE[char][self.state]
            self.pos += 1

            if self.state.is_final():
                self.pos -= self.SHIFT_BACK_TABLE[self.state]
                token: Token = self.form_token(start)
                self.state = State.INITIAL

                if token.code == Code.SP:
                    start = self.pos
                    continue

                if token.code == Code.COM and ignore_commentary:
                    start = self.pos
                    continue

                return token

        self.state = State.EOF
        return self.form_token(start)


def find_in_id_table(
        id_table: list[Identifier],
        lex: str,
) -> Identifier | None:
    for identifier in id_table:
        if identifier.lex == lex:
            return identifier


if __name__ == '__main__':
    scanner = Scanner('--')
    print(scanner.get_tokens())
    print(list(Scanner.KEYWORDS.keys()))
