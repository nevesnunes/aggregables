#!/usr/bin/env python3

import collections
import sys

with open(sys.argv[1], "r") as f:
    lines = f.readlines()
    pair_counts = {}
    el_counts = {}
    max_counts = 0
    for line in lines:
        line = line.split()
        name_1 = line[0].lower().strip()
        name_2 = line[1].lower().strip()
        # Order insensitive
        tuple_el_1 = name_1 if name_1 < name_2 else name_2
        tuple_el_2 = name_1 if name_1 > name_2 else name_2
        v = int(line[2].strip())

        if v > max_counts:
            max_counts = v

        if tuple_el_1 not in el_counts:
            el_counts[tuple_el_1] = 0
        el_counts[tuple_el_1] += v
        if tuple_el_2 not in el_counts:
            el_counts[tuple_el_2] = 0
        el_counts[tuple_el_2] += v
        k = (tuple_el_1, tuple_el_2)

        if k not in pair_counts:
            pair_counts[k] = 0
        pair_counts[k] += v

    el_counts = collections.OrderedDict(
        sorted(el_counts.items(), key=lambda i: i[1], reverse=True)
    )
    pair_counts = collections.OrderedDict(
        sorted(pair_counts.items(), key=lambda i: i[1], reverse=True)
    )

    el_counts_list = list(el_counts)
    m = [[0 for i in range(len(el_counts_list))] for j in range(len(el_counts_list))]
    for i1 in range(len(el_counts_list)):
        for i2 in range(i1 + 1, len(el_counts_list)):
            k1 = el_counts_list[i1]
            k2 = el_counts_list[i2]
            tuple_el_1 = k1 if k1 < k2 else k2
            tuple_el_2 = k1 if k1 > k2 else k2
            tuple_els = (tuple_el_1, tuple_el_2)
            if tuple_els in pair_counts:
                count_els = pair_counts[tuple_els]
                m[i1][i2] += count_els
                # print("{}:{}={}".format(i1, i2, count_els))

    out_strs = ["" for i in range(len(el_counts_list) + 1)]
    for i1 in range(len(el_counts_list)):
        for i2 in range(i1, len(el_counts_list)):
            if i1 == i2:
                continue

            v = m[i1][i2]
            out_str = " "
            if v > max_counts / 2:
                out_str = "O"
            elif v > max_counts / 3:
                out_str = "o"
            elif v > max_counts / 4:
                out_str = "u"
            elif v > 0:
                out_str = "."
            out_strs[i2] += out_str + "|"
            # out_strs[i2] += str(v) + '|'
            # print("{}:{}={}".format(i1, i2, v))

    for i in range(len(out_strs) - 1):
        out_str = out_strs[i]
        name = el_counts_list[i]
        print("|" + out_str + name)
    print()
    for i in pair_counts.items():
        print("{} {}".format(str(i[1]).rjust(len(str(max_counts))), i[0]))
