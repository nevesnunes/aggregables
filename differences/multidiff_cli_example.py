#!/usr/bin/env python3

from multidiff_cli import MultiDiff


def get_text(lineno):
    return f"@{lineno}"


md = MultiDiff("1\n2\n3", get_text)
md.run()
