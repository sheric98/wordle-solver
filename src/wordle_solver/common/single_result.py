from typing import Optional, Self
from enum import IntEnum


class SingleResult(IntEnum):
    GREEN = 2,
    GRAY = 0,
    YELLOW = 1

    @staticmethod
    def from_string(s: str) -> Optional[Self]:
        cleaned = s.strip().lower()

        if cleaned == 'green' or cleaned == '2':
            return SingleResult.GREEN
        elif cleaned == 'yellow' or cleaned == '1':
            return SingleResult.YELLOW
        elif cleaned == 'gray' or cleaned == 'grey' or cleaned == '0':
            return SingleResult.GRAY
        
        print(f'Could not convert input of {s}...')
        return None