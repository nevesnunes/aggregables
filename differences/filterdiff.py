#!/usr/bin/env python3

import difflib
import sys
import re

DEBUG = False
REPLACE_PREFIX = "__027b596b_2b2b_451e_b051_2130237b863f__{}__"


def debug(*args):
    if DEBUG:
        print(args)


def compute_replacements(patterns, texts):
    replace_counter = 0
    replacements = {}
    for pattern in patterns:
        for i, c in enumerate(texts):
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


def apply_replacements(replacements, texts):
    replaced_texts = []
    for i, c in enumerate(texts):
        replaced_text = c
        for k, v in replacements.items():
            for matched_str in v["matched_strs"][i]:
                debug(matched_str, v["replace_str"], replaced_text)
                replaced_text = re.sub(matched_str, v["replace_str"], replaced_text, 1)
        replaced_texts.append(replaced_text)
    debug(f"replaced_texts: {replaced_texts}")
    return replaced_texts


def compute_diffs(rules, text1, text2):
    patterns = []
    for rule in rules:
        patterns.append(re.compile(rule.strip(), re.IGNORECASE | re.MULTILINE))

    texts = [text1, text2]
    replacements = compute_replacements(patterns, texts)
    replaced_texts = apply_replacements(replacements, texts)

    diffs = difflib.unified_diff(
        replaced_texts[0].split("\n"),
        replaced_texts[1].split("\n"),
        fromfile="base",
        tofile="derivative",
    )
    replaced_diffs = []
    for diff in diffs:
        for k, v in replacements.items():
            for i in range(2):
                for matched_str in v["matched_strs"][i]:
                    diff = re.sub(v["replace_str"], matched_str, diff, 1)
            replaced_diffs.append(diff.rstrip())
    return replaced_diffs


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f1:
        rules = f1.readlines()
    with open(sys.argv[2], "r") as f2:
        text1 = f2.read().strip()
    with open(sys.argv[3], "r") as f3:
        text2 = f3.read().strip()

    for diff in compute_diffs(rules, text1, text2):
        print(diff)
