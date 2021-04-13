#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import io
import re
import sys


@ticker.FuncFormatter
def hex_major_formatter(x, pos):
    return hex(int(x))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hex", action="store_true", help="Use hexadecimal format in labels"
    )
    parser.add_argument("file", nargs="*", help="CSV file")
    parsed_args = parser.parse_args()

    has_names = True
    contents = None
    if not sys.stdin.isatty():
        raw_contents = sys.stdin.read()
        first_line = raw_contents.split("\n")[0]
        contents = io.StringIO(raw_contents)
    else:
        filename = parsed_args.files[0]
        with open(filename, "rb") as f:
            first_line = f.readline()
        contents = filename
    if re.match(r'"\?^[0-9]', first_line):
        has_names = False
    # TODO: Infer dtype
    # - https://numpy.org/devdocs/user/basics.io.genfromtxt.html#choosing-the-data-type
    data = np.genfromtxt(contents, missing_values=0.0, delimiter=",", names=has_names)

    fig, ax = plt.subplots()
    ax.ticklabel_format(useOffset=False, style="plain")
    for tick in ax.get_xticklabels():
        tick.set_fontname("monospace")
    for tick in ax.get_yticklabels():
        tick.set_fontname("monospace")
    if parsed_args.hex:
        ax.yaxis.set_major_formatter(hex_major_formatter)
    if len(data.dtype.names) == 2:
        ax.plot(
            data[data.dtype.names[0]],
            data[data.dtype.names[1]],
            color="lavender",
            marker=".",
            markerfacecolor="black",
            markeredgecolor="black",
            markersize=1.5,
        )
    else:
        ax.plot(
            data[data.dtype.names[0]],
            color="lavender",
            marker=".",
            markerfacecolor="black",
            markeredgecolor="black",
            markersize=1.5,
        )
    plt.show()
