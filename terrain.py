import collections
from enum import Enum, IntEnum, IntFlag, auto
from flags import Flag


class Type(IntEnum):
    """General Terrain tile type."""
    VOID = 0
    CHASM = auto()

    FLOOR = auto()
    PATH = auto()
    ROAD = auto()

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


class Terrain(Enum):
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

    def __init__(self, terrain_type, material):
        self.type = terrain_type
        self.material = material
        self.id = self.type + (self.material<<8)


TERRAIN_BY_ID = {
    terrain.id: terrain
    for terrain in Terrain
}


BLOCK_VISION = {
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



def get_flags(terrain):
    if not terrain in Terrain:
        terrain = TERRAIN_BY_ID.get(terrain)

    flags = Flag.NONE

    if terrain.type in BLOCK_VISION and \
       not terrain.material in TRANSPARENT:
        flags |= Flag.BLOCK_VISION

    if terrain.type in BLOCK_ALL_MOVEMENT:
        flags |= Flag.BLOCK_ALL_MOVEMENT
    if not terrain.type in ALLOW_SWIMMING:
        flags |= Flag.BLOCK_SWIMMING
    if terrain.type in BLOCK_WALKING:
        flags |= Flag.BLOCK_WALKING

    return flags

