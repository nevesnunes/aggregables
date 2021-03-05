#!/usr/bin/env python3

# TODO:
# - Input prompt for search callback
#     - [python\-prompt\-toolkit/calculator\.py at master · prompt\-toolkit/python\-prompt\-toolkit · GitHub](https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/calculator.py)
#     - [Super simple inverted index in Python · GitHub](https://gist.github.com/HonzaKral/d90d344bca18ffa71139ac11b9f83124)

# References:
# - [How to pass formatted text to a buffer ? · Issue \#711 · prompt\-toolkit/python\-prompt\-toolkit · GitHub](https://github.com/prompt-toolkit/python-prompt-toolkit/issues/711)
#     - [lira/widgets\.py](https://github.com/pythonecuador/lira/blob/92cb843981099a8230aa32f5dd7b26b26e2daa95/lira/tui/widgets.py#L71-L197)

from prompt_toolkit import Application, ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import fragment_list_to_text, to_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.processors import (
    HighlightSelectionProcessor,
    Processor,
    Transformation,
)

FOCUSABLE_CHILDREN_NAMES = ["entries", "preview"]
FOCUSABLE_CHILDREN = [0, 2]
FOCUSED_CHILD_IDX = 0

kb = KeyBindings()


@kb.add("c-c")
@kb.add("q")
def exit_(event):
    event.app.exit()


@kb.add("j")
def down_(event):
    if event.current_buffer.name in FOCUSABLE_CHILDREN_NAMES:
        event.current_buffer.cursor_down()


@kb.add("k")
def up_(event):
    if event.current_buffer.name in FOCUSABLE_CHILDREN_NAMES:
        event.current_buffer.cursor_up()


@kb.add("h")
def left_(event):
    if event.current_buffer.name in FOCUSABLE_CHILDREN_NAMES:
        event.current_buffer.cursor_left()


@kb.add("l")
def right_(event):
    if event.current_buffer.name in FOCUSABLE_CHILDREN_NAMES:
        event.current_buffer.cursor_right()


@kb.add("tab")
def cycle_(event):
    global FOCUSED_CHILD_IDX, FOCUSABLE_CHILDREN
    FOCUSED_CHILD_IDX = (FOCUSED_CHILD_IDX + 1) % len(FOCUSABLE_CHILDREN)
    focused_child_window_idx = FOCUSABLE_CHILDREN[FOCUSED_CHILD_IDX]
    next_child = event.app.layout.container.children[focused_child_window_idx]
    event.app.layout.focus(next_child)


class FormatTextProcessor(Processor):
    """
    Custom processor to represent formatted text.
    It makes use of :py:class:`FormattedBufferControl`.
    """

    def apply_transformation(self, transformation_input):
        formatted_lines = transformation_input.buffer_control.formatted_lines
        lineno = transformation_input.lineno
        max_lineno = len(formatted_lines) - 1
        if lineno > max_lineno:
            line = ""
        else:
            line = formatted_lines[lineno]
        return Transformation(to_formatted_text(line))


class FormattedBufferControl(BufferControl):
    def __init__(self, formatted_text, **kwargs):
        self.formatted_lines = self.parse_formatted_text(formatted_text)
        super().__init__(**kwargs)

    def parse_formatted_text(self, formatted_text):
        """
        Transform a formatted text with newlines into a list.
        This is to make it compatible with the processor.
        Each element represents a line of text.
        """
        lines = []
        line = []
        for format in formatted_text:
            style, text, *_ = format
            word = []
            for c in text:
                if c != "\n":
                    word.append(c)
                    continue

                if word:
                    line.append((style, "".join(word)))
                    lines.append(line)
                elif not word and line:
                    lines.append(line)
                else:
                    lines.append([("", "")])
                line = []
                word = []
            if word:
                line.append((style, "".join(word)))
        if line:
            lines.append(line)
        return lines


class MultiPane:
    def __init__(self, entries, callback):
        self.entries = entries
        self.callback = callback

        self.current_lineno = 1
        self.max_entry_width = min(max(map(lambda x: len(x), entries.split("\n"))), 48)
        self.entries_control = BufferControl(
            buffer=Buffer(
                document=Document(self.entries, 0),
                name="entries",
                on_cursor_position_changed=self.update,
                read_only=True,
            )
        )
        self.preview_text = ANSI(self.callback(self.current_lineno))
        formatted_text = to_formatted_text(self.preview_text)
        plain_text = fragment_list_to_text(formatted_text)
        self.preview_control = FormattedBufferControl(
            buffer=Buffer(
                document=Document(plain_text, 0),
                name="preview",
                on_cursor_position_changed=self.update_preview,
                read_only=True,
            ),
            focusable=True,
            formatted_text=formatted_text,
            include_default_input_processors=False,
            input_processors=[FormatTextProcessor(), HighlightSelectionProcessor()],
        )
        # Alternative (not scrollable):
        # self.preview_control = FormattedTextControl(
        #     focusable=True,
        #     show_cursor=True,
        #     text=ANSI(self.callback(self.current_lineno)),
        # )
        self.root_container = VSplit(
            [
                Window(
                    content=self.entries_control,
                    width=self.max_entry_width,
                    wrap_lines=True,
                ),
                Window(width=3, char=" | "),
                Window(content=self.preview_control, wrap_lines=True),
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

    def update_preview(self, buffer):
        self.update(self.entries_control.buffer)

    def update(self, buffer):
        new_lineno = self.get_lineno(self.entries, buffer.cursor_position)
        if self.current_lineno != new_lineno:
            self.current_lineno = new_lineno

            text = ANSI(self.callback(self.current_lineno))
            formatted_text = to_formatted_text(text)
            plain_text = fragment_list_to_text(formatted_text)
            self.preview_control.buffer.set_document(
                Document(plain_text, 0), bypass_readonly=True
            )
            self.preview_control.formatted_lines = self.preview_control.parse_formatted_text(
                formatted_text
            )

    def run(self):
        self.app.run()
