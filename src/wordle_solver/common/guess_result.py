from collections import defaultdict
import numpy as np

from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.word_reducer_constants import GUARANTEED, YELLOW
from wordle_solver.util.constants import WORD_LENGTH

type GuessResult = tuple[str, list[SingleResult]]


def to_res_arr(guess: str, res: GuessResult) -> np.ndarray:
    ret = np.zeros(WORD_LENGTH, dtype=np.uint8)
    grays = set()
    yellows = defaultdict(lambda: 0)
    greens = defaultdict(lambda: 0)

    for c, r in zip(guess, res):
        if r == SingleResult.GREEN:
            greens[c] += 1
        elif r == SingleResult.YELLOW:
            yellows[c] += 1
        else:
            grays.add(c)

    capped = {}
    for c in grays:
        if c in yellows or c in greens:
            capped[c] = yellows[c] + greens[c]

    for i, (c, r) in enumerate(zip(guess, res)):
        if r == SingleResult.GREEN:
            ret[i] = GUARANTEED
        elif c in capped:
            ret[i] = capped[c]
        elif r == SingleResult.YELLOW:
            ret[i] = YELLOW

    return ret
