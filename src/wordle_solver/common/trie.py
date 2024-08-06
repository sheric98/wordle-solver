from collections import deque
from typing import Optional, Self

from wordle_solver.analyzer.frequency_weigher import FrequencyWeigher
from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.util.constants import WORD_LENGTH
import numpy as np


class _TrieNode:
    def __init__(self, s: str):
        self._chars: set[str] = set(s)
        self._s: str = s
        self._children: dict[str, Self] = {}
        self._word: Optional[str] = None

    def add_char(self, c: str):
        if c not in self._children:
            next_s = self._s + c
            self._children[c] = _TrieNode(next_s)

        return self._children[c]


class Trie:
    def __init__(self, words: list[str]):
        self._head = _TrieNode("")
        self.trie_words = set(words)
        self.trie_size = len(self.trie_words)
        for word in words:
            self._add_word(word)

    def _add_word(self, word: str):
        curr = self._head

        for c in word:
            curr = curr.add_char(c)

        curr._word = word

    def get_words(self, solve_status: SolveStatus) -> list[str]:
        q = deque([(self._head, 0)])

        base_chars_arr = solve_status.get_base_chars_arr()
        # print(base_chars_arr)
        # print(solve_status.greens)
        # print(solve_status._yellows)
        # print(solve_status._uncertains)

        ret: list[str] = []
        while q:
            node, i = q.popleft()
            if node._word is not None:
                if solve_status.get_valid(node._word):
                    ret.append(node._word)
                continue
            # guaranteed_c = solve_status.greens[i]
            # if guaranteed_c is not None:
            #     if guaranteed_c in node._children:
            #         q.append((node._children[guaranteed_c], i + 1))
            #     continue

            # uncertain_candidates = solve_status.get_uncertain_candidates(node._s, base_chars_arr)

            # unused = solve_status.must_contain - node._chars
            # if len(unused) > WORD_LENGTH - i:
            #     continue

            # viable_chars = base_chars_arr[i]

            # if len(unused) == WORD_LENGTH - i:
            #     viable_chars = viable_chars.intersection(unused)
            for c in base_chars_arr[i]:
                if c in node._children:
                    q.append((node._children[c], i + 1))

        return ret
