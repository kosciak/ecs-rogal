from renderable import Tile
from colors.x11 import Color


"""All Tile definitions."""


# Terrain

STONE_WALL =    Tile.create('#', fg=Color.BASE_YELLOW)
STONE_FLOOR =   Tile.create('.', fg=Color.BASE_WHITE)


# Entities

PLAYER =        Tile.create('@', fg=Color.BRIGHT_WHITE)

