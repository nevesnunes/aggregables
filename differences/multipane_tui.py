#!/usr/bin/env python3

from prompt_toolkit import Application, ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

kb = KeyBindings()


@kb.add("c-c")
@kb.add("q")
def exit_(event):
    event.app.exit()


@kb.add("j")
def down_(event):
    if event.current_buffer.name == "entries":
        event.current_buffer.cursor_down()


@kb.add("k")
def up_(event):
    if event.current_buffer.name == "entries":
        event.current_buffer.cursor_up()


@kb.add("h")
def left_(event):
    if event.current_buffer.name == "entries":
        event.current_buffer.cursor_left()


@kb.add("l")
def right_(event):
    if event.current_buffer.name == "entries":
        event.current_buffer.cursor_right()


class MultiPane:
    def __init__(self, entries, callback):
        self.entries = entries
        self.max_entry_width = min(max(map(lambda x: len(x), entries.split("\n"))), 48)
        self.callback = callback

        self.current_lineno = 1
        self.entries_control = BufferControl(
            buffer=Buffer(
                document=Document(self.entries, 0),
                name="entries",
                on_cursor_position_changed=self.update,
                read_only=True,
            )
        )
        self.text_control = FormattedTextControl(
            text=ANSI(self.callback(self.current_lineno))
        )
        self.root_container = VSplit(
            [
                Window(
                    content=self.entries_control,
                    width=self.max_entry_width,
                    wrap_lines=True,
                ),
                Window(width=3, char=" | "),
                Window(content=self.text_control),
            ]
        )
        self.layout = Layout(self.root_container)

        self.app = Application(full_screen=True, key_bindings=kb, layout=self.layout)

    def get_lineno(self, text, pos):
        lineno = 1
        for i, c in enumerate(text):
            if c == "\n" and i != pos:
                lineno += 1
            if i == pos:
                break
            i += 1
        return lineno

    def update(self, buffer):
        new_lineno = self.get_lineno(self.entries, buffer.cursor_position)
        if self.current_lineno != new_lineno:
            self.current_lineno = new_lineno
            self.text_control.text = ANSI(self.callback(self.current_lineno))
            # app.invalidate()

    def run(self):
        self.app.run()
