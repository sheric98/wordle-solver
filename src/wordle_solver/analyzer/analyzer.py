from typing import Any, Callable, Optional

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.analyzer.scorer.scorer import Scorer
from wordle_solver.analyzer.scorer.scorer_pool import ScorerPool
from wordle_solver.common.word_reducer import WordReducer
from wordle_solver.common.guess_result import GuessResult, to_res_arr
from wordle_solver.common.solve_status.solve_status_np import SolveStatusNp
from wordle_solver.util.constants import NUMBER_OF_GUESSES


class Analyzer:
    def __init__(
            self,
            candidate_guesser_builder: Callable[[], CandidateGuesser],
            full_words: list[str],
            starting_word: Optional[str],
            num_processes: int,
            max_search_depth: Optional[int] = None,
            progress_bar=True):
        
        self._full_words = full_words
        self._ss = SolveStatusNp()
        self._word_reducer = WordReducer(full_words, self._ss)

        self._scorer_pool = ScorerPool(num_processes, full_words)

        if max_search_depth is None:
            max_search_depth = NUMBER_OF_GUESSES
        curr_guesses = 0 if starting_word is None else 1
        # candidate_guesser = candidate_guesser_builder(self._trie)
        candidate_guesser = None
        self._scorer = Scorer(
            self._scorer_pool,
            self._word_reducer,
            self._ss,
            candidate_guesser,
            full_words,
            max_search_depth,
            NUMBER_OF_GUESSES,
            curr_guesses,
            progress_bar=progress_bar)
        self._word = starting_word

    def update(self, results: GuessResult, word=None):
        if word is None:
            word = self._word
        res_arr = to_res_arr(word, results)
        word_arr = self._word_reducer.get_guess_arr(word)
        self._ss.update(word_arr, res_arr)
        self._word_reducer.update()
        self._scorer_pool.update(word, results)
        self._word = None

    def get_best_guess(self) -> str:
        if self._word is None:
            self._word = self._scorer.get_best_word()
        return self._word
    