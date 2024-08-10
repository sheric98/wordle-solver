from wordle_solver.util.constants import ALPHABET_LETTERS


def convert_char(c: str) -> int:
    return ord(c) - ord('a')


def convert_word(word: str) -> list[int]:
    return [convert_char(c) for c in word]


def convert_char_sparse(c: str) -> list[int]:
    ret = [0] * ALPHABET_LETTERS
    ret[convert_char(c)] = 1

    return ret


def convert_word_sparse(word: str) -> list[list[int]]:
    return [convert_char_sparse(c) for c in word]
