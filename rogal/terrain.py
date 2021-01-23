import collections
from enum import Enum, IntEnum, IntFlag, auto

from .flags import Flag


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

    MUD = 8

    WATER = 10
    ACID = auto()
    LAVA = auto()


def get_terrain_id(terrain):
    material = terrain.material or Material.NONE
    return material + (terrain.type<<4)

