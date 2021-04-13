#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    a = data[data.dtype.names[0]]
    b = data[data.dtype.names[1]]
    plt.scatter(a, b, marker="s")
    plt.show()
