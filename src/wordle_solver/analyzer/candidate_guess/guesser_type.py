from enum import Enum, auto
from typing import Self


class GuesserType(Enum):
    NoGuess = auto(),
    AnswerGuess = auto(),
    CommonChars = auto(),
    UnusedChars = auto()

    @classmethod
    def from_string(cls, s: str) -> Self:
        cleaned = ''.join(c for c in s.lower() if c.isalpha())

        for k, valid in _INPUT_MAPPING.items():
            if cleaned in valid:
                return k

        raise TypeError(f'{s} invalid as GuesserType input')


_INPUT_MAPPING: dict[GuesserType, tuple[str, ...]] = {
    GuesserType.NoGuess: ('none', 'noguess', 'noguess'),
    GuesserType.AnswerGuess: ('validonly', 'onlyvalid', 'valid', 'answerguess', 'aggressive'),
    GuesserType.CommonChars: ('common', 'commonchars'),
    GuesserType.UnusedChars: ('unused', 'unusedchars')
}
