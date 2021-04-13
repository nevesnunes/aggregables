#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    a = data[data.dtype.names[0]]
    b = data[data.dtype.names[1]]
    max_a = int(max(a))
    max_b = int(max(b))
    min_a = int(min(a))
    min_b = int(min(b))
    d = np.zeros((max_a + 1, max_b + 1))
    for i in range(len(a)):
        d[int(a[i]), int(b[i])] += 1
    fig, ax = plt.subplots()
    ax.set_xlim(min_b - 0.5, max_b + 0.5)
    ax.set_ylim(min_a - 0.5, max_a + 0.5)
    ax.invert_yaxis()
    img = ax.matshow(d, cmap="BuGn",)
    fig.colorbar(img)
    plt.show()
