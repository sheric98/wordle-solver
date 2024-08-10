from typing import Iterable

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser


class NoGuesser(CandidateGuesser):
    def _get_analytical_guesses(self, candidate_ans: Iterable[str], solve_status) -> set[str]:
        return self._trie.trie_words
