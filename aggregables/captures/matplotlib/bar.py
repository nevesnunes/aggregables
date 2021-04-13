#!/usr/bin/env python3

import io
import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    data = None
    if not sys.stdin.isatty():
        contents = sys.stdin.read()
        data = np.genfromtxt(io.StringIO(contents), delimiter=",", names=True)
    else:
        filename = sys.argv[1]
        data = np.genfromtxt(filename, delimiter=",", names=True)

    a = data[data.dtype.names[0]]
    var_count = len(data.dtype.names)
    # Sub-1 factor introduces gaps, but sub-unit widths may result in invisible bars
    # width = 0.75 / var_count
    width = 1 / var_count
    br = np.arange(
        -width * ((var_count + 1) / 2), len(a) - width * ((var_count + 1) / 2)
    )
    for i in range(var_count):
        values = data[data.dtype.names[i]]
        br = [x + width for x in br]
        plt.bar(br, values, width, align="center")

    plt.show()
