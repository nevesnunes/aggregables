#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    a = data[data.dtype.names[0]]
    b = data[data.dtype.names[1]]
    plt.hist2d(
        a,
        b,
        bins=[
            np.arange(0, max(a) * 1.1, 5),
            np.arange(0, max(b) * 1.1, 5),
        ],
    )
    plt.show()
