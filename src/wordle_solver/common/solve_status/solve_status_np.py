import numpy as np
from typing import Any

from wordle_solver.common.word_reducer_constants import GUARANTEED, YELLOW
from wordle_solver.util.constants import WORD_LENGTH, ALPHABET_LETTERS


LOWERS_DIGS = np.array([np.power(WORD_LENGTH, i)] for i in range(ALPHABET_LETTERS))


class SolveStatusNp:
    def __init__(self):
        self._valids_stack = [np.ones((WORD_LENGTH, ALPHABET_LETTERS), dtype=np.bool)]
        self._lowers_stack = [np.zeros(ALPHABET_LETTERS, dtype=np.uint8)]
        self._capped_stack = [np.zeros(ALPHABET_LETTERS, dtype=np.uint8)]
    
    def get_valids(self) -> np.ndarray:
        return self._valids_stack[-1]
    
    def get_lowers(self) -> np.ndarray:
        return self._lowers_stack[-1]
    
    def get_capped(self) -> np.ndarray:
        return self._capped_stack[-1]
    
    def key(self) -> Any:
        return np.concatenate((np.packbits(self._valids_stack[-1]), self._lowers_stack[-1], self._capped_stack[-1])).tobytes()

    def update(self, guess_arr: np.ndarray, res_arr: np.ndarray):
        valids, lowers, capped = self._add_word(guess_arr, res_arr)
        self._valids_stack = [valids]
        self._lowers_stack = [lowers]
        self._capped_stack = [capped]

    def try_add_word(self, guess_arr: np.ndarray, res_arr: np.ndarray):
        valids, lowers, capped = self._add_word(guess_arr, res_arr)
        self._valids_stack.append(valids)
        self._lowers_stack.append(lowers)
        self._capped_stack.append(capped)

    def undo(self):
        self._valids_stack.pop()
        self._lowers_stack.pop()
        self._capped_stack.pop()

    def _add_word(self, guess_arr: np.ndarray, res_arr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        valids = self._valids_stack[-1].copy()
        lowers = self._lowers_stack[-1].copy()
        capped = self._capped_stack[-1].copy()

        uncertains = (res_arr > 0) & (res_arr < GUARANTEED)
        valids[:, guess_arr[res_arr == 0]] = False
        valids[uncertains, guess_arr[uncertains]] = False
        valids[res_arr == GUARANTEED, :] = False
        valids[res_arr == GUARANTEED, guess_arr[res_arr == GUARANTEED]] = True

        capped_idxs = (res_arr > 0) & (res_arr < YELLOW)
        lowers = np.maximum(lowers, np.bincount(guess_arr[res_arr == YELLOW], minlength=ALPHABET_LETTERS))
        capped[guess_arr[capped_idxs]] = res_arr[capped_idxs]

        return valids, lowers, capped
