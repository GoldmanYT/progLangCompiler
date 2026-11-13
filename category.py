from enum import Enum


class Category(Enum):
    NO_CAT = 'no category'
    CONST = 'const'
    TYPE_NAME = 'type name'
    VAR_NAME = 'var name'
    FIELD_NAME = 'field name'
