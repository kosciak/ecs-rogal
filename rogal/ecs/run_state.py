from enum import Enum, auto


class RunState(Enum):
    PRE_RUN = auto()
    TICKING = auto()
    WAITING_FOR_ACTIONS = auto()
    WAITING_FOR_INPUT = auto()
    PERFOM_ACTIONS = auto()
    ANIMATIONS = auto()

