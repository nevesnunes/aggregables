#!/usr/bin/env python3

# References:
# - [Super simple inverted index in Python · GitHub](https://gist.github.com/HonzaKral/d90d344bca18ffa71139ac11b9f83124)
# - [GitHub \- willf/inverted\_index: A simple in memory inverted index in Python](https://github.com/willf/inverted_index)

import re
from collections import defaultdict, Counter


class ReverseIndex:
    def __init__(
        self, data, data_synonyms={}, not_regexes=[], pass_regexes=[], fields=[]
    ):
        if len(fields) == 0:
            raise RuntimeError("Must pass at least one field")

        self.combine_operators = {
            "OR": self.combine_or,
            "AND": self.combine_and,
        }
        self.not_regexes = list(map(lambda x: re.compile(x), not_regexes))
        self.pass_regexes = list(map(lambda x: re.compile(x), pass_regexes))
        if len(self.pass_regexes) == 0:
            self.pass_regexes.append(re.compile(r"[a-zA-Z0-9_\.]+"))
        self.split_regex = re.compile(r"[^a-zA-Z0-9_\.]")

        self.data = data
        self.data_synonyms = data_synonyms
        self.words = set()
        self.index_docs(data, fields)

    def combine_and(self, *args):
        if not args:
            return Counter()
        out = args[0].copy()
        for c in args[1:]:
            for doc_id in list(out):
                if doc_id not in c:
                    del out[doc_id]
                else:
                    out[doc_id] += c[doc_id]
        return out

    def combine_or(self, *args):
        if not args:
            return Counter()
        out = args[0].copy()
        for c in args[1:]:
            out.update(c)
        return out

    def tokenize(self, text):
        yield from self.split_regex.split(text)

    def text_only(self, tokens):
        ignore_token = False
        for t in tokens:
            for not_regex in self.not_regexes:
                if not_regex.match(t):
                    ignore_token = True
                    break

            if ignore_token:
                ignore_token = False
                continue

            for pass_regex in self.pass_regexes:
                if pass_regex.match(t):
                    yield t

    def lowercase(self, tokens):
        for t in tokens:
            yield t.lower()

    def stem(self, tokens):
        for t in tokens:
            if t.endswith("ly"):
                t = t[:-2]
            yield t

    def synonyms(self, tokens):
        for t in tokens:
            yield self.data_synonyms.get(t, t)

    def analyze(self, text):
        tokens = self.tokenize(text)
        for token_filter in (self.text_only, self.lowercase, self.stem, self.synonyms):
            tokens = token_filter(tokens)
        yield from tokens

    def index_docs(self, docs, fields):
        self.index = defaultdict(lambda: defaultdict(Counter))
        for id, doc in enumerate(docs):
            for field in fields:
                for token in self.analyze(doc[field]):
                    self.index[field][token][id] += 1
                    self.words.add(token)

    def search_in_fields(self, query, fields):
        for t in self.analyze(query):
            yield self.combine_operators["OR"](*(self.index[f][t] for f in fields))

    def search(self, query, operator="AND", fields=None):
        combine = self.combine_operators[operator]
        return combine(*(self.search_in_fields(query, fields or self.index.keys())))

    def query(self, query, operator="AND", fields=None):
        ids = self.search(query, operator, fields)
        for doc_id, score in ids.most_common():
            yield self.data[doc_id], score
