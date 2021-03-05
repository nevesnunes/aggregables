#!/usr/bin/env python3

from multidiff_cli import MultiDiff
import funcdiff
import sys


def get_text(lineno):
    return funcdiff.compute_diff(bms["matches"][lineno - 1])


bms = funcdiff.compute_best_matches(sys.argv[1], sys.argv[2])
md = MultiDiff(
    "\n".join([funcdiff.ratio_summary(bm, bms["width"]) for bm in bms["matches"]]),
    get_text,
)
md.run()
