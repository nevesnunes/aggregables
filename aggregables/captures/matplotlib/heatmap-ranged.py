#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    a = data[data.dtype.names[0]]
    b = data[data.dtype.names[1]]
    min_a = int(min(a))
    min_b = int(min(b))
    ra = int(max(a) - min(a)) + 1
    rb = int(max(b) - min(b)) + 1
    d = np.zeros((ra, rb))
    for i in range(len(a)):
        d[int(a[i]) - min_a, int(b[i]) - min_b] += 1
    plt.matshow(d, cmap="BuGn")
    plt.colorbar()
    plt.show()
