from tqdm import tqdm
from typing import Callable, Optional

from wordle_solver.analyzer.analyzer import Analyzer
from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.analyzer.scorer.scorer import get_results
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.trie import Trie
from wordle_solver.util.constants import NUMBER_OF_GUESSES
from wordle_solver.util.utils import read_all_words, get_best_starting_word, get_previous_answers


class Executor:
    def __init__(self, candidate_guesser_builder: Callable[[Trie], CandidateGuesser]):
        self._all_words = read_all_words()
        self._starting_word = get_best_starting_word()
        self._previous_answers = get_previous_answers()
        self._candidate_guesser_builder = candidate_guesser_builder

    def execute(self):
        cache = {}

        solved_guesses_taken = []

        for answer in tqdm(self._previous_answers):
            res = self._execute_single(answer, cache)
            if res is not None:
                solved_guesses_taken.append(res)

        solve_percent = len(solved_guesses_taken) / len(self._previous_answers)
        print(f'Able to solve {solve_percent * 100}% of previous answers within {NUMBER_OF_GUESSES} guesses')
        if solved_guesses_taken:
            print(f'Took an average of {sum(solved_guesses_taken) / len(solved_guesses_taken)} guesses per correct answer')

    def _execute_single(self, answer: str, cache: dict[tuple[tuple[str, tuple[SingleResult, ...]], ...], str]) -> Optional[int]:
        try:
            return self._execute_single_uncaught(answer, cache)
        except Exception:
            print(f'Caught exception while trying to solve {answer}. Skipping...')
            return None

    def _execute_single_uncaught(self, answer: str, cache: dict[tuple[tuple[str, tuple[SingleResult, ...]], ...], str]) -> Optional[int]:

        curr_answers = []

        analyzer = self._build_analyzer()

        while len(curr_answers) < NUMBER_OF_GUESSES:
            key = tuple(curr_answers)
            if key not in cache:
                cache[key] = analyzer.get_best_guess()

            curr_guess = cache[key]

            res = get_results(answer, curr_guess)
            curr_answers.append((curr_guess, res))

            if all(single == SingleResult.GREEN for single in res):
                return len(curr_answers)
            
            analyzer.update(res, curr_guess)
            
        return None

    def _build_analyzer(self) -> Analyzer:
        return Analyzer(self._candidate_guesser_builder, self._all_words, self._starting_word, 1, progress_bar=False)