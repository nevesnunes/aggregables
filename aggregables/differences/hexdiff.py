#!/usr/bin/env python3

"""
Diffs two binary files.

For the older version that first converted file bytes to hex
before applying the diff, see ./hexdiff.bin2hex.py

TODO:
- To workaround bad performance when comparing large files, split them by chunks, then compare chunks
- Other formats (e.g. hexdump, disasm...)
"""

import argparse
from vendor.bin_diff_match_patch import diff_match_patch
import gc
import sys

try:
    import colorama

    colorama.init()

    def highlight_filename(text):
        return colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL

    def highlight_addition(text):
        return (
            colorama.Fore.GREEN
            + colorama.Style.BRIGHT
            + str(text)
            + colorama.Style.RESET_ALL
        )

    def highlight_removal(text):
        return (
            colorama.Fore.RED
            + colorama.Style.BRIGHT
            + str(text)
            + colorama.Style.RESET_ALL
        )


except ImportError:

    def highlight_filename(text):
        return str(text)

    def highlight_addition(text):
        return str(text)

    def highlight_removal(text):
        return str(text)


def diff_bytes(c1, c2):
    dmp = diff_match_patch()
    diff = dmp.diff_main(c1, c2)
    dmp.diff_cleanupSemantic(diff)

    return diff


def print_unified_format(elements, parsed_args, just_len, display_len):
    print(highlight_filename(f"--- {parsed_args.base}"))
    print(highlight_filename(f"+++ {parsed_args.derivative}"))

    change_symbol = None
    base_offset = 0
    next_base_offset = 0
    offset = 0
    next_offset = 0
    for change_type, change_symbol, base_offset, offset, chunk_bin in elements:
        line = change_symbol
        if base_offset != offset:
            line += f"{hex(base_offset // 2).rjust(just_len)},"
        elif parsed_args.columns:
            line += "".rjust(just_len + 1)
        line += f"{hex(offset // 2).rjust(just_len)}: "

        if (change_type == 0 or parsed_args.all_diffs) and len(chunk_bin) > display_len:
            # Ommit middle bytes when outputting large differences.
            # Prefer displaying more start bytes than end bytes, as relevant
            # info is more likely to be at start (e.g. metadata, headers...).
            output_bytes = (
                f"{chunk_bin[:display_len - 20].hex()} [...] {chunk_bin[-20:].hex()}"
            )
            if not parsed_args.only_hex:
                output_bytes += (
                    f" -> {chunk_bin[:display_len - 20]} [...] {chunk_bin[-20:]}"
                )
            output_bytes += f" [+ {(len(chunk_bin) - display_len)} byte(s)]"
        else:
            output_bytes = f"{chunk_bin.hex()}"
            if not parsed_args.only_hex:
                output_bytes += f" -> {chunk_bin}"
        line += output_bytes

        if change_type == 1:
            print(highlight_addition(line))
        elif change_type == -1:
            print(highlight_removal(line))
        else:
            print(line)


def unified_format(diff):
    elements = []

    change_symbol = None
    base_offset = 0
    next_base_offset = 0
    offset = 0
    next_offset = 0
    for pair in diff:
        change_type = pair[0]
        chunk_bin = pair[1]
        chunk_len = len(chunk_bin) * 2
        if change_type == -1:
            change_symbol = "-"
            next_base_offset += chunk_len
        elif change_type == 1:
            change_symbol = "+"
            next_offset += chunk_len
        elif change_type == 0:
            change_symbol = " "
            base_offset = next_base_offset
            next_base_offset += chunk_len
            offset = next_offset
            next_offset += chunk_len

        elements.append((change_type, change_symbol, base_offset, offset, chunk_bin))

        if change_type == 0:
            offset = next_offset
            base_offset = next_base_offset

    return elements


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--all-diffs",
        action="store_false",
        help="include middle bytes when outputting large differences",
    )
    parser.add_argument(
        "-c",
        "--columns",
        action="store_true",
        help="align offsets in justified columns (as many as the number of compared files); only applies when diffs include added/removed bytes, since the next changesets will occur on distinct offsets",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=80,
        help="maximum display length used in output chunks",
    )
    parser.add_argument(
        "-x",
        "--only-hex",
        action="store_true",
        help="do not output literal bytes in addition to hex-encoded bytes",
    )
    parser.add_argument("base", type=str, help="base (i.e. old) file name")
    parser.add_argument("derivative", type=str, help="derivative (i.e. new) file name")
    parsed_args = parser.parse_args()

    filename_old = parsed_args.base
    filename_new = parsed_args.derivative
    with open(filename_old, "rb") as f1, open(filename_new, "rb") as f2:
        c1 = f1.read()
        c2 = f2.read()
    diff = diff_bytes(c1, c2)
    just_len = max(len(hex(len(c1))), len(hex(len(c2))))
    del c1
    del c2
    gc.collect()

    elements = unified_format(diff)
    del diff
    gc.collect()

    display_len = parsed_args.length
    print_unified_format(elements, parsed_args, just_len, display_len)
