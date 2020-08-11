#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
    filename = sys.argv[1]
    data = np.genfromtxt(filename, delimiter=",", names=True)
    event = data[data.dtype.names[0]]
    begin = data[data.dtype.names[1]]
    end = data[data.dtype.names[2]]
    events = {}
    for i, e in enumerate(event):
        ranges = []
        if e not in events:
            events[e] = []
        events[e].append((begin[i], end[i]))
    fig, ax = plt.subplots()
    yticks = []
    yticklabels = []
    for i, e in enumerate(events.items()):
        ax.broken_barh(e[1], (i, 0.5))
        yticks.append(i + 0.25)
        yticklabels.append(e[0])
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    plt.show()
