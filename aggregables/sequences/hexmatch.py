#!/usr/bin/env python3

# TODO:
# Memory scanner: Given n files, return offsets matching corresponding n values

import argparse
import binascii
import re
import sys

try:
    import colorama
    colorama.init()
    def highlight_bold(text):
        return colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
    def highlight_primary(text):
        return colorama.Fore.RED + colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
except ImportError:
    def highlight_bold(text):
        return str(text)
    def highlight_primary(text):
        return str(text)


def clean_needle(needle):
    bytes_clean = "".join(needle.split()).strip()
    raw_bytes = bytes_clean
    if re.search(r"\\x", raw_bytes):
        raw_bytes = bytes(bytes_clean, "latin-1")
    else:
        try:
            raw_bytes = binascii.a2b_hex(bytes_clean)
        except binascii.Error as e:
            print(f"Assuming literal bytes due to error: {e}")
            raw_bytes = bytes(bytes_clean, "latin-1")

    return raw_bytes


def match(data, needle):
    return [x.start() for x in re.finditer(re.escape(needle), data)]


def natural_sort_key(s, _re=re.compile(r'(\d+)')):
    return [int(t) if i & 1 else t.lower() for i, t in enumerate(_re.split(s))]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", action="store_true", help="fuzzy match with all heuristics (e.g. endianness, off-by-k...)")
    parser.add_argument("-e", "--endianness", type=str, choices=["be", "le"], help="match with either big (be) or little (le) endianness")
    parser.add_argument("-k", "--off-by-k", type=int, help="match any bytes in range [needle-k..needle+k]")
    parser.add_argument('file', type=str, help="file to search in")
    parser.add_argument('needle', type=str, help="byte sequence to search for")
    parsed_args = parser.parse_args()

    endianness = ["be"]
    k = 0
    if parsed_args.all:
        endianness = ["be", "le"]
        k = 8
    if parsed_args.endianness:
        endianness = [parsed_args.endianness]
    if parsed_args.off_by_k:
        k = parsed_args.off_by_k

    raw_bytes = clean_needle(parsed_args.needle)

    filename = parsed_args.file
    matched = False
    with open(filename, "rb") as f:
        data = f.read()

    results = []
    for i in range(-k, k + 1, 1):
        for e in endianness:
            raw_len = len(raw_bytes)
            needle = int.from_bytes(raw_bytes, "big")
            needle += i
            needle = bytearray(needle.to_bytes(raw_len, "big"))
            if e == "le":
                needle = needle[::-1]
            needle = bytes(needle)
            offsets = match(data, needle)
            for offset in offsets:
                iteration = ""
                if e != "be" or i != 0:
                    iteration = f"e={e},k={'+' if i > 0 else ''}{i}"
                results.append(f"{highlight_bold(filename)}:{highlight_primary(offset)}({highlight_primary(hex(offset))}):{highlight_bold(iteration)}{':' if iteration else ''}{binascii.hexlify(needle).decode('ascii')} {needle}")

    if len(results) < 1:
        sys.exit(1)
    results = sorted(results, key=natural_sort_key)
    for result in results:
        print(result)
