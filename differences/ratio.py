#!/usr/bin/env python3

import sys

if __name__ == "__main__":
    with open(sys.argv[1], "r") as f1:
        text1 = f1.readlines()
    with open(sys.argv[2], "r") as f2:
        text2 = f2.readlines()

    max_len = max(len(text1), len(text2))
    text1 += "\n" * (max_len - len(text1))
    text2 += "\n" * (max_len - len(text2))

    total = 0
    occurrences = {}
    for t1, t2 in zip(text1, text2):
        if t1.strip():
            if t1 not in occurrences:
                occurrences[t1] = 0
            occurrences[t1] -= 1
            total += 1
        if t2.strip():
            if t2 not in occurrences:
                occurrences[t2] = 0
            occurrences[t2] += 1
            total += 1

    total_v = 0
    for k, v in occurrences.items():
        total_v += abs(v)

    print(1 - round(total_v / total, 2))
