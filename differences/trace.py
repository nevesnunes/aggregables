#!/usr/bin/env python3

import math
import re
import sys

lines = None
if not sys.stdin.isatty():
    lines = [x.strip() for x in sys.stdin.readlines()]
else:
    with open(sys.argv[1], "r") as f:
        lines = [x.strip() for x in f.readlines()]

pattern = re.compile(r"(?P<variable>[^ ]*) (?P<value>.*)", re.IGNORECASE)
history = []
state = {}
seen_variables = set()
max_count = 0
for line in lines:
    match = pattern.match(line.strip())
    if not match:
        continue

    match_dict = match.groupdict()
    variable = match_dict["variable"]
    value = match_dict["value"]
    if variable not in state:
        state[variable] = {
            "old_count": 0,
            "new_count": 1,
            "old_value": None,
            "new_value": value,
        }
    else:
        state[variable] = {
            "old_count": state[variable]["new_count"],
            "new_count": state[variable]["new_count"] + 1,
            "old_value": state[variable]["new_value"],
            "new_value": value,
        }
    if state[variable]["new_count"] > max_count:
        max_count = state[variable]["new_count"]
    history.append((variable, state[variable]))
    seen_variables.add(variable)

history_state = {}
for variable in seen_variables:
    history_state[variable] = {
        "old_count": 0,
        "new_count": 0,
        "old_value": None,
        "new_value": None,
    }
history_state_keys = sorted(history_state)
for event in history:
    variable = event[0]
    state = event[1]
    history_state[variable] = state
    for history_variable in history_state_keys:
        just = int(math.log10(max_count)) + 1
        old_count = str(history_state[history_variable]["old_count"])
        new_count = str(history_state[history_variable]["new_count"])
        old_value = history_state[history_variable]["old_value"]
        new_value = history_state[history_variable]["new_value"]
        if history_variable == variable:
            print(f"-[{old_count.rjust(just)}]{history_variable.rjust(8)}: {old_value}")
            print(f"+[{new_count.rjust(just)}]{history_variable.rjust(8)}: {new_value}")
        else:
            print(f" [{new_count.rjust(just)}]{history_variable.rjust(8)}: {new_value}")
    print("~~~")
