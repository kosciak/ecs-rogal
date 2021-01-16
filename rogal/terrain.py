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


class Terrain(Enum):
    # TODO: Remove it? All data is in ECS already, only used in procgen for setting terrain
    #       This should be declared in yaml file with details about level generation
    VOID = (Type.VOID, Material.NONE)
    CHASM = (Type.CHASM, Material.NONE)

    DOOR = (Type.WALL, Material.NONE)

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
        self.id = self.material + (self.type<<4)

    @property
    def hex(self):
        return f'{self.id:02x}'

