from tqdm import tqdm
from typing import Callable, Optional
import traceback

from wordle_solver.analyzer.analyzer import Analyzer
from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.common.guess_result import get_guess_result
from wordle_solver.common.single_result import SingleResult
from wordle_solver.util.constants import NUMBER_OF_GUESSES
from wordle_solver.util.utils import read_all_words, get_best_starting_word, get_previous_answers


class Executor:
    def __init__(self, candidate_guesser_builder: Callable[[], CandidateGuesser], num_processes: int):
        self._all_words = read_all_words()
        self._starting_word = get_best_starting_word()
        self._previous_answers = get_previous_answers()
        self._candidate_guesser_builder = candidate_guesser_builder
        self._analyzer = Analyzer(self._candidate_guesser_builder, self._all_words, self._starting_word, num_processes, max_search_depth=1, progress_bar=False)

    def execute(self):
        cache = {}

        solved_guesses_taken = []
        failed = []

        for answer in tqdm(self._previous_answers):
            res = self._execute_single(answer, cache)
            if res is not None:
                solved_guesses_taken.append(res)
            else:
                failed.append(answer)

        solve_percent = len(solved_guesses_taken) / len(self._previous_answers)
        print(f'Able to solve {solve_percent * 100}% of previous answers within {NUMBER_OF_GUESSES} guesses')
        if solved_guesses_taken:
            print(f'Took an average of {sum(solved_guesses_taken) / len(solved_guesses_taken)} guesses per correct answer')
        if failed:
            print(f'Failed to solve {failed}')

    def _execute_single(self, answer: str, cache: dict[tuple[tuple[str, tuple[SingleResult, ...]], ...], str]) -> Optional[int]:
        try:
            return self._execute_single_uncaught(answer, cache)
        except Exception as e:
            print(f'Caught exception while trying to solve {answer}. Skipping...')
            print(traceback.format_exc())
            return None
        finally:
            self._analyzer.reset()

    def _execute_single_uncaught(self, answer: str, cache: dict[tuple[tuple[str, tuple[SingleResult, ...]], ...], str]) -> Optional[int]:
        curr_answers = []

        while len(curr_answers) < NUMBER_OF_GUESSES:
            key = tuple(curr_answers)
            if key not in cache:
                cache[key] = self._analyzer.get_best_guess()

            curr_guess = cache[key]

            res = get_guess_result(curr_guess, answer)
            curr_answers.append((curr_guess, tuple(res)))

            if all(single == SingleResult.GREEN for single in res):
                return len(curr_answers)
            
            self._analyzer.update(res, curr_guess)
            
        return None

    def _build_analyzer(self) -> Analyzer:
        return Analyzer(self._candidate_guesser_builder, self._all_words, self._starting_word, max_search_depth=1, progress_bar=False)