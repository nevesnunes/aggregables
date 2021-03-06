#!/usr/bin/env python3

# References:
# - [How to pass formatted text to a buffer ? · Issue \#711 · prompt\-toolkit/python\-prompt\-toolkit · GitHub](https://github.com/prompt-toolkit/python-prompt-toolkit/issues/711)
#     - [lira/widgets\.py](https://github.com/pythonecuador/lira/blob/92cb843981099a8230aa32f5dd7b26b26e2daa95/lira/tui/widgets.py#L71-L197)
# - [python\-prompt\-toolkit/calculator\.py at master · prompt\-toolkit/python\-prompt\-toolkit · GitHub](https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/calculator.py)
# - [Python prompt\_toolkit: Pick best fuzzy match when the user presses enter \- Stack Overflow](https://stackoverflow.com/questions/61167987/python-prompt-toolkit-pick-best-fuzzy-match-when-the-user-presses-enter)
# - [How can I remove the ANSI escape sequences from a string in python \- Stack Overflow](https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python)

import re
from prompt_toolkit import Application, ANSI
from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.filters import (
    Condition,
    has_completions,
    completion_is_selected,
)
from prompt_toolkit.formatted_text import fragment_list_to_text, to_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.widgets import SearchToolbar, TextArea
from prompt_toolkit.layout.containers import (
    Float,
    FloatContainer,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.processors import (
    HighlightSelectionProcessor,
    Processor,
    Transformation,
)

MOTION_CHILD_NAMES = ["entries", "preview"]


@Condition
def motion_filter() -> bool:
    """
    Enable when the current buffer is a motion child.
    """
    return get_app().current_buffer.name in MOTION_CHILD_NAMES


kb = KeyBindings()


kb.add("tab")(focus_next)
kb.add("s-tab")(focus_previous)
kb.add("c-n")(focus_next)
kb.add("c-p")(focus_previous)

kb.add("j", filter=motion_filter)(lambda event: event.current_buffer.cursor_down())
kb.add("k", filter=motion_filter)(lambda event: event.current_buffer.cursor_up())
kb.add("h", filter=motion_filter)(lambda event: event.current_buffer.cursor_left())
kb.add("l", filter=motion_filter)(lambda event: event.current_buffer.cursor_right())

kb.add("c-c")(lambda event: event.app.exit())
kb.add("q", filter=motion_filter)(lambda event: event.app.exit())


completion_filter = has_completions & ~completion_is_selected


@kb.add("enter", filter=completion_filter)
def completion_handle(event):
    event.current_buffer.go_to_completion(0)
    event.current_buffer.validate_and_handle()


@kb.add("c-space")
def completion_start(event):
    """
    Start auto completion. If the menu is showing already, select the next
    completion.
    """
    b = event.app.current_buffer
    if b.complete_state:
        b.complete_next()
    else:
        b.start_completion(select_first=False)


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
    def __init__(
        self,
        entries,
        preview_callback=None,
        input_callback=None,
        input_completions=None,
    ):
        if not entries or len(entries) == 0:
            raise RuntimeError("Entries cannot be empty.")
        self.entries = entries
        self.input_callback = input_callback
        self.preview_callback = preview_callback

        self.ansi_escape_8bit = re.compile(
            r"(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])"
        )
        self.current_lineno = 1
        self.max_entry_width = min(
            max(
                map(
                    lambda x: len(x) + 1, self.ansi_escape_8bit.sub("", entries).split("\n")
                )
            ),
            48,
        )

        entries_text = ANSI(self.entries)
        entries_formatted_text = to_formatted_text(entries_text)
        entries_plain_text = fragment_list_to_text(entries_formatted_text)
        self.entries_control = FormattedBufferControl(
            buffer=Buffer(
                document=Document(entries_plain_text, 0),
                name="entries",
                on_cursor_position_changed=self.update_entries,
                read_only=True,
            ),
            focusable=True,
            formatted_text=entries_formatted_text,
            include_default_input_processors=False,
            input_processors=[FormatTextProcessor(), HighlightSelectionProcessor()],
        )

        if self.preview_callback:
            self.preview_text = ANSI(self.preview_callback(self.current_lineno))
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
            #     text=ANSI(self.preview_callback(self.current_lineno)),
            # )
            entries_container = VSplit(
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
        else:
            entries_container = Window(
                content=self.entries_control,
                width=self.max_entry_width,
                wrap_lines=True,
            )
        if self.input_callback:
            self.search_field = SearchToolbar()
            self.input_field = TextArea(
                accept_handler=self.input_accept,
                completer=FuzzyWordCompleter(list(input_completions)),
                complete_while_typing=True,
                height=1,
                multiline=False,
                prompt="> ",
                search_field=self.search_field,
                wrap_lines=False,
            )
            self.root_container = FloatContainer(
                content=HSplit(
                    [entries_container, Window(height=1, char="-"), self.input_field,]
                ),
                floats=[
                    Float(
                        content=CompletionsMenu(max_height=16, scroll_offset=1),
                        xcursor=True,
                        ycursor=True,
                    )
                ],
            )

        else:
            self.root_container = entries_container
        self.layout = Layout(self.root_container)

        self.app = Application(full_screen=True, key_bindings=kb, layout=self.layout)

    def input_accept(self, buffer):
        self.input_callback(self.input_field.text)

    def get_lineno(self, text, pos):
        text = self.ansi_escape_8bit.sub("", text)
        lineno = 1
        for i, c in enumerate(text):
            if (c == ord(b"\n") or c == "\n") and i != pos:
                lineno += 1
            if i == pos:
                break
            i += 1
        return lineno

    def update_preview(self, buffer):
        self.update_entries(self.entries_control.buffer)

    def update_entries(self, buffer, force=False):
        new_lineno = self.get_lineno(self.entries, buffer.cursor_position)
        if force or self.current_lineno != new_lineno:
            self.current_lineno = new_lineno

            text = ANSI(self.preview_callback(self.current_lineno))
            formatted_text = to_formatted_text(text)
            plain_text = fragment_list_to_text(formatted_text)
            self.preview_control.buffer.set_document(
                Document(plain_text, 0), bypass_readonly=True
            )
            self.preview_control.formatted_lines = self.preview_control.parse_formatted_text(
                formatted_text
            )

    def replace_entries(self, entries):
        self.current_lineno = 1
        self.entries_control.buffer.set_document(
            Document(entries, 0), bypass_readonly=True
        )
        self.update_entries(self.entries_control.buffer, True)

    def run(self):
        self.app.run()
