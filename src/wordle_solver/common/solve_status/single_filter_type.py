from enum import Enum, auto

class SingleFilterType(Enum):
    ANY = auto(),
    NOT = auto(),
    GUARANTEED = auto()