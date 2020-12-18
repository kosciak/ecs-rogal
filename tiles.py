from renderable import Tile
from colors.x11 import Color

from terrain import Terrain


"""All Tile definitions."""


# Terrain

STONE_WALL =    Tile.create('#', fg=Color.BASE_YELLOW)
STONE_FLOOR =   Tile.create('.', fg=Color.BASE_WHITE)


TERRAIN = {
    Terrain.STONE_WALL.id:     STONE_WALL,
    Terrain.STONE_FLOOR.id:    STONE_FLOOR,
}


# Entities

PLAYER =        Tile.create('@', fg=Color.BRIGHT_WHITE)
MONSTER =       Tile.create('M', fg=Color.LIME)

