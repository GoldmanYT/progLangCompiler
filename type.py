from dataclasses import dataclass

from typecode import TypeCode


@dataclass
class Type:
    id_table: list['Identifier']
    type_code: TypeCode
    width: int
    fields_id_table: list['Identifier'] | None = None

    def __eq__(self, other) -> bool:
        return self.type_code == other.type_code
