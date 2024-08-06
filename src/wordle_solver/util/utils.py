import os
from typing import Optional

from wordle_solver.util.constants import ALL_WORDS_PATH, BEST_STARTING_WORD_PATH, PREVIOUS_ANSWERS_PATH, WORD_SCORES_PATH, WORD_FREQUENCIES_PATH


def read_all_words() -> list[str]:
    ret = []
    
    with open(ALL_WORDS_PATH, 'r') as f:
        for line in f:
            ret.append(line.strip())

    return ret


def read_word_scores() -> dict[str: int]:
    ret = {}
    with open(WORD_SCORES_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            word, score_str = line.split(' ')
            score = int(score_str)

            ret[word] = score

    return ret


def get_best_starting_word() -> Optional[str]:
    if not os.path.isfile(BEST_STARTING_WORD_PATH):
        return None
    
    with open(BEST_STARTING_WORD_PATH, 'r') as f:
        word = f.read().strip()

    if not word:
        return None
    
    return word


def get_word_frequencies() -> dict[str, int]:
    ret = {}

    with open(WORD_FREQUENCIES_PATH, 'r') as f:
        for line in f:
            word, cnt_str = line.strip().split()
            ret[word] = int(cnt_str)

    return ret


def get_previous_answers() -> list[str]:
    ret = []
    with open(PREVIOUS_ANSWERS_PATH, 'r') as f:
        for line in f:
            ret.append(line.strip())

    return ret
