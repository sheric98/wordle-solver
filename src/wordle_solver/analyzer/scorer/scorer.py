from collections import Counter, defaultdict, deque
from decimal import Decimal
from tqdm import tqdm
from typing import Any, Iterable, Optional

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.common.word_reducer import WordReducer
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.solve_status.solve_status_np import SolveStatusNp

GUESS_THRESHOLD = Decimal('0.8')


def get_results(ans: str, guess: str) -> tuple[tuple[SingleResult, ...], tuple[tuple[SingleResult, int, str], ...]]:
    ret = []
    counts = Counter(ans)
    for i, (ans_c, guess_c) in enumerate(zip(ans, guess)):
        if ans_c == guess_c:
            counts[ans_c] -= 1
            if counts[ans_c] == 0:
                del counts[ans_c]

    for i, (ans_c, guess_c) in enumerate(zip(ans, guess)):
        if ans_c == guess_c:
            color = SingleResult.GREEN
        elif guess_c in counts:
            counts[guess_c] -= 1
            if counts[guess_c] == 0:
                del counts[guess_c]
            color = SingleResult.YELLOW
        else:
            color = SingleResult.GRAY

        ret.append(color)

    return tuple(ret)


class Scorer:
    def __init__(
            self,
            word_reducer: WordReducer,
            solve_status: SolveStatusNp,
            candidate_guesser: CandidateGuesser,
            full_words: list[str],
            max_search_depth: int,
            max_guesses: int,
            curr_guesses: int = 0,
            progress_bar: bool = True):
        
        self._word_reducer = word_reducer
        self._ss = solve_status
        self._candidate_guesser = candidate_guesser
        self._full_words = full_words
        self._max_search_depth = max_search_depth
        self._max_guesses = max_guesses
        self._curr_guesses = curr_guesses
        self._progress_bar = progress_bar

    def get_best_word(self):
        print(self._word_reducer.num_answers())
        res, _ = self._get_best_word(show_progress=self._progress_bar)
        self._curr_guesses += 1

        return res

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

    def _get_score_word(self, curr_search_depth: int, guess_i: int, outer_cache: dict[Any, deque[Decimal]]) -> deque[Decimal]:
        if self._word_reducer.is_valid(guess_i):
            base = Decimal(1) / Decimal(self._word_reducer.num_answers())
        else:
            base = Decimal(0)

        guess_arr, res_arrs, cnts = self._word_reducer.get_guess_distr_and_counts(guess_i)
        
        dists = []
        for res_arr in res_arrs:
            self._ss.try_add_word(guess_arr, res_arr)
            key = self._ss.key()
            if key not in outer_cache:
                self._word_reducer.try_update()
                distribution = self._get_distribution(curr_search_depth + 1)
                self._word_reducer.undo()
                outer_cache[key] = distribution

            dists.append(outer_cache[key])
            self._ss.undo()

        r_dist = self._aggregate_distributions(cnts, dists)
        r_dist.appendleft(base)

        return r_dist

    def _get_best_word(
            self,
            curr_search_depth: int = 0,
            show_progress = True) -> tuple[str, deque[Decimal]]:
        
        total_depth = self._curr_guesses + curr_search_depth
        remaining_guesses = self._max_guesses - total_depth
        num_answers = self._word_reducer.num_answers()
        if num_answers == 1:
            return self._word_reducer.get_arbitrary_word(), deque([Decimal(1) / Decimal(num_answers)])
        
        highest_freq, highest_word = self._word_reducer.get_top_freq()
        if curr_search_depth == self._max_search_depth or remaining_guesses == 1 or highest_freq > GUESS_THRESHOLD:
            return highest_word, deque([highest_freq])

        # candidate_guesses = self._candidate_guesser.get_candidate_guesses(trie.trie_words, solve_status)
        candidate_guesses = enumerate(self._word_reducer._all_words)

        best_word = None
        best_score = -1
        best_dist = None
        cache = {}
        if show_progress:
            itr = tqdm(list(candidate_guesses))
        else:
            itr = candidate_guesses
        for i, word in itr:
            dist = self._get_score_word(curr_search_depth, i, cache)
            score = self._score_for_dist(dist)
            if score > best_score:
                best_word = word
                best_dist = dist
                best_score = score

        return best_word, best_dist

    def _get_distribution(self, curr_search_depth: int) -> Optional[deque[Decimal]]:
        _, prior_distribution = self._get_best_word(curr_search_depth, False)
        return prior_distribution.copy()
