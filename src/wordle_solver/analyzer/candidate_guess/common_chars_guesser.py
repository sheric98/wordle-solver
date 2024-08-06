from collections import defaultdict
from heapq import nlargest
from typing import Iterable

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.common.solve_status.single_filter_type import SingleFilterType
from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.common.trie import Trie


class CommonCharsGuesser(CandidateGuesser):
    def __init__(self, trie: Trie, num_common_chars: int):
        super().__init__(trie)
        self._num_common_chars = num_common_chars

    def _get_analytical_guesses(self, candidate_ans: Iterable[str], solve_status: SolveStatus) -> set[str]:
        counts = defaultdict(lambda: 0)
        for word in candidate_ans:
            seen = set()
            for sf, c in zip(solve_status.single_statuses, word):
                if sf.filter_type != SingleFilterType.GUARANTEED:
                    if c not in seen:
                        counts[c] += 1
                        seen.add(c)

        top_els = nlargest(self._num_common_chars, counts.keys(), key=lambda c: counts[c])
        return set(self._trie.get_words(SolveStatus.make_char_filter(top_els)))
