from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Iterator

from scanner import Scanner
from codes import Code
from tokens import Token
from sct import Sct


class UiLayoutConstructor:
    def __init__(self, ratios, orientation='v', padding=0.01):
        if orientation not in ('v', 'h'):
            raise ValueError(f'Incorrect value of parameter `type`: {orientation}. Supports only "v" and "h"')

        if isinstance(ratios, int):
            ratios = [1] * ratios

        # Normalize the ratios
        ratios = [ratio / sum(ratios) for ratio in ratios]

        self.layouts = [dict() for _ in range(len(ratios))]

        padding_count_x = len(ratios) + 1 if orientation == 'h' else 2
        padding_count_y = len(ratios) + 1 if orientation == 'w' else 2
        sum_padding_x = padding
        sum_padding_y = padding
        for index, ratio in enumerate(ratios):
            ratio_x = ratio if orientation == 'h' else 1.0
            ratio_y = ratio if orientation == 'v' else 1.0
            relwidth = self.layouts[index]['relwidth'] = (1.0 - padding * padding_count_x) * ratio_x
            self.layouts[index]['relx'] = sum_padding_x
            relheight = self.layouts[index]['relheight'] = (1.0 - padding * padding_count_y) * ratio_y
            self.layouts[index]['rely'] = sum_padding_y
            if orientation == 'h':
                sum_padding_x += relwidth + padding
            elif orientation == 'v':
                sum_padding_y += relheight + padding

    def __getitem__(self, index) -> dict:
        return self.layouts[index]


