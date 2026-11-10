from category import Category
from type import Type
from typecode import TypeCode

from dataclasses import dataclass


@dataclass
class Identifier:
    lex: str
    category: Category = Category.NO_CAT
    type: Type = Type(TypeCode.NO_TYPE, len(TypeCode.NO_TYPE))
    address: int = -1
