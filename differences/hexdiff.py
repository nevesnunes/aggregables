#!/usr/bin/env python3

import diff_match_patch
import sys


def isolate_bytes(diff):
    new_diff = []
    last_nibble = None
    for pair in diff:
        len_substring = len(pair[1])
        if pair[0] == 0:
            last_nibble = None
            if len_substring % 2 == 1:
                last_nibble = pair[1][len_substring - 1]
                new_substring = pair[1][: len_substring - 1]
                new_diff.append((pair[0], new_substring))
            else:
                new_diff.append((pair[0], pair[1]))
        else:
            if last_nibble:
                new_substring = last_nibble + pair[1]
                new_diff.append((pair[0], new_substring))
            else:
                new_diff.append((pair[0], pair[1]))
    return new_diff


def print_unified_format(hex_diff):
    change_symbol = None
    offset = 0
    next_offset = 0
    for pair in diff:
        if pair[0] == -1:
            change_symbol = "-"
            next_offset -= len(pair[1])
        elif pair[0] == 1:
            change_symbol = "+"
            next_offset += len(pair[1])
        elif pair[0] == 0:
            offset = next_offset
            change_symbol = " "
            next_offset += len(pair[1])
        print(f"{change_symbol}{hex(offset).rjust(8)}: {pair[1]} | {bytes.fromhex(pair[1])}")
        if pair[0] == 0:
            offset = next_offset


dmp = diff_match_patch.diff_match_patch()
with open(sys.argv[1], "rb") as f1, open(sys.argv[2], "rb") as f2:
    c1 = f1.read()
    c2 = f2.read()
diff = dmp.diff_main(c1.hex(), c2.hex())
dmp.diff_cleanupSemantic(diff)
diff = isolate_bytes(diff)
print_unified_format(diff)
