#!/usr/bin/env python3

from lrs import parse_contents
from suffix_trees.suffix_trees import STree
import colorama
import re
import sys

colorama.init()

lines = None
if not sys.stdin.isatty():
    lines = [x.strip() for x in sys.stdin.readlines()]
else:
    with open(sys.argv[1], "r") as f:
        lines = [x.strip() for x in f.readlines()]

delimiter = " "
text = delimiter.join(lines)
contents = [text]
top_substrings = []
min_len_substrings = 2
min_len_remaining_string = 10
max_len_top_substrings = 10
is_satisfied = True
while is_satisfied:
    len_contents = 0
    for content in contents:
        len_contents += len(content)
    if len_contents < min_len_remaining_string:
        is_satisfied = False
        break

    (lrs, new_contents) = parse_contents(contents)
    contents = new_contents
    if len(lrs) < min_len_substrings:
        is_satisfied = False
        break

    top_substrings.append(lrs)
    if len(top_substrings) > max_len_top_substrings:
        is_satisfied = False
        break


def is_delimited(text, needle):
    p = re.compile(re.escape(needle))
    is_start_delimited = True
    is_end_delimited = True
    for m in p.finditer(text):
        start = m.start()
        end = m.end()
        if start > 0:
            lookbehind_char = text[start - 1 : start]
            if lookbehind_char != delimiter:
                is_start_delimited = False
        if end < len(text) + 1:
            lookahead_char = text[end : end + 1]
            if lookahead_char != delimiter:
                is_end_delimited = False
    return (is_start_delimited, is_end_delimited)


def refine(sequences, text, delimiter):
    # 0x401174 0x401179 = ok
    # 74 0x401179 = nok
    refined_sequences = []
    for s in sequences:
        (is_start_delimited, is_end_delimited) = is_delimited(text, s)
        if is_start_delimited == False:
            s = " ".join(s.split(" ")[1:])
        if is_end_delimited == False:
            s = " ".join(s.split(" ")[:-1])
        if len(s) > 0:
            refined_sequences.append(s)
    return refined_sequences


top_substrings = refine(top_substrings, text, delimiter)
substring_states = []
for s in top_substrings:
    #print(s)
    color_start = None
    color_end = None
    count = 1
    is_color_applicable = False
    p = re.compile(re.escape(s))
    first_start = None
    last_end = None
    for m in p.finditer(text):
        if not first_start:
            first_start = m.start()
            last_end = m.end()
            continue
        if m.start() - last_end == 1:
            (is_start_delimited, is_end_delimited) = is_delimited(
                text, text[first_start : m.end()]
            )
            if is_start_delimited and is_end_delimited:
                color_start = first_start
                color_end = m.end()
                count += 1
                is_color_applicable = True
        else:
            first_start = m.start()
            if is_color_applicable:
                substring_states.append([color_start, color_end, count, s])
                is_color_applicable = False
                count = 0
        last_end = m.end()
    if is_color_applicable:
        substring_states.append([color_start, color_end, count, s])
        is_color_applicable = False
        count = 0

new_text = ""
last_start = 0
for state in substring_states:
    new_text += (
        text[last_start : state[0]]
        + colorama.Fore.RED
        + f"[{state[2]}]{delimiter}"
        + state[3]
        + colorama.Style.RESET_ALL
    )
    last_start = state[1]
new_text += text[last_start:]
print("\n".join(new_text.split(delimiter)))

colorama.deinit()
