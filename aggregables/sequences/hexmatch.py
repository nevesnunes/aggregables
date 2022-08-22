#!/usr/bin/env python3

import argparse
import binascii
import re
import subprocess
import sys

try:
    import colorama

    colorama.init()

    def highlight_bold(text):
        return colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL

    def highlight_primary(text):
        return (
            colorama.Fore.RED
            + colorama.Style.BRIGHT
            + str(text)
            + colorama.Style.RESET_ALL
        )

    def highlight_secondary(text):
        return (
            colorama.Fore.MAGENTA
            + colorama.Style.BRIGHT
            + str(text)
            + colorama.Style.RESET_ALL
        )

except ImportError:

    def highlight_bold(text):
        return str(text)

    def highlight_primary(text):
        return str(text)


def clean_needle(needle, is_regex):
    clean_bytes = "".join(needle.split()).strip()
    raw_bytes = clean_bytes

    if is_regex:
        return bytes(raw_bytes, "latin-1")

    if re.search(r"\\x", raw_bytes):
        raw_bytes = bytes(clean_bytes, "latin-1")
    else:
        try:
            raw_bytes = binascii.a2b_hex(clean_bytes)
        except binascii.Error as e:
            print(f"Assuming literal bytes due to error: {e}")
            raw_bytes = bytes(clean_bytes, "latin-1")

    return raw_bytes


def match(data, needle, is_regex):
    try:
        clean_needle = needle if is_regex else re.escape(needle)
        return [(x.start(), x.end()) for x in re.finditer(clean_needle, data)]
    except Exception as e:
        raise RuntimeError(f"Bad match with needle={needle}", e)


def match_index_based(data, needle):
    match_i = 0
    indexes = [ord(x)-ord(needle[0]) for x in needle[1:]]
    offsets = []
    try:
        for i in range(len(data) - len(indexes)):
            candidate = bytearray(data[i : i + len(indexes) + 1])
            for j in range(len(indexes)):
                if candidate[j+1] - candidate[0] == indexes[j]:
                    match_i += 1
                    if match_i == len(indexes):
                        offsets.append(i)
                        match_i = 0
                        break
                else:
                    match_i = 0
                    break
        return [(x, x + len(needle)) for x in offsets]
    except Exception as e:
        raise RuntimeError(f"Bad match with needle={needle}", e)


def clean_match(matched_bytes, output_encoding):
    if output_encoding == "bytes":
        return matched_bytes

    try:
        return matched_bytes.decode(output_encoding)
    except UnicodeDecodeError as e:
        return matched_bytes


def natural_sort_key(s, _re=re.compile(r"(\d+)")):
    return [int(t) if i & 1 else t.lower() for i, t in enumerate(_re.split(s))]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="fuzzy match with all heuristics (e.g. endianness, off-by-k...)",
    )
    parser.add_argument(
        "-d",
        "--disassembly_arch",
        type=str,
        help="disassemble matched bytes in the given architecture (format=rasm2)",
    )
    parser.add_argument(
        "-e",
        "--endianness",
        type=str,
        choices=["be", "le"],
        help="match with either big (be) or little (le) endianness",
    )
    parser.add_argument(
        "-i",
        "--index-based",
        action="store_true",
        help="match by alphabet index differential instead of literal bytes (e.g. 'ACDC' -> [+2, +1, -1] will match b'\x00\x02\x03\x02' and b'\x41\x43\x44\x43')",
    )
    parser.add_argument(
        "-k",
        "--off-by-k",
        type=int,
        help="match any bytes in range [needle-k..needle+k]",
    )
    parser.add_argument(
        "-r",
        "--regex",
        default=False,
        action="store_true",
        help="parse needle as regular expression",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="bytes",
        type=str,
        help="encoding used for results output (e.g. latin-1)",
    )
    parser.add_argument(
        "-p",
        "--padding",
        type=int,
        help="pad each byte in pattern with null bytes, to match candidates up to given length (e.g. `-p 2 0102` matches `\x01\x02` and `\x00\x01\x00\x02`)",
    )
    parser.add_argument("file", type=str, help="file to search in")
    parser.add_argument("needle", type=str, help="byte sequence to search for")
    parsed_args = parser.parse_args()

    endianness = ["be"]
    k = 0
    padding = 1
    if parsed_args.all:
        endianness = ["be", "le"]
        k = 8
        padding = 4
    if parsed_args.endianness:
        endianness = [parsed_args.endianness]
    if parsed_args.off_by_k:
        k = parsed_args.off_by_k
    if parsed_args.padding:
        padding = parsed_args.padding
    disassemble_arch = []
    if parsed_args.disassembly_arch:
        disassemble_arch = [parsed_args.disassembly_arch]

    is_needle_regex = parsed_args.regex
    is_index_based = parsed_args.index_based

    raw_bytes = clean_needle(parsed_args.needle, is_needle_regex)

    filename = parsed_args.file
    matched = False
    with open(filename, "rb") as f:
        data = f.read()

    results = []
    for i in range(-k, k + 1, 1):
        for e in endianness:
            for p in range(padding):
                raw_len = len(raw_bytes)
                needle = int.from_bytes(raw_bytes, "big")
                needle += i
                needle = bytearray(needle.to_bytes(raw_len, "big"))
                needle = b"".join([p * b"\x00" + bytes([x]) for x in needle])
                if e == "le":
                    needle = needle[::-1]
                needle = bytes(needle)
                if is_index_based:
                    if is_needle_regex:
                        raise RuntimeError("TODO: Regex with index based matching is not suported.")
                    offsets = match_index_based(data, parsed_args.needle)
                else:
                    offsets = match(data, needle, is_needle_regex)
                for offset in offsets:
                    matched_bytes = data[offset[0] : offset[1]]
                    matched_disassembly = ""
                    for arch in disassemble_arch:
                        matched_disassembly += highlight_secondary(" " + '; '.join(subprocess.check_output(['rasm2', '-a', arch, '-d', binascii.hexlify(matched_bytes).decode('ascii')]).decode('latin-1').split('\n')))
                    iteration = ""
                    if e != "be" or i != 0:
                        iteration = f"e={e},k={'+' if i > 0 else ''}{i}"
                    results.append(
                        f"{highlight_bold(filename)}:{highlight_primary(offset[0])}({highlight_primary(hex(offset[0]))}):{highlight_bold(iteration)}{':' if iteration else ''}{binascii.hexlify(matched_bytes).decode('ascii')} {clean_match(matched_bytes, parsed_args.output)}{matched_disassembly}"
                    )

    if len(results) < 1:
        sys.exit(1)
    results = sorted(results, key=natural_sort_key)
    for result in results:
        print(result)
