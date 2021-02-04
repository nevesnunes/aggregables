#!/usr/bin/env python3

import difflib
import sys
import re

DEBUG = False
REPLACE_PREFIX = "__027b596b_2b2b_451e_b051_2130237b863f__{}__"


def debug(*args):
    if DEBUG:
        print(args)


def compute_replacements(patterns, contents):
    replace_counter = 0
    replacements = {}
    for pattern in patterns:
        for i, c in enumerate(contents):
            text_to_replace = c
            for match in re.finditer(pattern, c):
                if not text_to_replace:
                    break

                matched_group = match.groups()[0]
                if pattern not in replacements:
                    replace_str = REPLACE_PREFIX.format(replace_counter)
                    replace_counter += 1
                    replacements[pattern] = {
                        "replace_str": replace_str,
                        "matched_strs": {},
                    }
                replace_str = replacements[pattern]["replace_str"]
                if i not in replacements[pattern]["matched_strs"]:
                    replacements[pattern]["matched_strs"][i] = []
                replacements[pattern]["matched_strs"][i].append(matched_group)

                text_to_replace = re.sub(pattern, replace_str, text_to_replace, 1)

                replace_str_index = text_to_replace.index(replace_str)
                text_to_replace = text_to_replace[
                    replace_str_index + len(replace_str) :
                ]
    debug(f"replacements: {replacements}")
    return replacements


def apply_replacements(replacements, contents):
    replaced_texts = []
    for i, c in enumerate(contents):
        replaced_text = c
        for k, v in replacements.items():
            for matched_str in v["matched_strs"][i]:
                debug(matched_str, v["replace_str"], replaced_text)
                replaced_text = re.sub(matched_str, v["replace_str"], replaced_text, 1)
        replaced_texts.append(replaced_text)
    debug(f"replaced_texts: {replaced_texts}")
    return replaced_texts


if __name__ == "__main__":
    patterns_filename = sys.argv[1]
    text1_filename = sys.argv[2]
    text2_filename = sys.argv[3]

    patterns = []
    with open(patterns_filename, "r") as f:
        rules = f.readlines()
        for rule in rules:
            patterns.append(re.compile(rule.strip(), re.IGNORECASE | re.MULTILINE))

    with open(text1_filename, "r") as f1, open(text2_filename, "r") as f2:
        c1 = f1.read().strip()
        c2 = f2.read().strip()

    contents = [c1, c2]
    replacements = compute_replacements(patterns, contents)
    replaced_texts = apply_replacements(replacements, contents)

    diffs = difflib.unified_diff(
        replaced_texts[0].split("\n"),
        replaced_texts[1].split("\n"),
        fromfile=sys.argv[2],
        tofile=sys.argv[3],
    )
    for diff in diffs:
        for k, v in replacements.items():
            for i in range(2):
                for matched_str in v["matched_strs"][i]:
                    diff = re.sub(v["replace_str"], matched_str, diff, 1)
        print(diff.rstrip())
