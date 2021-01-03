#!/usr/bin/env python3

import diff_match_patch
import sys

MAX_CHUNK_DISPLAY_LEN = 80


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
        change_type = pair[0]
        chunk_hex = pair[1]
        if change_type == -1:
            change_symbol = "-"
            next_offset -= len(chunk_hex)
        elif change_type == 1:
            change_symbol = "+"
            next_offset += len(chunk_hex)
        elif change_type == 0:
            offset = next_offset
            change_symbol = " "
            next_offset += len(chunk_hex)
        # Ommit middle bytes when outputting large differences.
        # Prefer displaying more start bytes than end bytes, as relevant
        # info is more likely to be at start (e.g. metadata, headers...).
        if len(chunk_hex) > MAX_CHUNK_DISPLAY_LEN:
            print(
                f"{change_symbol}{hex(offset//2).rjust(8)}: {chunk_hex[:MAX_CHUNK_DISPLAY_LEN - 20]} [...] {chunk_hex[-20:]} | {bytes.fromhex(chunk_hex[:MAX_CHUNK_DISPLAY_LEN - 20])} [...] {bytes.fromhex(chunk_hex[-20:])} [Ommitted {(len(chunk_hex) - MAX_CHUNK_DISPLAY_LEN) // 2} byte(s)]"
            )
        else:
            print(
                f"{change_symbol}{hex(offset//2).rjust(8)}: {chunk_hex} | {bytes.fromhex(chunk_hex)}"
            )
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
