from typing import Iterable, Optional, Self

from wordle_solver.common.solve_status.yellow_result import YellowResult
from wordle_solver.common.solve_status.yellow_result_type import YellowResultType
from wordle_solver.util.constants import WORD_LENGTH


class YellowStatus:
    def __init__(self, c: str, idxs: list[int], capped: bool):
        self.c = c
        self.cnt = len(idxs)
        self.is_capped = capped
        self.seen_idxs = set(idxs)
        self.possible_idxs = set(range(WORD_LENGTH)) - self.seen_idxs

    def update_seen(self, idxs: Iterable[int], capped: bool):
        cnt = len(idxs)
        if capped:
            self.is_capped = True
        if cnt > self.cnt or capped:
            self.cnt = cnt

        for i in idxs:
            self.seen_idxs.add(i)
            self.possible_idxs.discard(i)

    def add_guaranteed(self, idx: int):
        if idx in self.possible_idxs:
            self.possible_idxs.remove(idx)
            self.cnt -= 1
            self.cnt = max(0, self.cnt)

    def try_consolidate(self) -> Optional[YellowResult]:
        if self.cnt == 0:
            if self.is_capped:
                return YellowResult(t=YellowResultType.GUARANTEED)
            else:
                return YellowResult(t=YellowResultType.ANY)

        else:
            if self.cnt == len(self.possible_idxs):
                return YellowResult(t=YellowResultType.GUARANTEED, vals=self.possible_idxs)

        return None
    
    def __repr__(self) -> str:
        return str((self.c, self.cnt, self.is_capped, self.seen_idxs, self.possible_idxs))
    
    def copy(self) -> Self:
        ret = YellowStatus(self.c, [], self.is_capped)
        ret.cnt = self.cnt
        ret.seen_idxs = self.seen_idxs.copy()
        ret.possible_idxs = self.possible_idxs.copy()

        return ret
