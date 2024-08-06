from typing import Any, Optional, Self

from wordle_solver.util.constants import WORD_LENGTH


class CharStatus:
    def __init__(self, unknowns: set[int]):
        self.count: int = 0
        self.known: set[int] = set()

        self.possible: set[int] = unknowns
        self.capped = False

    def __repr__(self) -> str:
        return f'CharStatus(count={self.count}, known={self.known}, possible={self.possible}, capped={self.capped})'
    
    def unknown_count(self) -> int:
        return self.count - len(self.known)

    def combine(self, other: Self) -> Optional[list[int]]:
        self.count = max(self.count, other.count)
        self.capped = self.capped or other.capped
        self.known.update(other.known)
        self.possible.intersection_update(other.possible)

        # return self.check_combine()
        
    def check_combine(self) -> Optional[list[int]]:
        unknown_count = self.unknown_count()
        if unknown_count > 0 and unknown_count == len(self.possible):
            print(unknown_count, self.possible)
            ret = list(self.possible)
            self.known.update(self.possible)
            self.possible.clear()
            return ret
        else:
            return None
        
    def check_finished(self) -> bool:
        return self.capped and self.unknown_count == 0
    
    def copy(self) -> Self:
        ret = CharStatus(self.possible.copy())
        ret.count = self.count
        ret.known = self.known.copy()
        ret.capped = self.capped

        return ret
    
    def tup(self) -> tuple[Any]:
        return (self.count, tuple(sorted(self.known)), tuple(sorted(self.possible)), self.capped)
