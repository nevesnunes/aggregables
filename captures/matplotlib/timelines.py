#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    begin = data[data.dtype.names[0]]
    end = data[data.dtype.names[1]]
    event = ["{}".format(i) for i in range(len(begin))]
    plt.barh(range(len(begin)),  end-begin, left=begin)
    plt.yticks(range(len(begin)), event)
    plt.show()
