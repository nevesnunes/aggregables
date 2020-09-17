#!/usr/bin/env python3

import diff_match_patch
import sys
import re


def unified_format(diff):
    changes = []
    change_symbol = None
    has_changes = False
    for pair in diff:
        if pair[0] == -1:
            change_symbol = "-"
            has_changes = True
        elif pair[0] == 1:
            change_symbol = "+"
            has_changes = True
        elif pair[0] == 0:
            change_symbol = ""
        changes.append(f"{change_symbol}{pair[1]}")
    if has_changes:
        return changes


with open(sys.argv[1], "r") as f:
    rules = f.readlines()

patterns = []
for rule in rules:
    patterns.append(re.compile(rule.strip(), re.IGNORECASE))

with open(sys.argv[2], "r") as f1, open(sys.argv[3], "r") as f2:
    c1 = f1.readlines()
    c2 = f2.readlines()

dmp = diff_match_patch.diff_match_patch()
for l1, l2 in [(x.strip(), y.strip()) for x, y in zip(c1, c2)]:
    diff = dmp.diff_main(l1, l2)
    dmp.diff_cleanupSemantic(diff)
    changes = unified_format(diff)
    if changes:
        print(changes)

    for pattern in patterns:
        l1 = re.sub(pattern, "_", l1)
        l2 = re.sub(pattern, "_", l2)
    diff = dmp.diff_main(l1, l2)
    dmp.diff_cleanupSemantic(diff)
    changes = unified_format(diff)
    if changes:
        print(changes, file=sys.stderr)
