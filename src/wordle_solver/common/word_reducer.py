from functools import reduce
import numpy as np
from decimal import Decimal

from wordle_solver.common.solve_status.solve_status_np import SolveStatusNp
from wordle_solver.common.word_reducer_constants import DIG_CAP, GUARANTEED, YELLOW
from wordle_solver.util.constants import WORD_LENGTH, ALPHABET_LETTERS
from wordle_solver.util.word_utils import convert_word, convert_word_sparse
from wordle_solver.util.utils import get_word_frequencies

ALPHABET_IDXS = np.arange(ALPHABET_LETTERS, dtype=np.uint8)
RES_DIGS = np.array([np.power(DIG_CAP, i) for i in range(WORD_LENGTH)])
RES_MODS = np.array([np.power(DIG_CAP, i + 1) for i in range(WORD_LENGTH)])
ORDERED_ARRS = np.array([(i % RES_MODS) // RES_DIGS for i in range(np.power(DIG_CAP, WORD_LENGTH))])

NE_BOUND = ALPHABET_LETTERS // 2

DEFAULT_FREQUENCY = 100


def _get_single_arr_valid(i: int, arr: np.ndarray, mat: np.ndarray) -> np.ndarray:
    if np.sum(arr) >= NE_BOUND:
        return reduce(np.logical_and, (mat[:, i] != v for v in ALPHABET_IDXS[~arr]))
    else:
        return reduce(np.logical_or, (mat[:, i] == v for v in ALPHABET_IDXS[arr]))


def _get_complete_word_frequencies(all_words: list[str]) -> dict[str, int]:
    word_frequencies = get_word_frequencies()
    for word in all_words:
        if word not in word_frequencies:
            word_frequencies[word] = DEFAULT_FREQUENCY

    return word_frequencies


def _get_score_from_frequency(freq: int) -> float:
    return np.log10(freq)


def _multiply_along_axis(A: np.ndarray, B: np.ndarray, axis: int) -> np.ndarray:
    return np.swapaxes(np.swapaxes(A, axis, -1) * B, -1, axis)


def _divide_along_axis(A: np.ndarray, B: np.ndarray, axis: int) -> np.ndarray:
    return np.swapaxes(np.swapaxes(A, axis, -1) / B, -1, axis)


class WordReducer:
    def __init__(self, words: list[str], solve_status: SolveStatusNp):
        freq_dict = _get_complete_word_frequencies(words)
        self._idxs = {word: i for i, word in enumerate(words)}
        self._ss = solve_status
        self._valid_idxs = [np.arange(len(words))]
        self._valid_stack = [np.ones(len(words), dtype=np.bool)]
        self._frequencies_stack = [np.array([freq_dict[word] for word in words])]
        self._ans_scores_stack = [np.array([_get_score_from_frequency(freq) for freq in self._frequencies_stack[0]])]
        self._all_words = np.array(words, dtype='U5')
        self._words_stack = [self._all_words]
        self._full_words_arr = np.array([convert_word(word) for word in words], dtype=np.uint8)
        self._words_arr_stack: list[np.ndarray] = [self._full_words_arr]
        self._full_sparse_words = np.array([convert_word_sparse(word) for word in words], dtype=np.bool)
        self._sparse_words_stack = [self._full_sparse_words]
        self._full_char_counts = np.sum(self._sparse_words_stack[0], axis=1, dtype=np.uint8)
        self._char_counts_stack: list[np.ndarray] = [self._full_char_counts]

    def is_valid(self, i: int) -> bool:
        return self._valid_stack[-1][i]

    def get_guess_arr(self, word: str) -> np.ndarray:
        return self._full_words_arr[self._idxs[word]]

    def num_answers(self) -> int:
        return self._words_stack[-1].shape[0]
    
    def get_arbitrary_word(self) -> str:
        return self._words_stack[-1][0]

    def get_guess_distr_and_counts(self, i: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        guess_arr, ret = self._get_guess_distr(i)

        cnts = np.bincount(np.sum(ret * RES_DIGS, axis=1, dtype=np.uint16), minlength=len(ORDERED_ARRS), weights=self._ans_scores_stack[-1])
        nonzero = cnts != 0
        return guess_arr, ORDERED_ARRS[nonzero], cnts[nonzero]
    
    def get_top_freq(self) -> tuple[Decimal, str]:
        frequencies = self._frequencies_stack[-1]
        tot = np.sum(frequencies)
        highest_idx = np.argmax(frequencies)
        highest = frequencies[highest_idx]

        return Decimal(highest.item()) / Decimal(tot.item()), self._words_stack[-1][highest_idx]

    def get_top_candidates(self) -> list[int]:
        char_scores = self._get_char_scores()
        full_candidates = self._get_top_scores_mat(self._full_sparse_words, char_scores, 85)
        curr_idxs = self._get_top_scores_mat(self._sparse_words_stack[-1], char_scores, 5)
        curr_candidates = self._valid_idxs[-1][curr_idxs]

        # most likely answers
        likely_candidates = self._valid_idxs[-1][self._get_top_from_1d(self._frequencies_stack[-1], 10)]

        ret = set()
        ret.update(full_candidates)
        ret.update(curr_candidates)
        ret.update(likely_candidates)

        print(self._all_words[full_candidates])
        print(self._all_words[curr_candidates])
        print(self._all_words[likely_candidates])

        return list(ret)
        # return list(range(len(self._all_words)))

    def try_update(self):
        idxs = self._get_word_idxs()

        invalid_idxs = self._valid_idxs[-1][~idxs]
        new_valids = self._valid_stack[-1].copy()
        new_valids[invalid_idxs] = False
        self._valid_stack.append(new_valids)

        self._valid_idxs.append(self._valid_idxs[-1][idxs])
        self._frequencies_stack.append(self._frequencies_stack[-1][idxs])
        self._ans_scores_stack.append(self._ans_scores_stack[-1][idxs])
        self._words_stack.append(self._words_stack[-1][idxs])
        self._words_arr_stack.append(self._words_arr_stack[-1][idxs])
        self._sparse_words_stack.append(self._sparse_words_stack[-1][idxs])
        self._char_counts_stack.append(self._char_counts_stack[-1][idxs])

    def update(self):
        self.try_update()
        
        self._valid_stack = [self._valid_stack[-1]]
        self._valid_idxs = [self._valid_idxs[-1]]
        self._frequencies_stack = [self._frequencies_stack[-1]]
        self._ans_scores_stack = [self._ans_scores_stack[-1]]
        self._words_stack = [self._words_stack[-1]]
        self._words_arr_stack = [self._words_arr_stack[-1]]
        self._sparse_words_stack = [self._sparse_words_stack[-1]]
        self._char_counts_stack = [self._char_counts_stack[-1]]

    def undo(self):
        self._valid_stack.pop()
        self._valid_idxs.pop()
        self._frequencies_stack.pop()
        self._ans_scores_stack.pop()
        self._words_stack.pop()
        self._words_arr_stack.pop()
        self._sparse_words_stack.pop()
        self._char_counts_stack.pop()

    def _get_top_from_1d(self, arr: np.ndarray, num_top: int) -> np.ndarray:
        if len(arr) <= num_top:
            return np.arange(len(arr))
        return np.argpartition(-arr, num_top)[:num_top]

    def _get_top_scores_mat(self, mat: np.ndarray, char_scores: np.ndarray, num_top) -> np.ndarray:
        if num_top >= mat.shape[0]:
            return np.arange(mat.shape[0])
        score_mat = self._get_scored_mat(mat, char_scores)
        return np.argpartition(-score_mat, num_top)[:num_top]

    def _get_scored_mat(self, mat: np.ndarray, char_scores: np.ndarray) -> np.ndarray:
        return np.sum(mat * char_scores, axis=(1, 2))
        
    def _get_char_scores(self) -> np.ndarray:
        total_counts = np.sum(self._sparse_words_stack[-1], axis=0)
        inverted = len(self._sparse_words_stack[-1]) - total_counts


        raw = np.sum(_multiply_along_axis(self._sparse_words_stack[-1], self._ans_scores_stack[-1], 0), axis=0)
        probs = _divide_along_axis(raw, np.sum(raw, axis=1), 0)

        return probs * total_counts + inverted * (1 - probs)
    
    def _get_word_idxs(self) -> np.ndarray:
        reduced_idxs = (self._get_lowers_check()) & (self._get_capped_check())
        nested_reduction = self._get_valid_check(reduced_idxs)
        reduced_idxs[np.where(reduced_idxs)[0][~nested_reduction]] = False

        return reduced_idxs
    
    def _get_valid_check(self, reduced_idxs: np.ndarray) -> np.ndarray:
        valids = self._ss.get_valids()
        
        mat = self._words_arr_stack[-1][reduced_idxs]
        return reduce(np.logical_and, (_get_single_arr_valid(i, arr, mat) for i, arr in enumerate(valids)))
    
    def _get_lowers_check(self) -> np.ndarray:
        lowers = self._ss.get_lowers()
        return np.all(self._char_counts_stack[-1] >= lowers, axis=1)
    
    def _get_capped_check(self) -> np.ndarray:
        capped = self._ss.get_capped()
        capped_idxs = capped > 0
        return np.all(self._char_counts_stack[-1][:, capped_idxs] == capped[capped_idxs], axis=1)
    
    def _get_guess_distr(self, i: int) -> tuple[np.ndarray, np.ndarray]:
        guess_arr = self._full_words_arr[i]
        guess_counts = self._full_char_counts[i][guess_arr]
        matching = self._words_arr_stack[-1] == guess_arr
        char_counts_guess = self._char_counts_stack[-1][:, guess_arr]
        
        distr = matching * GUARANTEED + ((~matching) & (char_counts_guess > 0) & (char_counts_guess >= guess_counts)) * YELLOW + ((~matching) & (char_counts_guess > 0) & (char_counts_guess < guess_counts)) * char_counts_guess

        return guess_arr, distr
