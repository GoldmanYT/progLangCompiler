from attribute import Attribute
from codes import Code


class Operation:
    POSSIBLE_OPERATIONS: dict[Code, list[Attribute | None]] = {
        Code.ASS: [None],
        Code.ADD: [Attribute.OP_ADD, Attribute.OP_SUB],
        Code.MULT: [Attribute.OP_MULT, Attribute.OP_DIV],
        Code.GOTO: [None],
        Code.IF: [Attribute.OP_LT, Attribute.OP_GT, Attribute.OP_LE, Attribute.OP_GE, Attribute.OP_EQ, Attribute.OP_NE],
    }

    def __init__(
            self,
            code: Code,
            attribute: Attribute = None
    ):
        if code not in self.POSSIBLE_OPERATIONS:
            raise ValueError(f'Unsupported operation code: {code}')

        if attribute not in self.POSSIBLE_OPERATIONS[code]:
            raise ValueError(f'Unsupported code attribute for {code}: {attribute}')

        self.code = code
        self.attribute = attribute

    def __str__(self):
        if self.code == Code.ASS:
            return '{result} := {arg1}'

        if self.code in (Code.ADD, Code.MULT):
            return '{result} := {arg1} ' f'{self.attribute.value}' ' {arg2}'

        if self.code == Code.GOTO:
            return 'goto {result:03}'

        if self.code == Code.IF:
            return f'{self.code.value}' ' {arg1} ' f'{self.attribute.value}' ' {arg2} goto {result:03}'

        raise NotImplementedError


if __name__ == '__main__':
    print(Operation(Code.ASS))
    print(Operation(Code.ADD, Attribute.OP_ADD))
    print(Operation(Code.ADD, Attribute.OP_SUB))
    print(Operation(Code.MULT, Attribute.OP_MULT))
    print(Operation(Code.MULT, Attribute.OP_DIV))
    print(Operation(Code.GOTO))
    print(Operation(Code.IF, Attribute.OP_EQ))
    print(Operation(Code.IF, Attribute.OP_LT))
