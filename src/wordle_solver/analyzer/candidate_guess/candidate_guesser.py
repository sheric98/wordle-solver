from abc import ABC, abstractmethod
from typing import Iterable

from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.common.trie import Trie

CANDIDATE_ANS_LOW_THRESH = 10


class CandidateGuesser(ABC):
    def __init__(self, full_trie: Trie):
        self._trie = full_trie

    def get_candidate_guesses(self, candidate_ans: Iterable[str], solve_status: SolveStatus) -> Iterable[str]:
        ret = self._get_analytical_guesses(candidate_ans, solve_status)

        if not ret or len(candidate_ans) < CANDIDATE_ANS_LOW_THRESH:
            ret.update(candidate_ans)
        
        return ret
    
    @abstractmethod
    def _get_analytical_guesses(self, candidate_ans: Iterable[str], solve_status: SolveStatus) -> set[str]:
        pass
