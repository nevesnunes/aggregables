#!/usr/bin/env python3

import diff_match_patch
import sys

MAX_CHUNK_DISPLAY_LEN = 80


try:
    import colorama
    colorama.init()
    def highlight_filename(text):
        return colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
    def highlight_addition(text):
        return colorama.Fore.GREEN + colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
    def highlight_removal(text):
        return colorama.Fore.RED + colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
except ImportError:
    def highlight_filename(text):
        return str(text)
    def highlight_addition(text):
        return str(text)
    def highlight_removal(text):
        return str(text)


# Ensures changesets have an even number of bytes,
# to avoid errors when hex decoding
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


def print_unified_format(hex_diff, filename_old, filename_new):
    print(highlight_filename(f"--- {filename_old}"))
    print(highlight_filename(f"+++ {filename_new}"))

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
        line = None
        if len(chunk_hex) > MAX_CHUNK_DISPLAY_LEN:
            line = f"{change_symbol}{hex(offset//2).rjust(8)}: {chunk_hex[:MAX_CHUNK_DISPLAY_LEN - 20]} [...] {chunk_hex[-20:]} | {bytes.fromhex(chunk_hex[:MAX_CHUNK_DISPLAY_LEN - 20])} [...] {bytes.fromhex(chunk_hex[-20:])} [Ommitted {(len(chunk_hex) - MAX_CHUNK_DISPLAY_LEN) // 2} byte(s)]"
        else:
            line = f"{change_symbol}{hex(offset//2).rjust(8)}: {chunk_hex} | {bytes.fromhex(chunk_hex)}"
        if change_type == 1:
            print(highlight_addition(line))
        elif change_type == -1:
            print(highlight_removal(line))
        else:
            print(line)
            offset = next_offset


if __name__ == "__main__":
    filename_old = sys.argv[1]
    filename_new = sys.argv[2]
    with open(filename_old, "rb") as f1, open(filename_new, "rb") as f2:
        c1 = f1.read()
        c2 = f2.read()

    dmp = diff_match_patch.diff_match_patch()
    diff = dmp.diff_main(c1.hex(), c2.hex())
    dmp.diff_cleanupSemantic(diff)
    diff = isolate_bytes(diff)
    print_unified_format(diff, filename_old, filename_new)
