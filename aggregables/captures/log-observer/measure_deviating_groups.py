#!/usr/bin/env python3

import normalize_timestamps

import dateparser
import re
import statistics
import sys

with open(sys.argv[1], "r") as f:
    content = f.readlines()
with open(sys.argv[2], "r") as f:
    rules = f.readlines()
from_timestamp=dateparser.parse(sys.argv[3])

patterns = []
for rule in rules:
    patterns.append(re.compile(rule.strip(), re.IGNORECASE))
event_sets = [{}, {}]
for line in content:
    for pattern in patterns:
        match = pattern.match(line.strip())
        if match:
            break
    if not match:
        continue

    match_dict = match.groupdict()
    timestamp = dateparser.parse(match_dict['date'])
    if not timestamp:
        timestamp = normalize_timestamps.date(match_dict['date'])
    for key in match_dict:
        i = 0
        if timestamp.date() > from_timestamp.date():
            i = 1
        if key not in event_sets[i]:
            event_sets[i][key] = {}
        value = match_dict[key]
        if value not in event_sets[i][key]:
            event_sets[i][key][value] = 0
        event_sets[i][key][value] += 1
        if '_count' not in event_sets[i]:
            event_sets[i]['_count'] = 0
        event_sets[i]['_count'] += 1

comparisons = []
for key in event_sets[0].keys():
    if key.startswith('_'):
        continue

    all_subkeys = set()
    for i in range(2):
        for subkey in event_sets[i][key].keys():
            all_subkeys.add(subkey)
    all_subkeys_stdev = 0
    for subkey in all_subkeys:
        subvalues = [0] * 2
        for i in range(2):
            if subkey in event_sets[i][key].keys():
                subvalues[i] = event_sets[i][key][subkey] / event_sets[i]['_count']
        all_subkeys_stdev += statistics.pstdev(subvalues)
    comparisons.append({'stdev':all_subkeys_stdev, 'key':key})

comparisons = sorted(comparisons, key=lambda x: x['stdev'])
for comparison in comparisons:
    key = comparison['key']
    if key.startswith('_'):
        continue

    stdev = comparison['stdev']
    print(f"---\n{key} (std_dev: {stdev})")
    for i in range(2):
        subitems = sorted(event_sets[i][key].items(), key=lambda x: x[1], reverse=True)
        print(f"\t{subitems}")
