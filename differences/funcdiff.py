#!/usr/bin/env python3

import filterdiff
import ratio

import r2pipe
import sys


def parse_functions(filename):
    r2p = r2pipe.open(filename)
    r2p.cmd("aaa")
    functions = r2p.cmdj("aflj")
    parsed_functions = []
    for f in functions:
        if f["name"].startswith("sym.imp."):
            # Skip imports
            continue

        instructions = []
        opcodes = []
        # FIXME: Consider `pdrj`
        for ins in r2p.cmdj(f"pdfj @{f['offset']}")["ops"]:
            instructions.append(ins["disasm"])
            opcodes.append(ins["disasm"].split()[0])
        parsed_functions.append(
            {
                "name": f["name"],
                "offset": f["offset"],
                "instructions": instructions,
                "opcodes": opcodes,
            }
        )

    return parsed_functions


def compute_best_matches(filename1, filename2):
    parsed_functions_1 = parse_functions(sys.argv[1])
    parsed_functions_2 = parse_functions(sys.argv[2])
    best_matches = []
    max_width = 0
    for pf1 in parsed_functions_1:
        best_pf1_r = 0
        picked_pf2 = None
        for pf2 in parsed_functions_2:
            if pf1 == pf2:
                continue
            pf1_r = ratio.compute_ratio(pf1["opcodes"], pf2["opcodes"])
            if best_pf1_r < pf1_r:
                best_pf1_r = pf1_r
                picked_pf2 = pf2
        best_matches.append(
            {"ratio": round(best_pf1_r, 4), "first": pf1, "second": picked_pf2}
        )

    best_matches = sorted(best_matches, key=lambda x: x["ratio"], reverse=True)
    best_matches = list(filter(lambda x: x["ratio"] < 1.0, best_matches))
    for bm in best_matches:
        max_width = max(len(bm["first"]["name"]), max_width)

    return {"matches": best_matches, "width": max_width}


def compute_diff(bm):
    rules = ["((0x[0-9a-f]+)|([0-9]+))"]
    text1 = "\n".join(bm["first"]["instructions"])
    text2 = "\n".join(bm["second"]["instructions"])

    return "\n".join(filterdiff.compute_diffs(rules, text1, text2))


def ratio_summary(bm, max_width):
    return (
        f"{bm['ratio']:6} | {bm['first']['name']:>{max_width}} | {bm['second']['name']}"
    )


if __name__ == "__main__":
    bms = compute_best_matches(sys.argv[1], sys.argv[2])
    for bm in bms["matches"]:
        print(ratio_summary(bm, bms["width"]))
