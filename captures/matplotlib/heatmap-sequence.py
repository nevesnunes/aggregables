#!/usr/bin/env python3

from math import sqrt, floor
import matplotlib.pyplot as plt
import numpy as np
import sys


def closest_square(n):
    while sqrt(n) - floor(sqrt(n)) != 0:
        n += 1
    return n


if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    a = data[data.dtype.names[0]]
    min_a = int(min(a)) - 1
    ra = int(max(a) - min(a)) + 2
    csa = closest_square(ra)
    d = np.zeros(ra)
    for i in range(len(a)):
        d[int(a[i]) - min_a] += 1
    for i in range(csa - ra):
        d = np.append(d, np.array([0]))
    d = d.reshape(int(sqrt(csa)), int(sqrt(csa)))
    plt.matshow(d, cmap="BuGn")
    plt.colorbar()
    plt.show()
