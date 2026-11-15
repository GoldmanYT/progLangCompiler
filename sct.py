from typing import Any, Iterator
from xml.etree.ElementTree import fromstring as parse_xml

from attribute import Attribute
from operation import Operation
from category import Category
from tokens import Token
from lrtableelement import LRTableElement
from lrtableelemtype import LRTableElemType
from identifier import Identifier
from codes import Code
from scanner import find_in_id_table, Scanner
from type import Type
from typecode import TypeCode
from threeaddresscommand import ThreeAddressCommand


class Sct:
    """
    Syntactically controlled translation
    """

    GRAMMAR_PATH = 'content/LR_Table.xml'

    def __init__(
            self,
            scanner: Scanner,
            tokens: Iterator[Token],
    ):
        self.scanner = scanner
        self.tokens: Iterator = tokens
        self.id_table = scanner.id_table
        self.terminals: list[str] = []
        self.non_terminals: list[str] = []
        self.grammar = {}

        self.next_address: int = 0
        self.next_instruction: int = 0
        self.offset: int = 0
        self.temp_count: int = 0

        self.attr_stack: list[Any] = []
        self.offset_stack: list[int] = []
        self.id_table_stack: list[list[Identifier]] = []

        self.three_address_commands: list[ThreeAddressCommand] = []

        self.load_grammar()

    def generate(self, three_address_command: ThreeAddressCommand):
        self.three_address_commands.append(three_address_command)
        self.next_instruction += 1

    def get_new_temp(self, type_: Type) -> Identifier:
        self.temp_count += 1
        identifier: Identifier = Identifier(f'${self.temp_count}')
        self.add_type(identifier, Category.VAR_NAME, type_)
        return identifier

    def back_patch(
            self,
            commands: list[int],
            result: int,
    ):
        for i in commands:
            self.three_address_commands[i].result = result

    @staticmethod
    def set_error_message(token, expected):
        token.lex = '{pos}: Встречено "{lex}", ожидалось: {expected}'
        token.kwargs = {'expected': expected}

    def get_variable_list(self) -> list[Identifier]:
        stack: list[Iterator[Identifier]] = [iter(self.id_table)]
        base_address: list[int] = [0]
        result: list[Identifier] = []
        prefix: list[str] = []

        while stack:
            id_table: Iterator[Identifier] = stack.pop()
            try:
                identifier: Identifier = next(id_table)
                stack.append(id_table)

                if identifier.type.type_code == TypeCode.STRUCT and identifier.category in (
                        Category.VAR_NAME, Category.FIELD_NAME):
                    prefix.append(identifier.lex)
                    stack.append(iter(identifier.type.fields_id_table))

                    base_address.append(base_address[-1] + identifier.memory_address)

                elif identifier.category == Category.VAR_NAME:
                    result.append(Identifier(
                        '.'.join(prefix + [identifier.lex]), Category.VAR_NAME, identifier.type,
                        identifier.memory_address
                    ))

                elif identifier.category == Category.FIELD_NAME:
                    result.append(Identifier(
                        '.'.join(prefix + [identifier.lex]), Category.VAR_NAME, identifier.type,
                        base_address[-1] + identifier.memory_address
                    ))

            except StopIteration:
                if prefix:
                    prefix.pop()
                base_address.pop()

        return result

    def add_type(
            self,
            identifier: Identifier,
            category: Category,
            type_: Type,
    ):

        identifier.category = category
        identifier.type = type_

        if category == Category.VAR_NAME:
            while self.next_address % type_.width != 0:
                self.next_address += 1
                self.offset += 1
            identifier.memory_address = self.next_address
            self.next_address += type_.width
            self.offset += type_.width

        elif category == Category.FIELD_NAME:
            while self.offset % type_.width != 0:
                self.offset += 1
            identifier.memory_address = self.offset
            self.offset += type_.width

    def check_redeclaration(
            self,
            token: Token,
    ) -> None | Token:

        identifier: Identifier = find_in_id_table(self.id_table, token.lex)

        if identifier.category != Category.NO_CAT:
            token.lex = '{pos}: ' f'Переобъявление идентификатора: {identifier.lex}'
            return token

        self.attr_stack.append(identifier)

    def declare_type(
            self,
            _token: Token,
    ) -> None | Token:

        type_: Type = self.attr_stack.pop()
        identifier: Identifier = self.attr_stack.pop()

        self.add_type(identifier, Category.TYPE_NAME, type_)
        return

    def check_type(
            self,
            token: Token,
    ) -> None | Token:

        identifier: Identifier = find_in_id_table(self.id_table, token.lex)

        if identifier.category == Category.NO_CAT:
            token.lex = '{pos}: ' f'Идентификатор не объявлен: {identifier.lex}'
            return token

        if identifier.category != Category.TYPE_NAME:
            token.lex = '{pos}: ' f'Идентификатор не является именем типа: {identifier.lex}'
            return token

        self.attr_stack.append(identifier.type)

    def create_id_table(
            self,
            _token: Token,
    ) -> None | Token:

        self.scanner.id_table = self.id_table = self.scanner.get_new_id_table(self.id_table)
        self.id_table_stack.append(self.id_table)
        self.offset_stack.append(self.offset)
        self.offset = 0

        return

    def create_structure_type(
            self,
            _token: Token,
    ) -> None | Token:

        id_table = self.id_table_stack.pop()
        self.scanner.id_table = self.id_table = self.id_table_stack[-1]
        type_ = Type(self.id_table, TypeCode.STRUCT, self.offset, id_table)
        self.attr_stack.append(type_)
        self.offset = self.offset_stack.pop()

        return

    def add_type_to_field(
            self,
            _token: Token,
    ) -> None | Token:

        type_: Type = self.attr_stack.pop()
        identifier: Identifier = self.attr_stack.pop()

        self.add_type(identifier, Category.FIELD_NAME, type_)
        return

    def add_type_to_var(
            self,
            _token: Token,
    ) -> None | Token:

        type_: Type = self.attr_stack.pop()
        identifier: Identifier = self.attr_stack.pop()

        self.add_type(identifier, Category.VAR_NAME, type_)
        return

    def back_patch_operator_section(
            self,
            _token: Token,
    ) -> None | Token:

        operator_next_list: list[int] = self.attr_stack.pop()

        self.back_patch(operator_next_list, self.next_instruction)

        return

    def push_operator_list_next_instr(
            self,
            _token: Token,
    ) -> None | Token:

        self.attr_stack.append(self.next_instruction)

        return

    def back_patch_operator_next_list(
            self,
            _token: Token,
    ) -> None | Token:

        operator_next_list: list[int] = self.attr_stack.pop()
        next_instruction: int = self.attr_stack.pop()
        next_list: list[int] = self.attr_stack.pop()

        self.back_patch(next_list, next_instruction)

        self.attr_stack.append(operator_next_list)

        return

    def check_var_type_not_struct(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # false_list
        self.attr_stack.pop()  # true_list
        var_id: Identifier = self.attr_stack.pop()
        var_type: Type = self.attr_stack.pop()

        if var_type.type_code == TypeCode.STRUCT:
            token.lex = '{pos}: ' f'Присваивание не для базового типа: {var_id.lex}'
            return token

        self.attr_stack.append(var_type)
        self.attr_stack.append(var_id)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

    def generate_assign(
            self,
            token: Token,
    ) -> None | Token:

        expression_false_list: list[int] = self.attr_stack.pop()
        expression_true_list: list[int] = self.attr_stack.pop()
        expression_id: Identifier = self.attr_stack.pop()
        expression_type: Type = self.attr_stack.pop()
        self.attr_stack.pop()  # var_false_list
        self.attr_stack.pop()  # var_true_list
        var_id: Identifier = self.attr_stack.pop()
        var_type: Type = self.attr_stack.pop()

        if var_type != expression_type:
            token.lex = '{pos}: ' \
                        f'Типы переменной и выражения в операторе присваивания не совпадают ' \
                        f'({var_type.type_code.value} и {expression_type.type_code.value})'
            return token

        if var_type.type_code == TypeCode.BOOLEAN:
            self.back_patch(expression_true_list, self.next_instruction)
            self.back_patch(expression_false_list, self.next_instruction + 2)
            self.generate(ThreeAddressCommand(Operation(Code.ASS), var_id, True))
            self.generate(ThreeAddressCommand(Operation(Code.GOTO), self.next_instruction + 2))
            self.generate(ThreeAddressCommand(Operation(Code.ASS), var_id, False))
        else:
            self.generate(ThreeAddressCommand(Operation(Code.ASS), var_id, expression_id))

        self.attr_stack.append([])  # next_list

    def check_var_id(
            self,
            token: Token,
    ) -> None | Token:

        identifier: Identifier = find_in_id_table(self.id_table, token.lex)

        if identifier.category == Category.NO_CAT:
            token.lex = '{pos}: ' f'Идентификатор не объявлен: {identifier.lex}'
            return token

        if identifier.category != Category.VAR_NAME:
            token.lex = '{pos}: ' f'Идентификатор не является именем переменной: {identifier.lex}'
            return token

        if identifier.type.type_code == TypeCode.STRUCT:
            self.scanner.id_table = self.id_table = identifier.type.fields_id_table
            self.id_table_stack.append(identifier.type.fields_id_table)

        self.attr_stack.append(identifier.type)
        self.attr_stack.append(identifier)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

    def check_field_id(
            self,
            token: Token,
    ) -> None | Token:

        identifier: Identifier = find_in_id_table(self.id_table, token.lex)

        if identifier.category != Category.FIELD_NAME:
            token.lex = '{pos}: ' f'Идентификатор не является именем поля: {identifier.lex}'
            return token

        self.id_table_stack.pop()
        self.scanner.id_table = self.id_table = self.id_table_stack[-1]

        self.attr_stack.pop()  # false_list
        self.attr_stack.pop()  # true_list
        self.attr_stack.pop()  # id
        self.attr_stack.pop()  # type

        if identifier.type.type_code == TypeCode.STRUCT:
            self.scanner.id_table = self.id_table = identifier.type.fields_id_table
            self.id_table_stack.append(identifier.type.fields_id_table)

        self.attr_stack.append(identifier.type)
        self.attr_stack.append(identifier)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

        return

    def push_while_true_list_instr(
            self,
            _token: Token,
    ) -> None | Token:

        self.attr_stack.append(self.next_instruction)

        return

    def check_expression_type(
            self,
            token: Token,
    ) -> None | Token:

        expression_false_list: list[int] = self.attr_stack.pop()
        expression_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        expression_type: Type = self.attr_stack.pop()
        address: int = self.attr_stack.pop()

        if expression_type.type_code != TypeCode.BOOLEAN:
            token.lex = '{pos}: ' f'Операция отношения над нечисловым типом: {expression_type.type_code.value}'
            return token

        self.attr_stack.append(address)
        self.attr_stack.append(expression_type)
        self.attr_stack.append(None)  # id
        self.attr_stack.append(expression_true_list)
        self.attr_stack.append(expression_false_list)
        self.attr_stack.append(self.next_instruction)

    def generate_while(
            self,
            _token: Token,
    ) -> None | Token:

        operator_list_next_list: list[int] = self.attr_stack.pop()
        address2: int = self.attr_stack.pop()
        expression_false_list: list[int] = self.attr_stack.pop()
        expression_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        self.attr_stack.pop()  # type
        address1: int = self.attr_stack.pop()

        self.back_patch(operator_list_next_list, address1)
        self.back_patch(expression_true_list, address2)
        self.generate(ThreeAddressCommand(Operation(Code.GOTO), address1))

        self.attr_stack.append(expression_false_list)  # next_list

        return

    def check_rel_operand_type(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # false_list
        self.attr_stack.pop()  # true_list
        expression_id: Identifier = self.attr_stack.pop()
        expression_type: Type = self.attr_stack.pop()

        if expression_type.type_code not in (TypeCode.INTEGER, TypeCode.FLOAT):
            token.lex = '{pos}: ' f'Операция отношения над нечисловым типом: {expression_type.type_code.value}'
            return token

        self.attr_stack.append(expression_type)
        self.attr_stack.append(expression_id)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

    def push_rel_attribute(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.append(token.attr)

        return

    def generate_rel(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # expression1_false_list
        self.attr_stack.pop()  # expression1_true_list
        expression1_id: Identifier = self.attr_stack.pop()
        expression1_type: Type = self.attr_stack.pop()
        attribute: Attribute = self.attr_stack.pop()
        self.attr_stack.pop()  # expression_false_list
        self.attr_stack.pop()  # expression_true_list
        expression_id: Identifier = self.attr_stack.pop()
        self.attr_stack.pop()

        if expression1_type.type_code not in (TypeCode.INTEGER, TypeCode.FLOAT):
            token.lex = '{pos}: ' f'Операция отношения над нечисловым типом: {expression1_type.type_code.value}'
            return token

        self.attr_stack.append(Type([], TypeCode.BOOLEAN, len(TypeCode.BOOLEAN)))
        self.attr_stack.append(None)  # id
        self.attr_stack.append([self.next_instruction])  # true_list
        self.attr_stack.append([self.next_instruction + 1])  # false_list
        self.generate(ThreeAddressCommand(Operation(Code.IF, attribute), -1, expression_id, expression1_id))
        self.generate(ThreeAddressCommand(Operation(Code.GOTO), -1))

    def check_add_operand_type(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # false_list
        self.attr_stack.pop()  # true_list
        expression_id: Identifier = self.attr_stack.pop()
        expression_type: Type = self.attr_stack.pop()

        if expression_type.type_code not in (TypeCode.INTEGER, TypeCode.FLOAT):
            token.lex = '{pos}: ' f'Аддитивная операция над нечисловым типом: {expression_type.type_code.value}'
            return token

        self.attr_stack.append(expression_type)
        self.attr_stack.append(expression_id)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

    def push_add_attribute(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.append(token.attr)

        return

    def generate_add(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # term_false_list
        self.attr_stack.pop()  # term_true_list
        term_id: Identifier = self.attr_stack.pop()
        term_type: Type = self.attr_stack.pop()
        attribute: Attribute = self.attr_stack.pop()
        self.attr_stack.pop()  # expression_false_list
        self.attr_stack.pop()  # expression_true_list
        expression_id: Identifier = self.attr_stack.pop()
        expression_type: Type = self.attr_stack.pop()

        if term_type.type_code not in (TypeCode.INTEGER, TypeCode.FLOAT):
            token.lex = '{pos}: ' f'Аддитивная операция над нечисловым типом: {term_type.type_code.value}'
            return token

        if expression_type != term_type:
            token.lex = '{pos}: ' \
                        f'Типы аддитивной операции не совпадают ' \
                        f'({expression_type.type_code.value} и {term_type.type_code.value})'
            return token

        new_expression: Identifier = self.get_new_temp(term_type)
        self.generate(ThreeAddressCommand(Operation(Code.ADD, attribute), new_expression, expression_id, term_id))
        self.attr_stack.append(expression_type)
        self.attr_stack.append(new_expression)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

    def check_or_operand_type(
            self,
            token: Token,
    ) -> None | Token:

        expression_false_list: list[int] = self.attr_stack.pop()
        expression_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        expression_type: Type = self.attr_stack.pop()

        if expression_type.type_code != TypeCode.BOOLEAN:
            token.lex = '{pos}: ' f'Тип операнда логического ИЛИ не является логическим: {expression_type.type_code.value}'
            return token

        self.attr_stack.append(expression_type)
        self.attr_stack.append(None)  # id
        self.attr_stack.append(expression_true_list)
        self.attr_stack.append(expression_false_list)
        self.attr_stack.append(self.next_instruction)

    def generate_or(
            self,
            token: Token,
    ) -> None | Token:

        term_false_list: list[int] = self.attr_stack.pop()
        term_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        term_type: Type = self.attr_stack.pop()
        address: int = self.attr_stack.pop()
        expression_false_list: list[int] = self.attr_stack.pop()
        expression_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        self.attr_stack.pop()  # expression_type

        if term_type.type_code != TypeCode.BOOLEAN:
            token.lex = '{pos}: ' f'Тип операнда логического ИЛИ не является логическим: {term_type.type_code.value}'
            return token

        self.back_patch(expression_false_list, address)

        self.attr_stack.append(term_type)
        self.attr_stack.append(None)  # id
        self.attr_stack.append(expression_true_list + term_true_list)
        self.attr_stack.append(term_false_list)

    def check_mult_operand_type(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # false_list
        self.attr_stack.pop()  # true_list
        term_id: Identifier = self.attr_stack.pop()
        term_type: Type = self.attr_stack.pop()

        if term_type.type_code not in (TypeCode.INTEGER, TypeCode.FLOAT):
            token.lex = '{pos}: ' f'Мультипликативная операция над нечисловым типом: {term_type.type_code.value}'
            return token

        self.attr_stack.append(term_type)
        self.attr_stack.append(term_id)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

    def push_mult_attribute(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.append(token.attr)

        return

    def generate_mult(
            self,
            token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # factor_false_list
        self.attr_stack.pop()  # factor_true_list
        factor_id: Identifier = self.attr_stack.pop()
        factor_type: Type = self.attr_stack.pop()
        attribute: Attribute = self.attr_stack.pop()
        self.attr_stack.pop()  # term_false_list
        self.attr_stack.pop()  # term_true_list
        term_id: Identifier = self.attr_stack.pop()
        term_type: Type = self.attr_stack.pop()

        if factor_type.type_code not in (TypeCode.INTEGER, TypeCode.FLOAT):
            token.lex = '{pos}: ' f'Мультипликативная операция над нечисловым типом: {factor_type.type_code.value}'
            return token

        if term_type != factor_type:
            token.lex = '{pos}: ' \
                        f'Типы мультипликативной операции не совпадают ' \
                        f'({term_type.type_code.value} и {factor_type.type_code.value})'
            return token

        new_term: Identifier = self.get_new_temp(factor_type)
        self.generate(ThreeAddressCommand(Operation(Code.MULT, attribute), new_term, term_id, factor_id))
        self.attr_stack.append(term_type)
        self.attr_stack.append(new_term)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

    def check_and_operand_type(
            self,
            token: Token,
    ) -> None | Token:

        term_false_list: list[int] = self.attr_stack.pop()
        term_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        term_type: Type = self.attr_stack.pop()

        if term_type.type_code != TypeCode.BOOLEAN:
            token.lex = '{pos}: ' f'Тип операнда логического И не является логическим: {term_type.type_code.value}'
            return token

        self.attr_stack.append(term_type)
        self.attr_stack.append(None)  # id
        self.attr_stack.append(term_true_list)
        self.attr_stack.append(term_false_list)
        self.attr_stack.append(self.next_instruction)

    def generate_and(
            self,
            token: Token,
    ) -> None | Token:

        factor_false_list: list[int] = self.attr_stack.pop()
        factor_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        factor_type: Type = self.attr_stack.pop()
        address: int = self.attr_stack.pop()
        term_false_list: list[int] = self.attr_stack.pop()
        term_true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        self.attr_stack.pop()  # term_type

        if factor_type.type_code != TypeCode.BOOLEAN:
            token.lex = '{pos}: ' f'Тип операнда логического И не является логическим: {factor_type.type_code.value}'
            return token

        self.back_patch(term_true_list, address)

        self.attr_stack.append(factor_type)
        self.attr_stack.append(None)  # id
        self.attr_stack.append(factor_true_list)
        self.attr_stack.append(term_false_list + factor_false_list)

    def generate_bool_var_commands(
            self,
            _token: Token,
    ) -> None | Token:

        self.attr_stack.pop()  # factor_false_list
        self.attr_stack.pop()  # factor_true_list
        identifier: Identifier = self.attr_stack.pop()
        identifier_type: Type = self.attr_stack.pop()

        if identifier_type.type_code == TypeCode.BOOLEAN:
            self.attr_stack.append(identifier_type)
            self.attr_stack.append(identifier)
            self.attr_stack.append([self.next_instruction])  # true_list
            self.attr_stack.append([self.next_instruction + 1])  # false_list
            self.generate(ThreeAddressCommand(Operation(Code.IF, Attribute.OP_EQ), -1, identifier, True))
            self.generate(ThreeAddressCommand(Operation(Code.GOTO), -1))
        else:
            self.attr_stack.append(identifier_type)
            self.attr_stack.append(identifier)
            self.attr_stack.append([])  # true_list
            self.attr_stack.append([])  # false_list

        return

    def check_not_operand_type(
            self,
            token: Token,
    ) -> None | Token:

        false_list: list[int] = self.attr_stack.pop()
        true_list: list[int] = self.attr_stack.pop()
        self.attr_stack.pop()  # id
        type_: Type = self.attr_stack.pop()

        if type_.type_code != TypeCode.BOOLEAN:
            token.lex = '{pos}: ' f'Тип операнда логического НЕ не является логическим: {type_.type_code.value}'
            return token

        self.attr_stack.append(type_)
        self.attr_stack.append(None)  # id
        self.attr_stack.append(false_list)  # true_list
        self.attr_stack.append(true_list)  # false_list

    def push_number_attributes(
            self,
            token: Token,
    ) -> None | Token:

        identifier: Identifier = find_in_id_table(self.id_table, token.lex)

        self.attr_stack.append(identifier.type)
        self.attr_stack.append(identifier)
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([])  # false_list

        return

    def push_true_attributes(
            self,
            _token: Token,
    ) -> None | Token:

        self.attr_stack.append(Type([], TypeCode.BOOLEAN, len(TypeCode.BOOLEAN)))
        self.attr_stack.append(None)  # id
        self.attr_stack.append([self.next_instruction])  # true_list
        self.attr_stack.append([])  # false_list

        self.generate(ThreeAddressCommand(Operation(Code.GOTO), -1))

        return

    def push_false_attributes(
            self,
            _token: Token,
    ) -> None | Token:

        self.attr_stack.append(Type([], TypeCode.BOOLEAN, len(TypeCode.BOOLEAN)))
        self.attr_stack.append(None)  # id
        self.attr_stack.append([])  # true_list
        self.attr_stack.append([self.next_instruction])  # false_list

        self.generate(ThreeAddressCommand(Operation(Code.GOTO), -1))

        return

    def scan(self) -> None | Token:
        state: int = 1

        state_stack: list[int] = [state]
        self.attr_stack = []
        self.offset_stack = []
        self.id_table_stack = [self.id_table]

        token: Token = next(self.tokens)
        prev_token: Token = token
        lexeme: str = token.code.value
        is_terminal: bool = True

        while state != 0:
            if lexeme not in self.terminals + self.non_terminals:
                return token

            lr_table_elem: LRTableElement = self.grammar[state][lexeme]

            expected = ' или '.join(
                f'"{Code.get_lex_info(Code(lexeme))}"' for lexeme in self.grammar[state]
                if self.grammar[state][lexeme].elem_type != LRTableElemType.ERROR
                and lexeme in self.terminals
            )

            elem_param: int | None = lr_table_elem.elem_param

            if lr_table_elem.elem_type == LRTableElemType.SHIFT:
                state = elem_param
                state_stack.append(state)

                if is_terminal:
                    prev_token = token
                    token: Token = next(self.tokens)

                lexeme = token.code.value
                is_terminal = True

            elif lr_table_elem.elem_type == LRTableElemType.FOLD:
                pop_count: int = elem_param
                lexeme = lr_table_elem.left
                is_terminal = False

                if len(state_stack) <= pop_count:
                    self.set_error_message(token, expected)
                    return token

                state_stack = state_stack[:-pop_count if pop_count > 0 else None]
                state = state_stack[-1]

                try:
                    action = self.__getattribute__(lr_table_elem.action)
                    error_token: Token | None = action(prev_token)
                    if error_token is not None:
                        return error_token
                except AttributeError:
                    pass

            elif lr_table_elem.elem_type == LRTableElemType.STOP:
                state = 0

            elif lr_table_elem.elem_type == LRTableElemType.ERROR:
                self.set_error_message(token, expected)
                return token

    def load_grammar(self):
        xml_content: str = ''
        try:
            with open(self.GRAMMAR_PATH, 'r', encoding='utf-8') as file:
                xml_content = file.read()
        except FileNotFoundError:
            pass

        self.grammar = {}
        root = parse_xml(xml_content)

        columns = root.find('Columns')

        terminals = columns.find('Terms')
        for column in terminals.findall('Column'):
            lexeme = column.get('Lexeme')
            self.terminals.append(lexeme)

        non_terminals = columns.find('Neterms')
        for column in non_terminals.findall('Column'):
            lexeme = column.get('Lexeme')
            self.non_terminals.append(lexeme)

        col_num_to_lexeme = {}
        for column in root.iter('Column'):
            col_num = column.get('ColNum')
            lexeme = column.get('Lexeme')
            col_num_to_lexeme[col_num] = lexeme

        for row in root.findall('Row'):
            state: int = int(row.get('NSost'))
            self.grammar[state] = {}
            for elem in row:
                col_num = elem.get('ColNum')
                lexeme = col_num_to_lexeme[col_num]

                elem_type = LRTableElemType(elem.get('ElType'))

                if elem_type in (LRTableElemType.SHIFT, LRTableElemType.FOLD):
                    elem_param: int | None = int(elem.get('ElPar'))
                else:
                    elem_param = None

                if elem_type == LRTableElemType.FOLD:
                    left: str | None = elem.get('Left')
                else:
                    left = None

                action: str = elem.get('Act')

                self.grammar[state][lexeme] = LRTableElement(elem_type, elem_param, left, action)
