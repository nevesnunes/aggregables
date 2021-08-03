#!/usr/bin/env python3

from typing import List
import sys


def compute_similarity(input_text1: List[str], input_text2: List[str]) -> float:
    max_len = max(len(input_text1), len(input_text2))
    text1 = input_text1[:]
    text1 += "\n" * (max_len - len(input_text1))
    text2 = input_text2[:]
    text2 += "\n" * (max_len - len(input_text2))

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

    return 1 - round(total_v / total, 2)


def compute_levenshtein_similarity(
    input_text1: List[str], input_text2: List[str]
) -> float:
    total = max(len(input_text1), len(input_text2)) + 1
    text1 = input_text1[:]
    text2 = input_text2[:]
    total_v = _levenshtein_distance(text1, text2)

    return 1 - round(total_v / total, 2)


# References:
# - https://github.com/angr/angr/blob/master/angr/analyses/bindiff.py
# - http://rosettacode.org/wiki/Levenshtein_distance
def _levenshtein_distance(s1: List[str], s2: List[str]) -> float:
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for index2, num2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, num1 in enumerate(s1):
            if num1 == num2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(
                    1
                    + min((distances[index1], distances[index1 + 1], new_distances[-1]))
                )
        distances = new_distances
    return distances[-1]


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f1:
        text1 = f1.readlines()
    with open(sys.argv[2], "r") as f2:
        text2 = f2.readlines()

    print(compute_similarity(text1, text2))
