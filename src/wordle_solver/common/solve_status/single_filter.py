from dataclasses import dataclass
from typing import Self

from wordle_solver.common.solve_status.single_filter_type import SingleFilterType


@dataclass
class SingleFilter:
    filter_type: SingleFilterType = SingleFilterType.ANY
    val: None | str | set[str] = None

    def make_guaranteed(self, c: str) -> bool:
        if self.filter_type == SingleFilterType.GUARANTEED:
            return False
        self.filter_type = SingleFilterType.GUARANTEED
        self.val = c

        return True

    def try_add_not(self, c: str):
        if self.filter_type == SingleFilterType.NOT:
            self.val.add(c)
        elif self.filter_type == SingleFilterType.ANY:
            self.filter_type = SingleFilterType.NOT
            self.val = {c}

    def copy(self) -> Self:
        if self.filter_type == SingleFilterType.NOT:
            new_val = self.val.copy()
        else:
            new_val = self.val
        return SingleFilter(filter_type=self.filter_type, val=new_val)
