#!/usr/bin/env python3

from category_index import ReverseIndex
from multipane_tui import MultiPane
import funcdiff
import sys


def get_text(lineno):
    for cm in current_matches:
        if cm["lineno_index"] == lineno - 1:
            target_match = cm
            break

    i = target_match["cache_index"]
    if i not in cache:
        diff = funcdiff.compute_diff(target_match)
        cache[i] = diff

    return cache[i]


def handle_input(text):
    global current_matches

    results = list(index.query(text))
    filtered_matches = []
    if len(results) == 0:
        filtered_matches = bms["matches"]
    else:
        for result in results:
            for bm in bms["matches"]:
                if (
                    result[0]["first_name"] == bm["first"]["name"]
                    and result[0]["second_name"] == bm["second"]["name"]
                ) or (
                    result[0]["first_name"] == bm["second"]["name"]
                    and result[0]["second_name"] == bm["first"]["name"]
                ):
                    filtered_matches.append(bm)
    current_matches = []
    for i, bm in enumerate(filtered_matches):
        bm["lineno_index"] = i
        current_matches.append(bm)

    entries = "\n".join(
        [funcdiff.ratio_summary(bm, bms["width"]) for bm in current_matches]
    )
    md.replace_entries(entries)


def clean_instructions(instructions):
    return "\n".join([" ".join(x.split(" ")[1:]) for x in instructions])


cache = {}
index_data = []
bms = funcdiff.compute_best_matches(sys.argv[1], sys.argv[2])
current_matches = []
for i, bm in enumerate(bms["matches"]):
    bm["cache_index"] = i
    bm["lineno_index"] = i
    current_matches.append(bm)
    index_data.append(
        {
            "first_name": bm["first"]["name"],
            "second_name": bm["second"]["name"],
            "first_instructions": clean_instructions(bm["first"]["instructions"]),
            "second_instructions": clean_instructions(bm["second"]["instructions"]),
            "cache_index": bm["cache_index"],
            "lineno_index": bm["lineno_index"],
        }
    )
index = ReverseIndex(
    index_data,
    {},
    "first_name",
    "second_name",
    "first_instructions",
    "second_instructions",
)

entries = "\n".join([funcdiff.ratio_summary(bm, bms["width"]) for bm in current_matches])
md = MultiPane(entries, get_text, handle_input, index.words)
md.run()
