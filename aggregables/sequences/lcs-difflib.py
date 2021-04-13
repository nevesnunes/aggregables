#!/usr/bin/env python3

import difflib

string1 = "abxd"
string2 = "abcdcdvxvd"
matches = difflib.SequenceMatcher(None, string1, string2).get_matching_blocks()
lmb_size = 0
lmb = ""
lcs = ""
for match in matches:
    match_string = string1[match.a : match.a + match.size]
    lcs += match_string
    if match.size > lmb_size:
        lmb = match_string
        lmb_size = match.size
print("longest common substring: {}".format(lcs))
print("  longest matching block: {}".format(lmb))
