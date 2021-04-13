import re

class STree():
    """Class representing the suffix tree."""

    def __init__(self, input=''):
        self.root = _SNode()
        self.root.depth = 0
        self.root.idx = 0
        self.root.parent = self.root
        self.root._add_suffix_link(self.root)
        self.input_type = None
        self.terminal_symbol_length = 1
        self.terminal_symbols = set()

        if not input == '':
            self.build(input)

    def _check_input(self, input):
        """Checks the validity of the input.

        In case of an invalid input throws ValueError.
        """
        if isinstance(input, str):
            return (str, 'st')
        elif isinstance(input, bytes):
            return (bytes, 'st')
        elif isinstance(input, list):
            if all(isinstance(item, str) for item in input):
                return (str, 'gst')
            elif all(isinstance(item, bytes) for item in input):
                return (bytes, 'gst')

        raise ValueError("String argument should be of type 'Bytes' or 'String' or a list of those types")

    def build(self, x):
        """Builds the Suffix tree on the given input.
        If the input is of type List of Strings:
        Generalized Suffix Tree is built.

        :param x: String or List of Strings
        """
        (input_type, tree_type) = self._check_input(x)
        self.input_type = input_type
        if tree_type == 'st':
            terminal_symbol = next(self._terminalSymbolsGenerator())
            if self.input_type == bytes and isinstance(terminal_symbol, str):
                terminal_symbol = bytes(terminal_symbol, 'UTF8')
            self.terminal_symbol_length = len(terminal_symbol)
            self.terminal_symbols.add(terminal_symbol)
            x += terminal_symbol
            self._build(x)
        elif tree_type == 'gst':
            self._build_generalized(x)

    def _build(self, x):
        """Builds a Suffix tree."""
        self.word = x
        self._build_McCreight(x)

    def _build_McCreight(self, x):
        """Builds a Suffix tree using McCreight O(n) algorithm.

        Algorithm based on:
        McCreight, Edward M. "A space-economical suffix tree construction algorithm." - ACM, 1976.
        Implementation based on:
        UH CS - 58093 String Processing Algorithms Lecture Notes
        """
        u = self.root
        d = 0
        for i in range(len(x) - (self.terminal_symbol_length - 1)):
            while u.depth == d and u._has_transition(x[d + i]):
                u = u._get_transition_link(x[d + i])
                d = d + 1
                while d < u.depth and x[u.idx + d] == x[i + d]:
                    d = d + 1
            if d < u.depth:
                u = self._create_node(x, u, d)
            self._create_leaf(x, i, u, d)
            if not u._get_suffix_link():
                self._compute_slink(x, u)
            u = u._get_suffix_link()
            d = d - 1
            if d < 0:
                d = 0

    def _create_node(self, x, u, d):
        i = u.idx
        p = u.parent
        v = _SNode(idx=i, depth=d, input_type=self.input_type)
        v._add_transition_link(u, x[i + d])
        u.parent = v
        p._add_transition_link(v, x[i + p.depth])
        v.parent = p
        return v

    def _create_leaf(self, x, i, u, d):
        w = _SNode(input_type=self.input_type)
        w.idx = i
        w.depth = len(x) - i
        u._add_transition_link(w, x[i + d])
        w.parent = u
        return w

    def _compute_slink(self, x, u):
        d = u.depth
        v = u.parent._get_suffix_link()
        while v.depth < d - 1:
            v = v._get_transition_link(x[u.idx + v.depth + 1])
        if v.depth > d - 1:
            v = self._create_node(x, v, d - 1)
        u._add_suffix_link(v)

    def _build_Ukkonen(self, x):
        """Builds a Suffix tree using Ukkonen's online O(n) algorithm.

        Algorithm based on:
        Ukkonen, Esko. "On-line construction of suffix trees." - Algorithmica, 1995.
        """
        # TODO.
        raise NotImplementedError()

    def _build_generalized(self, xs):
        """Builds a Generalized Suffix Tree (GST) from the array of strings provided.
        """
        terminal_gen = self._terminalSymbolsGenerator()
        _xs = None
        for x in xs:
            terminal_symbol = next(terminal_gen)
            if self.input_type == bytes and isinstance(terminal_symbol, str):
                terminal_symbol = bytes(terminal_symbol, 'UTF8')
            self.terminal_symbol_length = len(terminal_symbol)
            self.terminal_symbols.add(terminal_symbol)
            if not _xs:
                _xs = x + terminal_symbol
            else:
                _xs += x + terminal_symbol
        self.word = _xs
        self._generalized_word_starts(xs)
        self._build(_xs)
        self.root._traverse(self._label_generalized)

    def _label_generalized(self, node):
        """Helper method that labels the nodes of GST with indexes of strings
        found in their descendants.
        """
        if node.is_leaf():
            x = {self._get_word_start_index(node.idx)}
        else:
            x = {n for ns in node.transition_links.values() for n in ns.generalized_idxs}
        node.generalized_idxs = x

    def _get_word_start_index(self, idx):
        """Helper method that returns the index of the string based on node's
        starting index"""
        i = 0
        for _idx in self.word_starts[1:]:
            if idx < _idx:
                return i
            else:
                i += 1
        return i

    def _suffix_contains_terminal_symbol(self, start, end):
        """Validates if suffix was composed with multi-byte terminal symbol"""
        for i in range(0, self.terminal_symbol_length):
            if end+i <= len(self.word):
                candidate_substring = None
                if end-start == self.terminal_symbol_length:
                    candidate_substring = self.word[start+i+1:end+i+1]
                else:
                    candidate_substring = self.word[start+i:end+i+1]
                if candidate_substring in self.terminal_symbols:
                    return True
        return False

    def lcs(self, stringIdxs=-1):
        """Returns the Largest Common Substring of Strings provided in stringIdxs.
        If stringIdxs is not provided, the LCS of all strings is returned.

        ::param stringIdxs: Optional: List of indexes of strings.
        """
        if stringIdxs == -1 or not isinstance(stringIdxs, list):
            stringIdxs = set(range(len(self.word_starts)))
        else:
            stringIdxs = set(stringIdxs)

        deepestNode = self._find_lcs(self.root, stringIdxs)
        start = deepestNode.idx
        end = deepestNode.idx + deepestNode.depth
        return self.word[start:end]

    def _find_lcs(self, node, stringIdxs):
        """Helper method that finds LCS by traversing the labeled GSD."""
        nodes = [self._find_lcs(n, stringIdxs)
                 for n in node.transition_links.values()
                 if n.generalized_idxs.issuperset(stringIdxs)]

        if nodes == []:
            return node

        candidates = sorted(nodes, key=lambda x: x.depth, reverse=True)
        for deepestNode in candidates:
            start = deepestNode.idx
            end = deepestNode.idx + deepestNode.depth
            if self._suffix_contains_terminal_symbol(start, end):
                continue
            else:
                return deepestNode
        return node

    def _dfs_recursive(self, v, state):
        if v not in state:
            state[v] = {'count_leaves': 0}
        for i in v.transition_links.values():
            if i not in state:
                self._dfs_recursive(i, state)
                if i.is_leaf():
                    state[i]['count_leaves'] = 1
                state[v]['count_leaves'] += state[i]['count_leaves']

    def _dfs(self, v):
        state = {}
        self._dfs_recursive(v, state)
        return state

    def lrs(self, count_occurrences=2):
        state = self._dfs(self.root)
        candidates = []
        for n in state:
            if state[n]['count_leaves'] >= count_occurrences:
                candidates.append(n)

        if candidates == []:
            return b'' if self.input_type == bytes else ''

        candidates = sorted(candidates, key=lambda x: x.depth, reverse=True)
        for deepestNode in candidates:
            start = deepestNode.idx
            end = deepestNode.idx + deepestNode.depth
            if self._suffix_contains_terminal_symbol(start, end):
                continue
            else:
                start = deepestNode.idx
                end = deepestNode.idx + deepestNode.depth
                return self.word[start:end]
        return b'' if self.input_type == bytes else ''

    def _generalized_word_starts(self, xs):
        """Helper method returns the starting indexes of strings in GST"""
        self.word_starts = []
        i = 0
        for n in range(len(xs)):
            self.word_starts.append(i)
            i += len(xs[n]) + 1

    def _startswith(self, edge, prefix):
        if self.input_type == bytes and isinstance(prefix, str):
            prefix = bytes(prefix, 'UTF8')
        if isinstance(prefix, str):
            regex = r'^' + prefix
        else:
            regex = bytes(r'^', 'UTF8') + prefix
        return re.match(regex, edge)

    def find(self, y):
        """Returns starting position of the substring y in the string used for
        building the Suffix tree.

        :param y: String
        :return: Index of the starting position of string y in the string used for building the Suffix tree
                 -1 if y is not a substring.
        """
        node = self.root
        while True:
            edge = self._edgeLabel(node, node.parent)
            if self._startswith(edge, y):
                return node.idx

            i = 0
            while (i < len(edge) and edge[i] == y[0]):
                y = y[1:]
                i += 1

            if i != 0:
                if i == len(edge) and y != '':
                    pass
                else:
                    return -1

            node = node._get_transition_link(y[0])
            if not node:
                return -1

    def find_all(self, y):
        node = self.root
        while True:
            edge = self._edgeLabel(node, node.parent)
            if self._startswith(edge, y):
                break

            i = 0
            while (i < len(edge) and edge[i] == y[0]):
                y = y[1:]
                i += 1

            if i != 0:
                if i == len(edge) and y != '':
                    pass
                else:
                    return {}

            node = node._get_transition_link(y[0])
            if not node:
                return {}

        leaves = node._get_leaves()
        return {n.idx for n in leaves}

    def _edgeLabel(self, node, parent):
        """Helper method, returns the edge label between a node and it's parent"""
        return self.word[node.idx + parent.depth: node.idx + node.depth]

    def _terminalSymbolsGenerator(self):
        """Generator of unique terminal symbols used for building the Generalized Suffix Tree.
        Unicode Private Use Area U+E000..U+F8FF is used to ensure that terminal symbols
        are not part of the input string.
        """
        UPPAs = list(list(range(0xE000, 0xF8FF+1)) +
                     list(range(0xF0000, 0xFFFFD+1)) + list(range(0x100000, 0x10FFFD+1)))
        for i in UPPAs:
            yield (chr(i))

        raise ValueError("Too many input strings.")


