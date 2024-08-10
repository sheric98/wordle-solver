from typing import Callable, Optional

from wordle_solver.analyzer.candidate_guess.answer_only_guesser import AnswerOnlyGuesser
from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.analyzer.candidate_guess.common_chars_guesser import CommonCharsGuesser
from wordle_solver.analyzer.candidate_guess.guesser_type import GuesserType
from wordle_solver.analyzer.candidate_guess.no_guesser import NoGuesser
from wordle_solver.analyzer.candidate_guess.unused_chars_guesser import UnusedCharsGuesser


class CandidateGuesserFactory:
    def __init__(self, guess_type: GuesserType, num_common_chars: Optional[int], num_candidate_guesses: Optional[int]):
        self._guess_type = guess_type
        self._num_common_chars = num_common_chars
        self._num_candidate_guesses = num_candidate_guesses

    def build(self) -> Callable[[], CandidateGuesser]:
        if self._guess_type == GuesserType.NoGuess:
            return NoGuesser
        elif self._guess_type == GuesserType.AnswerGuess:
            return AnswerOnlyGuesser
        elif self._guess_type == GuesserType.CommonChars:
            if self._num_common_chars is None:
                raise TypeError(f'Need to specify num common characters for Common Char Guessing Strategy')
            return lambda t: CommonCharsGuesser(t, self._num_common_chars)
        elif self._guess_type == GuesserType.UnusedChars:
            if self._num_candidate_guesses is None:
                raise TypeError('Need to specify num candidate guesses for unused chars strategy')
            return lambda t: UnusedCharsGuesser(t, self._num_candidate_guesses)
        else:
            raise TypeError('Unsupported candidate guessing strategy')
