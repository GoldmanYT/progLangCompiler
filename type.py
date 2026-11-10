from dataclasses import dataclass

from typecode import TypeCode


@dataclass
class Type:
    type_code: TypeCode
    width: int
