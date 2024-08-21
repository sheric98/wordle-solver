from collections import Counter, defaultdict, deque
from decimal import Decimal
from tqdm import tqdm
from typing import Any, Iterable, Optional
import numpy as np

from wordle_solver.analyzer.scorer.scorer_child import get_base_word_and_distr
from wordle_solver.analyzer.scorer.scorer_pool import ScorerPool
from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.common.word_reducer import WordReducer
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.solve_status.solve_status_np import SolveStatusNp

GUESS_THRESHOLD = Decimal('0.8')


class Scorer:
    def __init__(
            self,
            scorer_pool: ScorerPool,
            word_reducer: WordReducer,
            solve_status: SolveStatusNp,
            candidate_guesser: CandidateGuesser,
            full_words: list[str],
            max_search_depth: int,
            max_guesses: int,
            curr_guesses: int = 0,
            progress_bar: bool = True):
        self._base_guesses = curr_guesses

        self._scorer_pool = scorer_pool
        self._word_reducer = word_reducer
        self._ss = solve_status
        self._candidate_guesser = candidate_guesser
        self._full_words = full_words
        self._max_search_depth = max_search_depth
        self._max_guesses = max_guesses
        self._curr_guesses = curr_guesses
        self._progress_bar = progress_bar

    def get_best_word(self) -> str:
        if self._progress_bar:
            print(f'Reduced search space to: {self._word_reducer.num_answers()}')

        remaining_guesses = self._max_guesses - self._curr_guesses
        depth = min(remaining_guesses - 1, self._max_search_depth)


        if (res := get_base_word_and_distr(self._word_reducer, self._max_guesses, self._max_search_depth, self._curr_guesses, 0)) is not None:
            self._curr_guesses += 1
            return res[0]
        
        self._curr_guesses += 1

        itr = self._word_reducer.get_top_candidates()
        best_idx = np.argmin(self._scorer_pool.process(itr, len(itr)))

        return self._full_words[itr[best_idx]]
    
    def reset(self, word_reducer: WordReducer, solve_status: SolveStatusNp):
        self._word_reducer = word_reducer
        self._ss = solve_status
        self._curr_guesses = self._base_guesses
    