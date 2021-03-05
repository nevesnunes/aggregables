#!/usr/bin/env python3

from multipane_tui import MultiPane


def get_text(lineno):
    return f"@{lineno}"


md = MultiPane("1\n2\n3", get_text)
md.run()
