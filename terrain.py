import collections
from enum import Enum, IntEnum, IntFlag, auto


class TerrainTile(Enum):
    VOID = (Type.VOID, Material.NONE)
    CHASM = (Type.CHASM, Material.NONE)

    STONE_FLOOR = (Type.FLOOR, Material.STONE)
    STONE_WALL = (Type.WALL, Material.STONE)

    ROCK_FLOOR = (Type.FLOOR, Material.ROCK)
    ROCK_WALL = (Type.WALL, Material.ROCK)

    GROUND_FLOOR = (Type.FLOOR, Material.GROUND) 

    MUD_FLOOR = (Type.FLOOR, Material.MUD)

    DEEP_WATER = (Type.LIQUID, Material.WATER)
    SHALLOW_WATER = (Type.SHALLOW_LIQUID, Material.WATER)

    LAVA = (Type.LIQUID, Material.LAVA)
    ACID = (Type.LIQUID, Material.ACID)

    def __init__(self, type, material):
        self.type = type
        self.material = material

    @property
    def id(self):
        return self.type + (self.material<<8)


class Type(IntEnum):
    """General Terrain tile type."""
    VOID = 0
    CHASM = auto()

    FLOOR = auto()
    WALL = auto()

    LIQUID = auto()
    SHALLOW_LIQUID = auto()


class Material(IntEnum):
    """Material from which Terrain tile is made."""
    NONE = 0

    GROUND = auto()
    STONE = auto()
    ROCK = auto()

    SNOW = auto()
    ICE = auto()

    GLASS = auto()

    MUD = auto()

    WATER = auto()
    ACID = auto()
    LAVA = auto()


class TerrainFlag(IntFlag):
    NONE = 0

    OPAQUE = auto()

    BLOCK_WALKING = auto()
    BLOCK_FLYING = auto()
    BLOCK_SWIMMING = auto()
    BLOCK_ALL_MOVEMENT = BLOCK_WALKING | BLOCK_FLYING | BLOCK_SWIMMING


OPAQUE = {
    Type.WALL,
}

TRANSPARENT = {
    Material.GLASS,
}

ALLOW_SWIMMING = {
    Type.LIQUID,
    Type.SHALLOW_LIQUID,
}

BLOCK_WALKING = {
    Type.LIQUID,
    Type.CHASM,
}

BLOCK_ALL_MOVEMENT = {
    Type.VOID,
    Type.WALL,
}



def get_flags(type, material, variant=None):
    flags = TerrainFlag.NONE

    if type in OPAQUE and \
       not material in TRANSPARENT:
        flags |= TerrainFlag.OPAQUE

    if type in BLOCK_ALL_MOVEMENT:
        flags |= TerrainFlag.BLOCK_ALL_MOVEMENT
    if not type in ALLOW_SWIMMING:
        flags |= TerrainFlag.BLOCK_SWIMMING
    if type in BLOCK_WALKING:
        flags |= TerrainFlag.BLOCK_WALKING

    return flags
