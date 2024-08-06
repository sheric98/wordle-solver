from collections import Counter, defaultdict, deque
from decimal import Decimal
import time
from uuid import uuid4

from wordle_solver.analyzer.frequency_weigher import FrequencyWeigher
from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.common.guess_result import GuessResult
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.trie import Trie

_CHILD = None


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


def init_scorer_child(words: list[str]):
    global _CHILD
    _CHILD = ScorerChild(words)


def process(word: str, depth: int):
    _CHILD.process_word(word, depth)


def update(update_id: int, res: GuessResult) -> str:
    return _CHILD.update(update_id, res)


def reset(reset_id: int) -> str:
    return _CHILD.reset(reset_id)


class ScorerChild:
    def __init__(self, words: list[str]):
        self._words = words
        self._frequency_weigher = FrequencyWeigher(words)
        self._trie = Trie(words)
        self._solve_status = SolveStatus()
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

    def _get_distr(self, word: str, trie: Trie, solve_status: SolveStatus, depth: int) -> deque[Decimal]:
        if word in trie.trie_words:
            base = Decimal(0)
        else:
            base = Decimal(1) / Decimal(trie.trie_size)
        
        cache_weights: dict[tuple[SingleResult, ...], int] = defaultdict(lambda: Decimal(0))
        cache_to_dist: dict[tuple[SingleResult, ...], deque[Decimal]] = {}

        for ans in trie.trie_words:
            res = get_results(ans, word)
            cache_weights[res] += self._frequency_weigher.get_weight(ans)
            if res in cache_to_dist:
                continue
            
            ss = solve_status.copy()
            ss.add_results(word, res)
            # key = ss.tup()
            # if key not in outer_cache:
            #     new_words = trie.get_words(ss)
            #     if not new_words:
            #         print(ss._guessed_words)
            #         print(ss.greens)
            #         print(ss.must_not_contain)
            #         print(ss._yellows)
            #         print(f'Failed to get words for guess {guess} answer {ans}')

            #     distribution = self._get_distribution(curr_search_depth + 1, Trie(new_words), ss)
            #     outer_cache[key] = distribution

            new_words = trie.get_words(ss)
            _, distribution = self._best_word_and_distr(Trie(new_words), ss, depth - 1)

            cache_to_dist[res] = distribution


        r_dist = self._aggregate_distributions(cache_weights, cache_to_dist)
        r_dist.appendleft(base)

        return r_dist        

    def _best_word_and_distr(self, trie: Trie, solve_status: SolveStatus, depth: int) -> tuple[str, deque[Decimal]]:
        if trie.trie_size == 1:
            return next(iter(trie.trie_words)), deque([Decimal(1) / Decimal(trie.trie_size)])
        
        highest_freq_word, freq = self._frequency_weigher.get_guess(trie.trie_words, depth == 0)
        if highest_freq_word is not None:
            return highest_freq_word, deque([freq])
        
        # candidate_guesses = self._candidate_guesser.get_candidate_guesses(list(trie.trie_words), solve_status)
        candidate_guesses = trie.trie_words
        
        best_word = None
        best_score = -1
        best_dist = None

        for word in candidate_guesses:
            dist = self._get_distr(word, trie, solve_status, depth)
            score = self._score_for_dist(dist)
            if score > best_score:
                best_word = word
                best_dist = dist
                best_score = score

        return best_word, best_dist

    # depth will never be zero in this function
    def process_word(self, word: str, depth: int) -> Decimal:
        dist = self._get_distr(word, self._trie, self._solve_status, depth)
        return self._score_for_dist(dist)

    def update(self, update_id: int, res: GuessResult) -> str:
        if update_id == self._update_id:
            time.sleep(0.5)
            return self._id

        self._solve_status.add_results(res[0], res[1])
        self._trie = Trie(self._trie.get_words(self._solve_status))

        self._udpate_id = update_id
        return self._id

    def reset(self, reset_id: int) -> str:
        if reset_id == self._reset_id:
            time.sleep(0.5)
            return self._id
        
        self._trie = Trie(self._words)
        self._solve_status = SolveStatus()

        self._reset_id = reset_id
        return self._id
