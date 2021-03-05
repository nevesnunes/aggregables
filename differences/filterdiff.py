#!/usr/bin/env python3

from typing import Any, Dict, List
import difflib
import os
import re
import sys

DEBUG = bool(os.environ.get("DEBUG"))
EXACT = bool(os.environ.get("EXACT"))
if EXACT:
    REPLACE_STR = "__027b596b_2b2b_451e_b051_2130237b863f__{}__"
else:
    REPLACE_STR = "\x00"


def debug(*args: Any, indent: int = 0) -> None:
    if DEBUG:
        print(" " * indent, args)


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
        elif text[0] == "-":
            return (
                colorama.Fore.RED
                + colorama.Style.BRIGHT
                + str(text)
                + colorama.Style.RESET_ALL
            )
        elif text[0] == "@":
            return colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
        else:
            return str(text)


except ImportError:

    def highlight(text):
        return str(text)


def compute_replacements(rules: List[str], texts: List[str]) -> Dict[int, Any]:
    patterns = []
    for rule in rules:
        patterns.append(re.compile(rule.strip(), re.IGNORECASE | re.MULTILINE))

    replace_counter = 0
    replacements: Dict[int, Any] = {}
    pattern_replace_strs = {}
    for i, c in enumerate(texts):
        previous_text = c
        text_to_replace = c
        needs_replace = True
        while needs_replace:
            if not text_to_replace:
                break

            next_group = ""
            next_match = None
            next_match_start = float("inf")
            next_pattern = None
            for pattern in patterns:
                debug(pattern, text_to_replace, indent=4)
                maybe_match = re.search(pattern, text_to_replace)
                debug(maybe_match, indent=8)
                if maybe_match and maybe_match.start() < next_match_start:
                    next_group = maybe_match.groups()[0]
                    next_match_start = maybe_match.start()
                    next_match = maybe_match
                    next_pattern = pattern
            if not next_match:
                break

            if EXACT:
                if pattern not in pattern_replace_strs:
                    replace_str = REPLACE_STR.format(replace_counter)
                    replace_counter += 1
                    pattern_replace_strs[pattern] = replace_str
                replace_str = pattern_replace_strs[pattern]
            else:
                replace_str = REPLACE_STR * len(next_group)

            if i not in replacements:
                replacements[i] = []
            replacements[i].append(
                {
                    "group": next_group,
                    "pattern": next_pattern,
                    "replace_str": replace_str,
                }
            )
            debug(i, text_to_replace, next_pattern, next_group, replace_str, indent=4)

            text_to_replace = text_to_replace[next_match.end() :]
            if text_to_replace == previous_text or not text_to_replace:
                needs_replace = False
            previous_text = text_to_replace
    debug(f"replacements: {replacements}")
    return replacements


def apply_replacements(replacements: Dict[int, Any], texts: List[str]) -> List[str]:
    replaced_texts = []
    for i, c in enumerate(texts):
        text_to_replace = c
        replaced_text = ""
        if i in replacements:
            for match_dict in replacements[i]:
                match = re.search(match_dict["pattern"], text_to_replace)
                if not match:
                    print(
                        f"No match for pattern '{match_dict['pattern']}'",
                        file=sys.stderr,
                    )
                    continue

                replaced_end = match.start() + len(match_dict["replace_str"])
                replaced_chunk = re.sub(
                    match_dict["group"], match_dict["replace_str"], text_to_replace, 1
                )
                debug(f"replaced_chunk: {replaced_chunk}", indent=4)
                debug(replaced_chunk[replaced_end:], indent=8)
                debug(replaced_chunk[:replaced_end], indent=8)
                replaced_text += replaced_chunk[:replaced_end]
                text_to_replace = replaced_chunk[replaced_end:]
                if not text_to_replace:
                    break
        # include last chunk that wasn't matched
        replaced_text += text_to_replace
        replaced_texts.append(replaced_text)
    debug(f"replaced_texts: {replaced_texts}")
    return replaced_texts


def compute_diffs(rules: List[str], text1: str, text2: str) -> List[str]:
    texts = [text1, text2]
    replacements = compute_replacements(rules, texts)
    replaced_texts = apply_replacements(replacements, texts)

    diffs = difflib.unified_diff(
        replaced_texts[0].split("\n"),
        replaced_texts[1].split("\n"),
        fromfile="base",
        tofile="derivative",
        n=max(len(replaced_texts[0]), len(replaced_texts[1])),
    )
    text1_lines = text1.split("\n")
    text2_lines = text2.split("\n")
    new_text_lines = []
    text1_pos = 0
    text2_pos = 0
    for i in range(3):
        next(diffs)
    for diff in diffs:
        if diff[0] == " ":
            new_text_lines.append(text1_lines[text1_pos])
            text1_pos += 1
            text2_pos += 1
        elif diff[0] == "-":
            text1_pos += 1
        elif diff[0] == "+":
            new_text_lines.append(text2_lines[text2_pos])
            text2_pos += 1

    new_text = "\n".join(new_text_lines)
    diffs = difflib.unified_diff(
        text1.split("\n"), new_text.split("\n"), fromfile="base", tofile="derivative",
    )
    return list(map(lambda x: highlight(x.rstrip()), diffs))


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f1:
        rules = f1.readlines()
    with open(sys.argv[2], "r") as f2:
        text1 = f2.read().strip()
    with open(sys.argv[3], "r") as f3:
        text2 = f3.read().strip()

    for diff in compute_diffs(rules, text1, text2):
        print(diff)
