#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    a = data[data.dtype.names[0]]
    var_count = len(data.dtype.names)
    width = 0.75 / var_count
    br = np.arange(
        -width * ((var_count + 1) / 2), len(a) - width * ((var_count + 1) / 2)
    )
    for i in range(var_count):
        values = data[data.dtype.names[i]]
        br = [x + width for x in br]
        plt.bar(br, values, width, align="center")
    plt.show()
