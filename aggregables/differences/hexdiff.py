#!/usr/bin/env python3

# TODO:
# - To workaround bad performance when comparing large files, split them by chunks, then compare chunks
# - Other formats (e.g. hexdump, disasm...)

import argparse
import diff_match_patch
import gc
import sys

MAX_CHUNK_DISPLAY_LEN = 80


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


# Ensures changesets have an even number of bytes,
# to avoid errors when hex decoding
def isolate_bytes(diff):
    new_diff = []
    last_nibble = None
    last_nibble_carryover = None
    for pair in diff:
        len_substring = len(pair[1])
        if pair[0] == 0:
            last_nibble = None
            if len_substring % 2 == 1:
                if last_nibble_carryover:
                    # if we have a carryover, then add it,
                    # making changeset have even length
                    new_substring = last_nibble_carryover + pair[1]
                    new_diff.append((pair[0], new_substring))
                    last_nibble_carryover = None
                else:
                    # changeset has odd length, store last nibble for next pair
                    last_nibble = pair[1][len_substring - 1]
                    new_substring = pair[1][: len_substring - 1]
                    new_diff.append((pair[0], new_substring))
            else:
                new_diff.append((pair[0], pair[1]))
        else:
            if last_nibble:
                new_substring = last_nibble + pair[1]

                # if adding a nibble makes this changeset have an odd length,
                # then store last nibble for next pair
                len_new_substring = len(new_substring)
                if len_new_substring % 2 == 1:
                    last_nibble_carryover = pair[1][len_substring - 1]
                    new_substring = new_substring[: len_new_substring - 1]

                new_diff.append((pair[0], new_substring))
            else:
                new_diff.append((pair[0], pair[1]))
    return new_diff


def print_unified_format(elements, parsed_args, just_len):
    print(highlight_filename(f"--- {parsed_args.base}"))
    print(highlight_filename(f"+++ {parsed_args.derivative}"))

    change_symbol = None
    base_offset = 0
    next_base_offset = 0
    offset = 0
    next_offset = 0
    for change_type, change_symbol, base_offset, offset, chunk_hex in elements:
        line = change_symbol
        if base_offset != offset:
            line += f"{hex(base_offset // 2).rjust(just_len)},"
        elif parsed_args.columns:
            line += "".rjust(just_len + 1)
        line += f"{hex(offset // 2).rjust(just_len)}: "

        if change_type == 0 or (
            parsed_args.all_diffs and len(chunk_hex) > MAX_CHUNK_DISPLAY_LEN
        ):
            # Ommit middle bytes when outputting large differences.
            # Prefer displaying more start bytes than end bytes, as relevant
            # info is more likely to be at start (e.g. metadata, headers...).
            output_bytes = (
                f"{chunk_hex[:MAX_CHUNK_DISPLAY_LEN - 20]} [...] {chunk_hex[-20:]}"
            )
            if not parsed_args.only_hex:
                output_bytes += f" | {bytes.fromhex(chunk_hex[:MAX_CHUNK_DISPLAY_LEN - 20])} [...] {bytes.fromhex(chunk_hex[-20:])}"
            output_bytes += (
                f" [+ {(len(chunk_hex) - MAX_CHUNK_DISPLAY_LEN) // 2} byte(s)]"
            )
        else:
            output_bytes = f"{chunk_hex}"
            if not parsed_args.only_hex:
                output_bytes += f" | {bytes.fromhex(chunk_hex)}"
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
        chunk_hex = pair[1]
        chunk_len = len(chunk_hex)
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

        elements.append((change_type, change_symbol, base_offset, offset, chunk_hex))

        if change_type == 0:
            offset = next_offset
            base_offset = next_base_offset

    return elements


def diff_bytes(c1, c2):
    dmp = diff_match_patch.diff_match_patch()
    diff = dmp.diff_main(c1.hex(), c2.hex())
    dmp.diff_cleanupSemantic(diff)

    return diff


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
    just_len = max(len(hex(len(c1))), len(hex(len(c2))))

    diff = diff_bytes(c1, c2)
    del c1
    del c2
    gc.collect()

    diff = isolate_bytes(diff)
    elements = unified_format(diff)
    del diff
    gc.collect()

    print_unified_format(elements, parsed_args, just_len)
