from collections import defaultdict, deque
from decimal import Decimal
import time
from typing import Iterable, Optional
from uuid import uuid4

from wordle_solver.common.guess_result import GuessResult, to_res_arr
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.solve_status.solve_status_np import SolveStatusNp
from wordle_solver.common.word_reducer import WordReducer

GUESS_THRESHOLD = Decimal('0.8')

_CHILD = None


def init_scorer_child(words: list[str]):
    global _CHILD
    _CHILD = ScorerChild(words)


def process(args):
    word_i, depth = args
    return _CHILD.process_word(word_i, depth)


def update(args) -> str:
    update_id, word, res = args
    return _CHILD.update(update_id, word, res)


def reset(reset_id: int) -> str:
    return _CHILD.reset(reset_id)


def get_base_word_and_distr(word_reducer: WordReducer, base_case: bool) -> Optional[tuple[str, deque[Decimal]]]:
    num_answers = word_reducer.num_answers()
    if num_answers == 1:
        return word_reducer.get_arbitrary_word(), deque([Decimal(1) / Decimal(num_answers)])
    
    highest_freq, highest_word = word_reducer.get_top_freq()
    if base_case or highest_freq > GUESS_THRESHOLD:
        return highest_word, deque([highest_freq])
    
    return None


class ScorerChild:
    def __init__(self, words: list[str]):
        self._words = words
        self._ss = SolveStatusNp()
        self._word_reducer = WordReducer(words, self._ss)
        self._id = str(uuid4())
        self._update_id = -1
        self._reset_id = -1

    def _score_for_dist(self, probs: deque[Decimal]) -> Decimal:
        multiplier = Decimal(1)

        score = Decimal(0)
        for prob in probs:
            score += multiplier * prob
            multiplier /= Decimal(2)

        return score

    def _aggregate_distributions(self, weights: Iterable[int], distributions: Iterable[deque[Decimal]]) -> deque[Decimal]:
        ret = deque()

        tot = Decimal(0)
        for weight, dist in zip(weights, distributions):
            tot += weight
            for i, d in enumerate(dist):
                if i >= len(ret):
                    ret.append(Decimal(0))
                ret[i] += weight * d

        for i in range(len(ret)):
            ret[i] /= tot

        return ret
    
    def _get_distr(self, guess_i: int, depth: int) -> deque[Decimal]:
        if self._word_reducer.is_valid(guess_i):
            base = Decimal(1) / Decimal(self._word_reducer.num_answers())
        else:
            base = Decimal(0)
        
        guess_arr, res_arrs, cnts = self._word_reducer.get_guess_distr_and_counts(guess_i)
        
        dists = []
        for res_arr in res_arrs:
            self._ss.try_add_word(guess_arr, res_arr)
            self._word_reducer.try_update()
            distribution = self._best_distr(depth - 1)
            self._word_reducer.undo()
            dists.append(distribution)
            self._ss.undo()

        r_dist = self._aggregate_distributions(cnts, dists)
        r_dist.appendleft(base)

        return r_dist     

    def _best_distr(self, depth: int) -> deque[Decimal]:
        if (base_res := get_base_word_and_distr(self._word_reducer, depth == 0)) is not None:
            return base_res[1]

        # candidate_guesses = self._candidate_guesser.get_candidate_guesses(list(trie.trie_words), solve_status)
        candidate_guesses = range(len(self._word_reducer._all_words))
        
        best_score = -1
        best_dist = None

        for i in candidate_guesses:
            dist = self._get_distr(i, depth)
            score = self._score_for_dist(dist)
            if score > best_score:
                best_dist = dist
                best_score = score

        return best_dist

    # depth will never be zero in this function
    def process_word(self, word_i: int, depth: int) -> Decimal:
        dist = self._get_distr(word_i, depth)
        return self._score_for_dist(dist)

    def update(self, update_id: int, word: str, res: GuessResult) -> str:
        if update_id == self._update_id:
            time.sleep(0.5)
            return self._id

        res_arr = to_res_arr(word, res)
        word_arr = self._word_reducer.get_guess_arr(word)
        self._ss.update(word_arr, res_arr)
        self._word_reducer.update()

        self._udpate_id = update_id
        return self._id

    def reset(self, reset_id: int) -> str:
        if reset_id == self._reset_id:
            time.sleep(0.5)
            return self._id
        
        self._ss = SolveStatusNp()
        self._word_reducer = WordReducer(self._words, self._ss)

        self._reset_id = reset_id
        return self._id
