from typing import Any, Callable, Iterator
from xml.etree.ElementTree import fromstring as parse_xml

from category import Category
from tokens import Token
from lrtableelement import LRTableElement
from lrtableelemtype import LRTableElemType
from identifier import Identifier
from codes import Code
from scanner import find_in_id_table
from type import Type


class Sct:
    """
    Syntactically controlled translation
    """

    GRAMMAR_PATH = 'content/LR_Table.xml'

    def __init__(
            self,
            tokens: Iterator[Token],
            id_table: list[Identifier],
    ):
        self.tokens: Iterator = tokens
        self.id_table = id_table
        self.terminals: list[str] = []
        self.non_terminals: list[str] = []
        self.grammar = {}
        self.actions: dict[str, Callable[[list[Any], Token], None | Token]] = {
            'A1': self.action1,
            'A2': self.action2,
            'A3': self.action3,
            'A5': self.action5,
            'A10': self.action10,
        }
        self.next_address: int = 0
        self.next_instruction: int = 0
        self.load_grammar()

    @staticmethod
    def set_error_message(token, expected):
        token.lex = '{pos}: Встречено "{lex}", ожидалось: {expected}'
        token.kwargs = {'expected': expected}

    def get_variable_list(self) -> list[Identifier]:
        return [identifier for identifier in self.id_table if identifier.category == Category.VAR_NAME]

    def add_type(
            self,
            index: int,
            category: Category,
            type_: Type,
    ):
        identifier: Identifier = self.id_table[index]
        identifier.category = category
        identifier.type = type_

        if category == Category.VAR_NAME:
            while self.next_address % type_.width != 0:
                self.next_address += 1
            identifier.address = self.next_address
            self.next_address += type_.width

    def action1(
            self,
            stack: list[Any],
            token: Token,
    ) -> None | Token:

        i: int = find_in_id_table(self.id_table, token.lex)
        identifier: Identifier = self.id_table[i]

        if identifier.category != Category.NO_CAT:
            token.lex = '{pos}: ' f'Переобъявление идентификатора: {identifier.lex}'
            return token

        stack.append(i)

    def action2(
            self,
            stack: list[Any],
            _token: Token,
    ) -> None | Token:

        type_: Type = stack.pop()
        var_i: int = stack.pop()

        self.add_type(var_i, Category.TYPE_NAME, type_)
        return

    def action3(
            self,
            stack: list[Any],
            token: Token,
    ) -> None | Token:

        i: int = find_in_id_table(self.id_table, token.lex)
        identifier: Identifier = self.id_table[i]

        if identifier.category == Category.NO_CAT:
            token.lex = '{pos}: ' f'Идентификатор не объявлен: {identifier.lex}'
            return token

        if identifier.category != Category.TYPE_NAME:
            token.lex = '{pos}: ' f'Идентификатор не является именем типа: {identifier.lex}'
            return token

        stack.append(identifier.type)

    def action5(
            self,
            stack: list[Any],
            _token: Token,
    ) -> None | Token:

        # ИСПРАВИТЬ: Заглушка для структур
        i: int = find_in_id_table(self.id_table, 'integer')
        identifier: Identifier = self.id_table[i]

        stack.append(identifier.type)
        return

    def action10(
            self,
            stack: list[Any],
            _token: Token,
    ) -> None | Token:

        type_: Type = stack.pop()
        var_i: int = stack.pop()

        self.add_type(var_i, Category.VAR_NAME, type_)
        return

    def scan(self) -> None | Token:
        state: int = 1
        state_stack: list[int] = [state]
        attr_stack: list[Any] = []
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

                action = self.actions.get(lr_table_elem.action)

                if action is not None:
                    error_token: Token | None = action(attr_stack, prev_token)
                    if error_token is not None:
                        return error_token

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
