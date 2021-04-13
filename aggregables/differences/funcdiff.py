#!/usr/bin/env python3

# TODO:
# - Apply bitmask on opcodes to zero out variant bits (e.g. relative and absolute addresses or nops)
#     - Hash resulting instruction bytes instead of mnemonics
#     - https://www.hex-rays.com/products/ida/tech/flirt/in_depth/#Variability

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
        # FIXME: Consider `pdrj` for non-linear obfuscated functions
        # - [radare2 disassembly commands doesn&\#39;t work properly\. · Issue \#11325 · radareorg/radare2 · GitHub](https://github.com/radareorg/radare2/issues/11325)
        for ins in r2p.cmdj(f"pdfj @{f['offset']}")["ops"]:
            instructions.append(f"{hex(ins['offset'])} {ins['disasm']}")
            opcodes.append(ins["disasm"].split()[0])
        parsed_functions.append(
            {
                "name": f["name"],
                "offset": f["offset"],
                "instructions": instructions,
                "opcodes": opcodes,
                "hash": hash(tuple(opcodes)),
            }
        )

    return parsed_functions


def matches_from_functions(functions, opcode_hashes, reverse=False):
    best_matches = []
    for f1 in functions[0]:
        best_f1_r = 0
        picked_f2 = None
        for f2 in functions[1]:
            if f1 == f2:
                continue
            f1_r = ratio.compute_similarity(f1["opcodes"], f2["opcodes"])
            if best_f1_r < f1_r:
                best_f1_r = f1_r
                picked_f2 = f2
        if not picked_f2:
            picked_f2 = {
                "name": "[N/A]",
                "offset": 0,
                "instructions": [],
                "opcodes": [],
                "hash": hash(tuple([])),
            }

        if reverse:
            first = picked_f2
            second = f1
        else:
            first = f1
            second = picked_f2

        best_matches.append(
            {"ratio": round(best_f1_r, 4), "first": first, "second": second}
        )

    best_matches = sorted(best_matches, key=lambda x: x["ratio"], reverse=True)
    best_matches = list(
        filter(
            lambda x: x["ratio"] < 1.0
            and (
                not x["second"]["hash"] in opcode_hashes
                or opcode_hashes[x["second"]["hash"]] != 0
            ),
            best_matches,
        )
    )

    return best_matches


def compute_best_matches(filename1, filename2):
    parsed_functions_1 = parse_functions(sys.argv[1])
    parsed_functions_2 = parse_functions(sys.argv[2])

    # To avoid false positives due to functions in the first listing
    # also existing in the second listing, track relative number of
    # occurrences. This way, only functions exclusive to the second listing
    # are persisted when filtering matches.
    opcode_hashes = {}
    for pf1 in parsed_functions_1:
        pf1_hash = pf1["hash"]
        if pf1_hash not in opcode_hashes:
            opcode_hashes[pf1_hash] = 0
        opcode_hashes[pf1_hash] += 1
    for pf2 in parsed_functions_2:
        pf2_hash = pf2["hash"]
        if pf2_hash not in opcode_hashes:
            opcode_hashes[pf2_hash] = 0
        opcode_hashes[pf2_hash] -= 1
    best_matches = matches_from_functions(
        (parsed_functions_1, parsed_functions_2), opcode_hashes
    )

    # To include new functions from the second listing, we do a second pass,
    # processing the unmatched functions of both listings from the first pass.
    best_opcode_hashes = set()
    for bm in best_matches:
        best_opcode_hashes.add(bm["first"]["hash"])
        best_opcode_hashes.add(bm["second"]["hash"])
    distinct_functions_1 = list(
        filter(
            lambda x: x["hash"] not in best_opcode_hashes
            and opcode_hashes[x["hash"]] != 0,
            parsed_functions_1,
        )
    )
    distinct_functions_2 = list(
        filter(
            lambda x: x["hash"] not in best_opcode_hashes
            and opcode_hashes[x["hash"]] != 0,
            parsed_functions_2,
        )
    )
    best_matches += matches_from_functions(
        (distinct_functions_2, distinct_functions_1), best_opcode_hashes, True
    )

    max_width = 0
    for bm in best_matches:
        max_width = max(len(bm["first"]["name"]), max_width)

    return {"matches": best_matches, "width": max_width}


def compute_diff(bm):
    rules = ["((0x[0-9a-f]+)|([0-9]+))"]
    text1 = "\n".join(bm["first"]["instructions"])
    text2 = "\n".join(bm["second"]["instructions"])

    return "\n".join(filterdiff.compute_diffs(rules, text1, text2))


def ratio_summary(bm, max_width):
    return f"{bm['ratio']:6} | {bm['first']['name']:>{max_width}} | {bm['second']['name']}"


if __name__ == "__main__":
    bms = compute_best_matches(sys.argv[1], sys.argv[2])
    for bm in bms["matches"]:
        print(ratio_summary(bm, bms["width"]))
