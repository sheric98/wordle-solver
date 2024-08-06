from decimal import Decimal
from math import log
from typing import Iterable, Optional

from wordle_solver.util.utils import get_word_frequencies

LOG_BASE = 10
DEFAULT_FREQUENCY = 100

GUESS_THRESHOLD = Decimal('0.8')


def _get_complete_word_frequencies(all_words: list[str]) -> dict[str, int]:
    word_frequencies = get_word_frequencies()
    for word in all_words:
        if word not in word_frequencies:
            word_frequencies[word] = DEFAULT_FREQUENCY

    return word_frequencies


class FrequencyWeigher:
    def __init__(self, all_words: list[str]):
        self._word_frequencies = _get_complete_word_frequencies(all_words)
        self._word_weights = self._get_word_weights()

    def get_guess(self, candidate_ans: Iterable[str], always_return=False) -> tuple[Optional[str], Optional[Decimal]]:
        tot = 0
        
        best_cnt = -1
        best_word = None
        for word in candidate_ans:
            cnt = self._word_frequencies[word]
            tot += cnt
            if cnt > best_cnt:
                best_word = word
                best_cnt = cnt

        highest_freq = Decimal(best_cnt) / Decimal(tot)
        if highest_freq > GUESS_THRESHOLD or always_return:
            return best_word, highest_freq
        else:
            return None, None

    def get_weight(self, word: str) -> Decimal:
        # return self._word_weights[word]
        return 1

    def _get_word_weights(self) -> dict[str, Decimal]:
        return {word: Decimal(log(cnt, LOG_BASE)) for word, cnt in self._word_frequencies.items()}
