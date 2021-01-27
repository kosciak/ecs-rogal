from enum import IntFlag, auto

from . import components


class Flag(IntFlag):
    NONE = 0

    BLOCKS_VISION = auto()

    BLOCKS_WALKING = auto()
    # TODO: Reenable after adding some kind on MovementType support
    BLOCKS_FLYING = 0 #auto()
    BLOCKS_SWIMMING = 0 #auto()
    BLOCKS_MOVEMENT = BLOCKS_WALKING | BLOCKS_FLYING | BLOCKS_SWIMMING

    #BLOCKS_ITEMS = auto() # Blocks item placement?

