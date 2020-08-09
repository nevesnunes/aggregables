#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    if len(data.dtype.names) == 2:
        plt.plot(data[data.dtype.names[0]], data[data.dtype.names[1]])
    else:
        plt.plot(data[data.dtype.names[0]])
    plt.show()
