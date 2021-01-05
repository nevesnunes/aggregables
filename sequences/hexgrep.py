#!/usr/bin/env python3

# TODO: Include matches based on endianess and off-by-one
# - BE
# - LE
# - +1
# - -1

import binascii
import re
import sys

try:
    import colorama
    colorama.init()
    def highlight_filename(text):
        return colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
    def highlight_offset(text):
        return colorama.Fore.RED + colorama.Style.BRIGHT + str(text) + colorama.Style.RESET_ALL
except ImportError:
    def highlight_filename(text):
        return str(text)
    def highlight_offset(text):
        return str(text)

bytes_clean = "".join(sys.argv[2].split()).strip()
raw_bytes = bytes_clean
if re.search(r"\\x", raw_bytes):
    raw_bytes = bytes(bytes_clean, "latin-1")
else:
    try:
        raw_bytes = binascii.a2b_hex(bytes_clean)
    except binascii.Error as e:
        print(f"Assuming literal bytes due to error: {e}")
        raw_bytes = bytes(bytes_clean, "latin-1")

filename = sys.argv[1]
with open(filename, "rb") as f:
    matched = False
    for x in re.finditer(re.escape(raw_bytes), f.read()):
        matched = True
        print(f"{highlight_filename(filename)}:{highlight_offset(x.start())}({highlight_offset(hex(x.start()))}):{x.group(0)}")
    if not matched:
        sys.exit(1)
