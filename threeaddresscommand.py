from identifier import Identifier
from operation import Operation
from codes import Code
from attribute import Attribute


class ThreeAddressCommand:
    def __init__(
            self,
            operation: Operation,
            result: int | Identifier,
            arg1: Identifier | None = None,
            arg2: Identifier | None | bool = None,
    ):
        self.operation = operation

        if operation.code in (Code.GOTO, Code.IF, Code.IF_FALSE):
            if not isinstance(result, int):
                raise ValueError(f'For operation `{operation}` result must be int')

            self.result = result
        else:
            if not isinstance(result, Identifier):
                raise ValueError(f'For operation `{operation}` result must be Identifier')

            self.result = result.lex

        if arg1 is not None:
            if not isinstance(arg1, Identifier):
                raise ValueError(f'arg1 must be Identifier or None')

            self.arg1 = arg1.lex
        else:
            self.arg1 = None

        if arg2 is True:
            self.arg2 = True
        elif arg2 is not None:
            if not isinstance(arg2, Identifier):
                raise ValueError(f'arg2 must be Identifier, True or None')

            self.arg2 = arg2.lex
        else:
            self.arg2 = None

    def __str__(self):
        return str(self.operation).format(result=self.result, arg1=self.arg1, arg2=self.arg2)


if __name__ == '__main__':
    x, y, z = [Identifier('x'), Identifier('y'), Identifier('z'), ]
    print(ThreeAddressCommand(Operation(Code.ASS), x, y))
    print(ThreeAddressCommand(Operation(Code.ADD, Attribute.OP_ADD), x, y, z))
    print(ThreeAddressCommand(Operation(Code.ADD, Attribute.OP_SUB), x, y, z))
    print(ThreeAddressCommand(Operation(Code.GOTO), 50))
    print(ThreeAddressCommand(Operation(Code.IF, Attribute.OP_LE), 50, x, y))
    print(ThreeAddressCommand(Operation(Code.IF_FALSE, Attribute.OP_NE), 100, z, y))
    print(ThreeAddressCommand(Operation(Code.IF, Attribute.OP_EQ), 100, x, True))
