#!/usr/bin/env python3

from filterdiff import compute_diffs
import unittest


class Tests(unittest.TestCase):
    def test_single_rule(self):
        rules = ["([0-9]+)"]
        with open("test1-text1-filterdiff", "r") as f1:
            text1 = f1.read().strip()
        with open("test1-text2-filterdiff", "r") as f2:
            text2 = f2.read().strip()
        with open("test1-expected-filterdiff", "r") as f3:
            expected_diffs = [x.rstrip() for x in f3.readlines()]
        diffs = compute_diffs(rules, text1, text2)
        self.assertListEqual(diffs, expected_diffs)
