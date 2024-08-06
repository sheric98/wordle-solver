from heapq import nlargest
from typing import Iterable

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.common.solve_status.single_filter_type import SingleFilterType
from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.common.trie import Trie


class UnusedCharsGuesser(CandidateGuesser):
    def __init__(self, trie: Trie, num_candidate_guesses: int):
        super().__init__(trie)
        self._num_candidate_guesses = num_candidate_guesses

    def _get_analytical_guesses(self, candidate_ans: Iterable[str], solve_status: SolveStatus) -> set[str]:
        return set(nlargest(self._num_candidate_guesses, self._trie.trie_words, key=lambda word: self._information_gained(word, solve_status)))
    
    def _information_gained(self, word: str, solve_status: SolveStatus):
        score = 0
        seen = set()
        for sf, c in zip(solve_status.single_statuses, word):
            if sf.filter_type == SingleFilterType.GUARANTEED:
                if c == sf.val:
                    continue
                single_score = 8
            elif sf.filter_type == SingleFilterType.NOT:
                if c in sf.val:
                    continue
                single_score = 9
            else:
                single_score = 10

            if c in solve_status.must_not_contain:
                continue

            if c not in solve_status.must_contain and c not in solve_status.guaranteeds and c not in seen:
                single_score += 5

            seen.add(c)
            score += single_score

        return score
