from renderable import Tile
from colors.x11 import Color
from glyphs import Glyph

from terrain import Terrain


"""All Tile definitions."""


# Terrain

BOUNDARY =      Tile.create(Glyph.BLOCK1, fg=Color.BASE_RED)

STONE_WALL =    Tile.create('#', fg=Color.BASE_YELLOW)
STONE_FLOOR =   Tile.create('.', fg=Color.BASE_WHITE)


VISIBLE_TERRAIN = {
    Terrain.STONE_WALL.id:     STONE_WALL,
    Terrain.STONE_FLOOR.id:    STONE_FLOOR,
}

REVEALED_TERRAIN = {
    terrain_id: Tile.create(tile.glyph, fg=Color.BRIGHT_BLACK)
    for terrain_id, tile in VISIBLE_TERRAIN.items()
}


# Entities

PLAYER =        Tile.create('@', fg=Color.BRIGHT_WHITE)
MONSTER =       Tile.create('M', fg=Color.LIME)

