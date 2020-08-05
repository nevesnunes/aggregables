#!/usr/bin/env python3

from suffix_trees.suffix_trees import STree
import ipdb
import itertools
import re
import sys


def parse_contents(contents):
    lrs = ""
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


with ipdb.launch_ipdb_on_exception():
    with open(sys.argv[1], "rb") as f:
        content = f.read()

    contents = [content]
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
    for substring in top_substrings:
        print(substring)
    print(len(top_substrings))
