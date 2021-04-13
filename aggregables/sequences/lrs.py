#!/usr/bin/env python3

from aggregables.sequences.suffix_trees.suffix_trees import STree
from typing import List, Tuple
import itertools
import re
import sys


def parse_contents(contents: List[bytes]) -> Tuple[bytes, List[bytes]]:
    lrs = b""
    if len(contents) < 1:
        return (lrs, contents)

    st = STree.STree(contents)
    if len(contents) == 1:
        lrs = st.lrs()
    elif len(contents) > 1:
        for content in contents:
            s = st.lrs()
            if len(s) > len(lrs):
                lrs = s
        pairs = itertools.combinations(contents, 2)
        for pair in pairs:
            s = st.lcs(pair)
            if len(s) > len(lrs):
                lrs = s

    new_contents = []
    if len(lrs) > 1:
        for content in contents:
            candidate_contents = re.split(re.escape(lrs), content)
            for candidate in candidate_contents:
                if len(candidate) > 0:
                    new_contents.append(candidate)
    else:
        new_contents = contents
    return (lrs, new_contents)


def compute_lrs(content: bytes, min_len_substrings: int = 2) -> List[bytes]:
    contents = [content]
    top_substrings = []
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

    return top_substrings


def clean_lrs(content: bytes, substrings: List[bytes]) -> List[bytes]:
    clean_substrings = []
    for substring in substrings:
        if not re.search(b"\n", substring):
            continue

        match = re.search(re.escape(substring), content, re.MULTILINE)
        if not match:
            raise RuntimeError("Expected lrs to be present in content, no match found.")
        else:
            span = match.span()

        clean_start_pos = None
        for i in range(span[0], span[1]):
            start_c = content[i]
            if start_c == ord(b"\n"):
                # Exclude start new line
                clean_start_pos = i + 1
                break
        if not clean_start_pos:
            continue

        clean_end_pos = None
        for i in range(span[1], span[0], -1):
            end_c = content[i]
            if end_c == ord(b"\n"):
                # Include end new line
                clean_end_pos = i + 1
                break
        if not clean_end_pos or clean_end_pos <= clean_start_pos:
            continue

        clean_substrings.append(content[clean_start_pos:clean_end_pos])

    return clean_substrings


if __name__ == "__main__":
    content = b""
    if not sys.stdin.isatty():
        content = bytes(sys.stdin.read(), encoding="latin-1")
    else:
        with open(sys.argv[1], "rb") as f:
            content = f.read()

    top_substrings = compute_lrs(content)
    # clean_substrings = clean_lrs(content, top_substrings)
    for substring in top_substrings:
        print(substring)
    print(len(top_substrings))
