#!/usr/bin/env python3

from hexdiff import diff_bytes, isolate_bytes, print_unified_format
import unittest


class Tests(unittest.TestCase):
    def test_no_diff(self):
        c1 = b"ab\n"
        c2 = c1[:]
        expected_diff = [(0, "61620a")]
        expected_isolated_diff = expected_diff[:]
        expected_offsets = [0]
        self.assertDiffs(
            c1, c2, expected_diff, expected_isolated_diff, expected_offsets
        )

    def test_add_1(self):
        c1 = b"aa\n"
        c2 = b"aba\n"
        expected_diff = [(0, "616"), (1, "26"), (0, "10a")]
        expected_isolated_diff = [(0, "61"), (1, "62"), (0, "610a")]
        expected_offsets = [0, 1, 2]
        self.assertDiffs(
            c1, c2, expected_diff, expected_isolated_diff, expected_offsets
        )

    def test_sub_1(self):
        c1 = b"aab\n"
        c2 = b"ab\n"
        expected_diff = [(0, "616"), (-1, "16"), (0, "20a")]
        expected_isolated_diff = [(0, "61"), (-1, "61"), (0, "620a")]
        expected_offsets = [0, 1, 1]
        self.assertDiffs(
            c1, c2, expected_diff, expected_isolated_diff, expected_offsets
        )

    def test_subadd_1_same_len(self):
        c1 = b"ab\n"
        c2 = b"ac\n"
        expected_diff = [(0, "616"), (-1, "2"), (1, "3"), (0, "0a")]
        expected_isolated_diff = [(0, "61"), (-1, "62"), (1, "63"), (0, "0a")]
        expected_offsets = [0, 1, 1, 2]
        self.assertDiffs(
            c1, c2, expected_diff, expected_isolated_diff, expected_offsets
        )

    def test_many_diffs(self):
        c1 = b"abaababbbbbb"
        c2 = b"acaacacc"
        expected_diff = [(0, '616'), (-1, '2'), (1, '3'), (0, '61616'), (-1, '2'), (1, '3'), (0, '616'), (-1, '26262626262'), (1, '363')]
        expected_isolated_diff = [(0, '61'), (-1, '62'), (1, '63'), (0, '6161'), (-1, '62'), (1, '63'), (0, '61'), (-1, '626262626262'), (1, '6363')]
        expected_offsets = [0, 1, 1, 2, 4, 4, 5, 6, 6]
        self.assertDiffs(
            c1, c2, expected_diff, expected_isolated_diff, expected_offsets
        )

    def assertDiffs(
        self, c1, c2, expected_diff, expected_isolated_diff, expected_offsets
    ):
        diff = diff_bytes(c1, c2)
        self.assertListEqual(diff, expected_diff)
        isolated_diff = isolate_bytes(diff)
        self.assertListEqual(isolated_diff, expected_isolated_diff)
        offsets = print_unified_format(isolated_diff, "base", "derivative")
        self.assertListEqual(offsets, expected_offsets)
