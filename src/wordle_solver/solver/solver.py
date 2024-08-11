from typing import Callable, Optional

from wordle_solver.analyzer.analyzer import Analyzer
from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.common.single_result import SingleResult
from wordle_solver.util.constants import WORD_LENGTH
from wordle_solver.util.utils import read_all_words, get_best_starting_word


def _read_input(user_input_str: str) -> Optional[list[SingleResult]]:
    cleaned = user_input_str.strip()

    split = cleaned.split(' ')
    if len(split) != WORD_LENGTH:
        print(f'Input needs to be {WORD_LENGTH} colors...')
        return None
    converted = [SingleResult.from_string(s) for s in split]
    if any(res is None for res in converted):
        return None
    
    return converted


def _get_input() -> list[SingleResult]:
    ret = None

    while ret is None:
        ret = _read_input(input('What are the results?\n'))

    return ret


class Solver:
    def __init__(self, candidate_guesser_builder: Callable[[], CandidateGuesser], num_processes: int, use_computed_start: bool = True, max_search_depth: Optional[int] = None):
        self._all_words = read_all_words()
        word = None
        if use_computed_start:
            word = get_best_starting_word()

        self._analyzer = Analyzer(candidate_guesser_builder, self._all_words, word, num_processes, max_search_depth)

    def play(self):
        while True:
            best_word = self._analyzer.get_best_guess()

            print(f'You should guess: {best_word}')

            result = _get_input()
            if all(single == SingleResult.GREEN for single in result):
                print(f'Great win!')
                return
            
            self._analyzer.update(result)
