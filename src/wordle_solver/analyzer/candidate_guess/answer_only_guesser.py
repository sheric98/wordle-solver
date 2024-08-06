from typing import Iterable

from wordle_solver.analyzer.candidate_guess.candidate_guesser import CandidateGuesser
from wordle_solver.common.solve_status.solve_status import SolveStatus


class AnswerOnlyGuesser(CandidateGuesser):
    def _get_analytical_guesses(self, candidate_ans: Iterable[str], solve_status: SolveStatus) -> set[str]:
        return set(candidate_ans)
