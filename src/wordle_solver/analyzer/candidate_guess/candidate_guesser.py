from abc import ABC, abstractmethod
from typing import Iterable

CANDIDATE_ANS_LOW_THRESH = 10


class CandidateGuesser(ABC):
    def __init__(self, full_trie):
        self._trie = full_trie

    def get_candidate_guesses(self, candidate_ans: Iterable[str], solve_status) -> Iterable[str]:
        ret = self._get_analytical_guesses(candidate_ans, solve_status)

        if len(ret) == 0 or len(candidate_ans) < CANDIDATE_ANS_LOW_THRESH:
            ret.update(candidate_ans)
        
        return ret
    
    @abstractmethod
    def _get_analytical_guesses(self, candidate_ans: Iterable[str], solve_status) -> set[str]:
        pass
