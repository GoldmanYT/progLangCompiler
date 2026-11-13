from category import Category
from type import Type
from typecode import TypeCode
# from typing import Self
from dataclasses import dataclass, field


@dataclass
class Identifier:
    lex: str
    category: Category = Category.NO_CAT
    type: Type = field(default_factory=lambda: Type([], TypeCode.NO_TYPE, len(TypeCode.NO_TYPE)))
    memory_address: int = -1

    def get_memory_address(self) -> str:
        return f'{self.memory_address:03}:\t{self.lex}\tWidth: {self.type.width}'

    def __str__(self) -> str:
        return self.lex
