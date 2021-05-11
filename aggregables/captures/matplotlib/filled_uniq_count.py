#!/usr/bin/env python3

from collections import OrderedDict
import sys

if __name__ == "__main__":
    data = None
    if not sys.stdin.isatty():
        data = sys.stdin.readlines()
    else:
        filename = sys.argv[1]
        with open(filename, "rb") as f:
            data = f.readlines()

    min_data = sys.maxsize
    max_data = -sys.maxsize
    occurrences = {}
    for d in data:
        d = d.strip()
        if not d:
            continue

        v = int(d)
        if v not in occurrences:
            occurrences[v] = 0
        occurrences[v] += 1
        if v > max_data:
            max_data = v
        if v < min_data:
            min_data = v
    for i in range(min_data, max_data):
        if i not in occurrences:
            occurrences[i] = 0

    occurrences = OrderedDict(sorted(occurrences.items()))
    for k in occurrences:
        print(occurrences[k])
