from enum import Enum


class State(Enum):
    INITIAL = 0
    SLASH = 1
    AMP = 2
    VERT_SLASH = 3
    LESS = 4
    LETTER = 5
    GREATER = 6
    DIGIT = 7
    DIGIT_DOT = 8
    DIGIT_DOT_DIGIT = 9
    SPACE = 10
    DASH = 11
    DASH_DASH = 12
    DASH_DASH_DASH = 13

    SEMICOLON = -1
    COLON = -2
    DOT = -3
    OP_PAR = -4
    CL_PAR = -5
    OP_CUR_BR = -6
    CL_CUR_BR = -7
    EXCL = -8
    EQUALS = -9
    PLUS = -10
    STAR = -11
    SLASH_OTHER = -12
    SLASH_EQUALS = -13
    AMP_AMP = -14
    VERT_SLASH_VERT_SLASH = -15
    LESS_OTHER = -16
    LESS_EQUALS = -17
    LESS_DASH = -18
    LETTER_OTHER = -19
    GREATER_OTHER = -20
    GREATER_EQUALS = -21
    DIGIT_OTHER = -22
    DIGIT_DOT_DIGIT_OTHER = -23
    SPACE_OTHER = -24
    DASH_OTHER = -25
    DASH_DASH_DASH_DASH = -26
    EOF = -27

    ERR_START = -28
    ERR_AMP = -29
    ERR_VERT_SLASH = -30
    ERR_NUMBER = -31
    ERR_COMMENT_NOT_CLOSED = -32

    def is_final(self):
        return self.value < 0