class Window:
    def __init__(self):
        rel_elem_full = UiLayoutConstructor(1)[0]
        rel_elem_half_left = UiLayoutConstructor(2, 'h')[0]
        rel_elem_half_right = UiLayoutConstructor(2, 'h')[1]
        rel_elem_95_5_v = UiLayoutConstructor((95, 5), 'v')
        rel_elem_80_20_v = UiLayoutConstructor((80, 20), 'v')
        rel_elem_10_90_v = UiLayoutConstructor((10, 90), 'v')

        self.root = Tk()
        self.root.geometry('1200x800')

        left_frame = Frame(self.root)

        top_left_frame = Labelframe(left_frame, text='Исходный код программы')
        save_load_button_frame = Frame(top_left_frame)
        load_button = Button(save_load_button_frame, text='Открыть', command=self.load_button_action)
        save_button = Button(save_load_button_frame, text='Сохранить', command=self.save_button_action)
        self.program_code_text = ScrolledText(top_left_frame, font=('Consolas', 14))

        bottom_left_frame = Labelframe(left_frame, text='Список найденных ошибок')
        self.errors_text = ScrolledText(bottom_left_frame, font=('Cascadia Mono', 14), foreground='#dd0000')

        right_tab_widget = Notebook(self.root)

        scaner_frame = Labelframe(right_tab_widget, text='Сформированные токены')
        self.scanner_output_text = ScrolledText(scaner_frame, font=('Consolas', 14))
        start_scanner_button = Button(scaner_frame, text='Запуск', command=self.start_scanner_button_action)

        sgt_frame = Frame(right_tab_widget)  # СУТ
        sgt_top_frame = Frame(sgt_frame)

        three_address_commands_frame = Labelframe(sgt_top_frame, text='Трёхадресные команды')
        memory_allocation_frame = Labelframe(sgt_top_frame, text='Распределение памяти')

        self.three_address_commands_text = ScrolledText(three_address_commands_frame, font=('Consolas', 12))
        self.memory_allocation_text = ScrolledText(memory_allocation_frame, font=('Consolas', 12))
        start_sgt_button = Button(sgt_frame, text='Запуск', command=self.start_sgt_button_action)

        scaner_frame.place(**rel_elem_full)
        self.scanner_output_text.place(**rel_elem_95_5_v[0])
        start_scanner_button.place(**rel_elem_95_5_v[1])

        sgt_frame.place(**rel_elem_full)
        sgt_top_frame.place(**rel_elem_95_5_v[0])

        three_address_commands_frame.place(**rel_elem_half_left)
        self.three_address_commands_text.place(**rel_elem_full)

        memory_allocation_frame.place(**rel_elem_half_right)
        self.memory_allocation_text.place(**rel_elem_full)

        start_sgt_button.place(**rel_elem_95_5_v[1])

        right_tab_widget.add(scaner_frame, text='Сканер')
        right_tab_widget.add(sgt_frame, text='СУТ')

        left_frame.place(**rel_elem_half_left)
        top_left_frame.place(**rel_elem_80_20_v[0])
        save_load_button_frame.place(**rel_elem_10_90_v[0])
        load_button.place(**rel_elem_half_left)
        save_button.place(**rel_elem_half_right)
        self.program_code_text.place(**rel_elem_10_90_v[1])

        bottom_left_frame.place(**rel_elem_80_20_v[1])
        self.errors_text.place(**rel_elem_full)

        right_tab_widget.place(**rel_elem_half_right)

        self.indexes = []
        self.current_file_name = 'new'
        self.load_program_code('')

        self.root.mainloop()

    def load_button_action(self):
        filename: str = askopenfilename(
            initialdir='./program codes',
            filetypes=(('Текстовые документы', '*.txt'),),
        )

        if filename != '':
            with open(filename, encoding='utf-8') as file:
                code = file.read()
                self.current_file_name = file.name
                self.load_program_code(code)

    def save_button_action(self):
        filename: str = asksaveasfilename(
            initialdir='./program codes',
            initialfile=self.current_file_name,
            filetypes=(('Текстовые документы', '*.txt'),),
            defaultextension='.txt'
        )

        if filename != '':
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.program_code_text.get('1.0', END))

    def get_tk_index(self, index):
        l = 0
        r = len(self.indexes)
        while r - l > 1:
            m = (r + l) // 2
            if self.indexes[m] >= index:
                r = m
            else:
                l = m
        return f'{l + 1}.{index - self.indexes[l] - 1}'

    def load_program_code(self, code):
        self.program_code_text.delete('1.0', END)
        self.program_code_text.insert(END, code)

        self.program_code_text.tag_configure('keyword', foreground='#ff7700')
        self.program_code_text.tag_configure('comment', foreground='#dd0000')
        self.program_code_text.tag_configure('const', foreground='#0000ff')
        self.program_code_text.tag_configure('error', background='#ff7777')

        self.program_code_text.bind("<KeyRelease>", self.start_sgt_button_action)
        self.update_syntax_highlight()

    def update_syntax_highlight(self, *_):
        code_to_tag = {
            Code.PROG: 'keyword',
            Code.USING: 'keyword',
            Code.CLASS: 'keyword',
            Code.VAR: 'keyword',
            Code.WHILE: 'keyword',
            Code.TRUE: 'keyword',
            Code.FALSE: 'keyword',
            Code.FULLNAME: 'keyword',
            Code.NUM: 'const',
            Code.COM: 'comment',
            Code.ERR: 'error',
        }
        for tag in code_to_tag.values():
            self.program_code_text.tag_delete(tag)

        self.program_code_text.tag_configure('keyword', foreground='#ff7700')
        self.program_code_text.tag_configure('comment', foreground='#dd0000')
        self.program_code_text.tag_configure('const', foreground='#0000ff')
        self.program_code_text.tag_configure('error', background='#ff7777')
        self.program_code_text.tag_configure('type', background='#900090')

        code: str = self.program_code_text.get('1.0', END)
        scanner: Scanner = Scanner(code)
        tokens: list[Token] = scanner.get_tokens()
        self.indexes: list[int] = [-1] + [i for i in range(len(code)) if code[i] == '\n']

        for token in tokens:
            tag = code_to_tag.get(token.code)
            if tag is not None:
                index1 = self.get_tk_index(token.start)
                index2 = self.get_tk_index(token.end)
                self.program_code_text.tag_add(tag, index1, index2)

        scanner.restart()
        sct: Sct = Sct(scanner, iter(scanner))
        error_token: Token = sct.scan()

        if error_token is not None:
            index1 = self.get_tk_index(error_token.start)
            index2 = self.get_tk_index(error_token.end)
            self.program_code_text.tag_add('error', index1, index2)

    def start_scanner_button_action(self):
        program_code: str = self.program_code_text.get('1.0', END)
        scanner: Scanner = Scanner(program_code)
        tokens: list[Token] = scanner.get_tokens()

        self.scanner_output_text.delete('1.0', END)
        self.scanner_output_text.insert(END, '\n'.join(str(token) for token in tokens))

        has_errors: bool = False
        self.errors_text.delete('1.0', END)
        for token in tokens:
            if token.code == Code.ERR:
                index = self.get_tk_index(token.start)
                self.errors_text.insert(END, f'{index}: {token.lex}\n')
                has_errors = True
        if not has_errors:
            self.errors_text.insert(END, 'Лексический анализ успешно завершен')

    def start_sgt_button_action(self, *_):
        program_code: str = self.program_code_text.get('1.0', END)
        scanner: Scanner = Scanner(program_code)
        tokens: Iterator[Token] = iter(scanner)
        sct = Sct(scanner, tokens)
        error_token = sct.scan()

        self.errors_text.delete('1.0', END)
        self.three_address_commands_text.delete('1.0', END)
        self.memory_allocation_text.delete('1.0', END)

        if error_token is not None:
            index1 = self.get_tk_index(error_token.start)
            index2 = self.get_tk_index(error_token.end)
            self.program_code_text.tag_add('error', index1, index2)
            lex: str = program_code[error_token.start:error_token.end]
            self.errors_text.insert(END, error_token.lex.format(pos=index1, lex=lex, **error_token.kwargs))
        else:
            self.errors_text.insert(END, 'СУ-трансляция успешно завершена')
            for command in sct.three_address_commands:
                self.three_address_commands_text.insert(END, str(command) + '\n')
            for var in sct.get_variable_list():
                self.memory_allocation_text.insert(END, var.get_memory_address() + '\n')

        self.update_syntax_highlight()


if __name__ == '__main__':
    Window()
