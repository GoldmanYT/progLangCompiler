from enum import Enum


class TypeCode(Enum):
    NO_TYPE = 'no type'
    INTEGER = 'integer'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    STRUCT = 'struct'

    def __len__(self):
        return {
            self.NO_TYPE: 0,
            self.INTEGER: 4,
            self.FLOAT: 8,
            self.BOOLEAN: 1,
            self.STRUCT: 0,
        }[self]
