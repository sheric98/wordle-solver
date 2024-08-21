from collections import defaultdict, deque
from decimal import Decimal
from functools import lru_cache
import numpy as np
import time
from typing import Iterable, Optional
from uuid import uuid4

from wordle_solver.common.guess_result import GuessResult, to_res_arr
from wordle_solver.common.solve_status.solve_status_np import SolveStatusNp
from wordle_solver.common.word_reducer import WordReducer
from wordle_solver.common.word_reducer_constants import SOLVED

GUESS_THRESHOLD = Decimal('0.5')
FULL_FAIL_SCORE = 100

_CHILD = None


def init_scorer_child(words: list[str], starting_guesses: int, max_guesses: int, max_depth: int):
    global _CHILD
    _CHILD = ScorerChild(words, starting_guesses, max_guesses, max_depth)


def process(word_i):
    return _CHILD.process_word(word_i)


def prepare(args):
    process_id, word_idxs = args
    return _CHILD.prepare(process_id, word_idxs)


def update(args) -> str:
    update_id, word, res = args
    return _CHILD.update(update_id, word, res)


def reset(reset_id: int) -> str:
    return _CHILD.reset(reset_id)


def get_base_word_and_distr(word_reducer: WordReducer, max_guesses: int, max_depth: int, curr_guesses: int, curr_depth: int) -> Optional[tuple[str, Decimal]]:
    num_answers = word_reducer.num_answers()
    if num_answers == 1:
        return word_reducer.get_arbitrary_word(), Decimal(1)
    
    highest_freq, highest_word = word_reducer.get_top_freq()
    total_guess_num = curr_guesses + curr_depth + 1
    if total_guess_num == max_guesses:
        return highest_word, highest_freq + (Decimal(1) - highest_freq) * Decimal(FULL_FAIL_SCORE)
    elif curr_depth == max_depth:
        return highest_word, highest_freq + (Decimal(1) - highest_freq) * Decimal(FULL_FAIL_SCORE)
    else:
        return None


class ScorerChild:
    def __init__(self, words: list[str], starting_guesses: int, max_guesses: int, max_depth: int):
        self._words = words
        self._ss = SolveStatusNp()
        self._word_reducer = WordReducer(words, self._ss)
        self._id = str(uuid4())
        self._prepare_id = -1
        self._update_id = -1
        self._reset_id = -1

        self._max_depth = max_depth
        self._max_guesses = max_guesses
        self._starting_guesses = starting_guesses
        self._curr_guesses = starting_guesses

        self._candidate_words = None
        self._curr_depth = None

    def prepare(self, prepare_id: int, candidate_words: list[int]):
        if prepare_id == self._prepare_id:
            time.sleep(0.5)
            return self._id
        
        self._candidate_words = candidate_words
        self._prepare_id = prepare_id
        return self._id
    
    def _get_single_guess_ev(self, guess_i: int) -> Decimal:
        res = Decimal(0)
        guess_arr, res_arrs, weights = self._word_reducer.get_guess_distr_and_counts(guess_i)
        
        for res_arr, weight in zip(res_arrs, weights):
            if np.array_equal(res_arr, SOLVED):
                res += Decimal(weight)

            else:
                self._ss.try_add_word(guess_arr, res_arr)
                key = self._ss.key()
                res += (Decimal(1) + self._best_ev_cached(key)) * Decimal(weight)
                self._ss.undo()

        res /= Decimal(np.sum(weights))

        return res
    
    @lru_cache(maxsize=1000000)
    def _best_ev_cached(self, tup):
        self._curr_depth += 1
        self._word_reducer.try_update()
        next_ev = self._best_ev()
        self._word_reducer.undo()
        self._curr_depth -= 1

        return next_ev

    def _best_ev(self) -> deque[Decimal]:
        if (base_res := get_base_word_and_distr(
            self._word_reducer, self._max_guesses, self._max_depth, self._curr_guesses, self._curr_depth)) is not None:
            return base_res[1]

        # candidate_guesses = self._candidate_guesser.get_candidate_guesses(list(trie.trie_words), solve_status)
        if self._candidate_words is None:
            candidate_guesses = self._word_reducer.get_top_candidates()
        else:
            candidate_guesses = self._candidate_words
        
        return min(self._get_single_guess_ev(i) for i in candidate_guesses)

    # depth will never be zero in this function
    def process_word(self, word_i: int) -> Decimal:
        self._curr_depth = 0
        return self._get_single_guess_ev(word_i)

    def update(self, update_id: int, word: str, res: GuessResult) -> str:
        if update_id == self._update_id:
            time.sleep(0.5)
            return self._id

        res_arr = to_res_arr(word, res)
        word_arr = self._word_reducer.get_guess_arr(word)
        self._ss.update(word_arr, res_arr)
        self._word_reducer.update()
        self._curr_guesses += 1

        self._udpate_id = update_id
        return self._id

    def reset(self, reset_id: int) -> str:
        if reset_id == self._reset_id:
            time.sleep(0.5)
            return self._id
        
        self._ss = SolveStatusNp()
        self._word_reducer = WordReducer(self._words, self._ss)
        self._update_id = -1
        self._prepare_id = -1
        self._curr_guesses = self._starting_guesses

        self._reset_id = reset_id
        return self._id
