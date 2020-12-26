from enum import Enum, auto


class RunState(Enum):
    PRE_RUN = auto()
    TICKING = auto()
    WAITING_FOR_INPUT = auto()
    ACTION_PERFORMED = auto()
    ANIMATIONS = auto()

