from typing import Any, Callable, Optional

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.analyzer.scorer.scorer import Scorer
from wordle_solver.common.trie import Trie
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.util.constants import NUMBER_OF_GUESSES


class Analyzer:
    def __init__(
            self,
            candidate_guesser_builder: Callable[[Trie], CandidateGuesser],
            full_words: list[str],
            starting_word: Optional[str],
            max_search_depth: Optional[int] = None,
            progress_bar=True):
        self._full_words = full_words
        self._trie = Trie(full_words)
        self._solve_status = SolveStatus()
        if max_search_depth is None:
            max_search_depth = NUMBER_OF_GUESSES
        curr_guesses = 0 if starting_word is None else 1
        candidate_guesser = candidate_guesser_builder(self._trie)
        self._scorer = Scorer(
            candidate_guesser,
            full_words,
            max_search_depth,
            NUMBER_OF_GUESSES,
            curr_guesses,
            progress_bar=progress_bar)
        self._word = starting_word

    def update(self, results: list[SingleResult], word=None):
        if word is None:
            word = self._word
        self._solve_status.add_results(word, results)
        new_words = self._trie.get_words(self._solve_status)
        self._trie = Trie(new_words)
        self._word = None

    def get_best_guess(self) -> str:
        if self._word is None:
            self._word = self._scorer.get_best_word(self._trie, self._solve_status)
        return self._word
    