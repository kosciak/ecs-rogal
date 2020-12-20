from renderable import Tile
from colors.x11 import Color
from glyphs import Glyph

from terrain import Terrain


"""All Tile definitions."""


def visible(tile):
    """Return visible tile."""
    return tile

def revealed(tile):
    """Return revealed but not visible tile."""
    return Tile.create(tile.glyph, fg=Color.BRIGHT_BLACK)


# Terrain

BOUNDARY =      Tile.create(Glyph.BLOCK1, fg=Color.BASE_RED)

VOID =          Tile.create(Glyph.FULL_BLOCK, fg=Color.BASE_BLACK)
STONE_WALL =    Tile.create('#', fg=Color.BASE_YELLOW)
STONE_FLOOR =   Tile.create('.', fg=Color.BASE_WHITE)
SHALLOW_WATER = Tile.create('~', fg=Color.BRIGHT_BLUE)


# Entities

PLAYER =        Tile.create('@', fg=Color.BRIGHT_WHITE)
MONSTER =       Tile.create('M', fg=Color.LIME)

