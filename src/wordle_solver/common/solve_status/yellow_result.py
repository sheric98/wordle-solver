from dataclasses import dataclass
from typing import Iterable, Optional

from wordle_solver.common.solve_status.yellow_result_type import YellowResultType


@dataclass
class YellowResult:
    t: YellowResultType
    vals: Optional[Iterable[int]] = None