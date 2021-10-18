from enum import Enum, auto


class RunState(Enum):
    PRE_RUN = auto()        # Preparations
    TICKING = auto()        # Ticking actions queue
    TAKE_ACTIONS = auto()   # Decide what actions to take
    PERFOM_ACTIONS = auto() # Perform actions

    ANIMATIONS = auto()     # 

    WAIT_FOR_INPUT = auto() # Process input events
    RENDER = auto()         # Render graphics