class _SNode():
    __slots__ = ['_suffix_link', 'transition_links', 'idx', 'depth', 'parent', 'generalized_idxs', 'input_type']

    """Class representing a Node in the Suffix tree."""

    def __init__(self, idx=-1, parentNode=None, depth=-1, input_type=None):
        # Links
        self._suffix_link = None
        self.transition_links = {}
        # Properties
        self.idx = idx
        self.depth = depth
        self.parent = parentNode
        self.generalized_idxs = {}
        self.input_type = input_type

    def __str__(self):
        return ("SNode: idx:" + str(self.idx) + " depth:" + str(self.depth) +
                " transitons:" + str(list(self.transition_links.keys())))

    def _add_suffix_link(self, snode):
        self._suffix_link = snode

    def _get_suffix_link(self):
        if self._suffix_link is not None:
            return self._suffix_link
        else:
            return False

    def _get_transition_link(self, suffix):
        if self.input_type == bytes and isinstance(suffix, str):
            suffix = bytes(suffix, 'UTF8')
        return False if suffix not in self.transition_links else self.transition_links[suffix]

    def _add_transition_link(self, snode, suffix):
        self.transition_links[suffix] = snode

    def _has_transition(self, suffix):
        return suffix in self.transition_links

    def is_leaf(self):
        return len(self.transition_links) == 0

    def _traverse(self, f):
        for node in self.transition_links.values():
            node._traverse(f)
        f(self)

    def _get_leaves(self):
        # Python <3.6 dicts don't perserve insertion order (and even after, we
        # shouldn't rely on dicts perserving the order) therefore these can be
        # out-of-order, so we return a set of leaves.
        if self.is_leaf():
            return {self}
        else:
            return {x for n in self.transition_links.values() for x in n._get_leaves()}
