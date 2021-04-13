#!/usr/bin/env python3

from aggregables.captures.multipane_tui import MultiPane
from aggregables.differences.filterdiff import (
    compute_replacements,
    apply_replacements,
    REPLACE_STR_DEFAULT,
)
from aggregables.sequences.lrs import compute_lrs, clean_lrs

from collections import OrderedDict
import re
import sys


try:
    import colorama

    colorama.init()

    def highlight(text):
        if text[0] == "+":
            return (
                colorama.Fore.GREEN
                + colorama.Style.BRIGHT
                + str(text)
                + colorama.Style.RESET_ALL
            )
        else:
            return str(text)


except ImportError:

    def highlight(text):
        return str(text)


def get_text(lineno):
    text = []
    k = list(collapsed_occurrences.keys())[lineno - 1]
    for i in collapsed_occurrences[k]:
        text.append(original_lines[i])
    return "\n".join(text)


def reduce_repeated_lines(lines):
    seen_i = None
    seen_line = None
    collapsed_occurrences = {}
    for i, line in enumerate(lines):
        if not line == seen_line:
            seen_i = i
            seen_line = line
        if seen_i not in collapsed_occurrences:
            collapsed_occurrences[seen_i] = [i]
        else:
            collapsed_occurrences[seen_i].append(i)

    return OrderedDict(sorted(collapsed_occurrences.items(), key=lambda x: int(x[0])))


def reduce_text(text, lines):
    text = bytes(text, encoding="latin-1")
    newline_positions = [x.span()[0] for x in re.finditer(b"\n", text)]
    top_substrings = compute_lrs(text)
    clean_substrings = clean_lrs(text, top_substrings)

    seen_i = None
    collapsed_occurrences = {}
    covered_lines = set()
    for substring in clean_substrings:
        matches = re.finditer(b"(" + re.escape(substring) + b")+", text, re.MULTILINE)
        for match in matches:
            span = match.span()
            seen_newlines = 0
            start_i = None
            end_i = None
            for pos in newline_positions:
                if not start_i and span[0] < pos:
                    start_i = seen_newlines
                if not end_i and span[1] < pos:
                    end_i = seen_newlines
                seen_newlines += 1

            if start_i in covered_lines:
                # Already part of a collapsed entry
                continue
            covered_lines.update([x for x in range(start_i, end_i)])

            seen_i = start_i
            if seen_i not in collapsed_occurrences:
                collapsed_occurrences[seen_i] = []
            for i in range(start_i, end_i):
                collapsed_occurrences[seen_i].append(i)

    for i, line in enumerate(lines):
        if i not in covered_lines:
            collapsed_occurrences[i] = [i]

    return OrderedDict(sorted(collapsed_occurrences.items(), key=lambda x: int(x[0])))


original_text = open(sys.argv[1], "r").read()
original_lines = original_text.split("\n")
texts = [original_text]
rules = open(sys.argv[2], "r").readlines()
replacements = compute_replacements(rules, texts)
replaced_text = apply_replacements(replacements, texts)[0]
replaced_lines = replaced_text.split("\n")

# collapsed_occurrences = reduce_repeated_lines(replaced_lines)
collapsed_occurrences = reduce_text(replaced_text, replaced_lines)
collapsed_lines = []
for i in collapsed_occurrences.keys():
    if len(collapsed_occurrences[i]) > 1:
        line = "+" + replaced_lines[i].replace(REPLACE_STR_DEFAULT, "?")
    else:
        line = " " + original_lines[i]
    line = line.rstrip()
    if line:
        collapsed_lines.append(highlight(line))

md = MultiPane("\n".join(collapsed_lines), get_text)
md.run()
