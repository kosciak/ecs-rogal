from enum import IntFlag, auto


class Flag(IntFlag):
    NONE = 0

    BLOCK_VISION = auto()

    BLOCK_WALKING = auto()
    BLOCK_FLYING = auto()
    BLOCK_SWIMMING = auto()
    BLOCK_ALL_MOVEMENT = BLOCK_WALKING | BLOCK_FLYING | BLOCK_SWIMMING

    #BLOCK_ITEMS = auto() # Blocks item placement?


