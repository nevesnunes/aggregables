#!/usr/bin/env python3

from suffix_trees.suffix_trees import STree

# Suffix-Tree example.
st = STree.STree("abc\x00defghab")
print(st.find("def"))  # 0
print(st.find_all("ab"))  # {0, 9}
st = STree.STree(b"abc\x00defghab")
print(st.find(b"def"))  # 0
print(st.find_all(b"ab"))  # {0, 9}

# Generalized Suffix-Tree example.
a = ["xxxabcxxx", "adsaabc", "ytysabcrew", "qqqabcqw", "aaabc"]
st = STree.STree(a)
print(st.lcs()) # "abc"
a = [b"xxxa", b"adsaabc", b"ytysabcrew", b"aqqqqqqw", b"aaabc"]
st = STree.STree(a)
print(st.lcs()) # b"a"
