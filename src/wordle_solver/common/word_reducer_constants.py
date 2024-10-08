import numpy as np

from wordle_solver.util.constants import WORD_LENGTH


DIG_CAP = WORD_LENGTH + 2
GUARANTEED = DIG_CAP - 1
YELLOW = GUARANTEED - 1

SOLVED = np.array([GUARANTEED] * WORD_LENGTH)
