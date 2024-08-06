from collections import Counter, defaultdict, deque
from decimal import Decimal
from tqdm import tqdm
from typing import Any, Optional

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.analyzer.frequency_weigher import FrequencyWeigher
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.common.trie import Trie


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
            candidate_guesser: CandidateGuesser,
            full_words: list[str],
            max_search_depth: int,
            max_guesses: int,
            curr_guesses: int = 0,
            progress_bar: bool = True):
        
        self._candidate_guesser = candidate_guesser
        self._full_words = full_words
        self._max_search_depth = max_search_depth
        self._max_guesses = max_guesses
        self._curr_guesses = curr_guesses
        self._frequency_weigher = FrequencyWeigher(self._full_words)
        self._progress_bar = progress_bar

    def get_best_word(self, trie: Trie, solve_status: SolveStatus):
        # print(trie.trie_size)
        res, _ = self._get_best_word(trie, solve_status, show_progress=self._progress_bar)
        self._curr_guesses += 1

        return res

    def _score_for_dist(self, probs: deque[Decimal]) -> Decimal:
        multiplier = Decimal(1)

        score = Decimal(0)
        for prob in probs:
            score += multiplier * prob
            multiplier /= Decimal(2)

        return score

    def _aggregate_distributions(self, weights: dict[tuple[SingleResult, ...], Decimal], distributions: dict[tuple[SingleResult, ...], deque[Decimal]]) -> deque[Decimal]:
        ret = deque()

        tot = Decimal(0)
        for res, dist in distributions.items():
            weight = weights[res]
            tot += weight
            for i, d in enumerate(dist):
                if i >= len(ret):
                    ret.append(Decimal(0))
                ret[i] += weight * d

        for i in range(len(ret)):
            ret[i] /= tot

        return ret

    def _get_score_word(self, curr_search_depth: int, guess: str, trie: Trie, solve_status: SolveStatus, outer_cache: dict[Any, deque[Decimal]]) -> deque[Decimal]:
        if guess in trie.trie_words:
            base = Decimal(0)
        else:
            base = Decimal(1) / Decimal(trie.trie_size)
        
        cache_weights: dict[tuple[SingleResult, ...], int] = defaultdict(lambda: Decimal(0))
        cache_to_dist: dict[tuple[SingleResult, ...], deque[Decimal]] = {}

        for ans in trie.trie_words:
            res = get_results(ans, guess)
            cache_weights[res] += self._frequency_weigher.get_weight(ans)
            if res in cache_to_dist:
                continue
            
            ss = solve_status.copy()
            ss.add_results(guess, res)
            key = ss.tup()
            if key not in outer_cache:
                new_words = trie.get_words(ss)
                if not new_words:
                    print(ss._guessed_words)
                    print(ss.greens)
                    print(ss.must_not_contain)
                    print(ss._yellows)
                    print(f'Failed to get words for guess {guess} answer {ans}')

                distribution = self._get_distribution(curr_search_depth + 1, Trie(new_words), ss)
                outer_cache[key] = distribution

            cache_to_dist[res] = outer_cache[key]


        r_dist = self._aggregate_distributions(cache_weights, cache_to_dist)
        r_dist.appendleft(base)

        return r_dist

    def _get_best_word(
            self,
            trie: Trie,
            solve_status: SolveStatus,
            curr_search_depth: int = 0,
            show_progress = True) -> tuple[str, deque[Decimal]]:
        
        total_depth = self._curr_guesses + curr_search_depth
        remaining_guesses = self._max_guesses - total_depth
        if trie.trie_size == 1:
            return next(iter(trie.trie_words)), deque([Decimal(1) / Decimal(trie.trie_size)])
        
        highest_freq_word, freq = self._frequency_weigher.get_guess(trie.trie_words, curr_search_depth == self._max_search_depth or remaining_guesses == 1)
        if highest_freq_word is not None:
            return highest_freq_word, deque([freq])

        candidate_guesses = self._candidate_guesser.get_candidate_guesses(list(trie.trie_words), solve_status)

        best_word = None
        best_score = -1
        best_dist = None
        cache = {}
        if show_progress:
            itr = tqdm(candidate_guesses)
        else:
            itr = candidate_guesses
        for word in itr:
            dist = self._get_score_word(curr_search_depth, word, trie, solve_status, cache)
            score = self._score_for_dist(dist)
            if score > best_score:
                best_word = word
                best_dist = dist
                best_score = score

        return best_word, best_dist

    def _get_distribution(self, curr_search_depth: int, trie: Trie, solve_status: SolveStatus) -> Optional[deque[Decimal]]:
        _, prior_distribution = self._get_best_word(trie, solve_status, curr_search_depth, False)
        return prior_distribution.copy()
