from typing import Iterable

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser


class AnswerOnlyGuesser(CandidateGuesser):
    def _get_analytical_guesses(self, candidate_ans: Iterable[str], solve_status) -> set[str]:
        return set(candidate_ans)
