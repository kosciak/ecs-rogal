from enum import Enum

from .colors.x11 import Color
from .glyphs import Glyph
from .renderable import Tile


"""All Tile definitions."""

class Tilesset(Enum):

    def __init__(self, ch, fg, bg=None):
        self.tile = Tile.create(ch, fg=fg, bg=bg)

    @property
    def visible(self):
        """Return visible tile."""
        return self.tile

    @property
    def revealed(self):
        """Return revealed but not visible tile."""
        raise NotImplementedError()

    @property
    def char(self):
        return self.tile.char

    @property
    def ch(self):
        return self.tile.ch

    @property
    def fg(self):
        return self.tile.fg

    @property
    def bg(self):
        return self.tile.bg

    def __repr__(self):
        return f'<Tile {self.char!r}, fg={self.fg}, bg={self.bg}>'


class TermTiles(Tilesset):

    BOUNDARY =      (Glyph.BLOCK1, Color.BASE_RED)

    # Terrain
    VOID =          (Glyph.FULL_BLOCK, Color.BASE_BLACK)
    STONE_WALL =    ('#', Color.BASE_YELLOW)
    STONE_FLOOR =   ('.', Color.BASE_WHITE)
    SHALLOW_WATER = ('~', Color.BASE_BLUE)

    # Entities
    PLAYER =        ('@', Color.BRIGHT_WHITE)
    MONSTER =       ('M', Color.LIME)

    # Particles
    MEELE_HIT =     (0, None, Color.BRIGHT_RED)

    @property
    def revealed(self):
        """Return revealed but not visible tile."""
        return Tile.create(self.ch, fg=Color.BRIGHT_BLACK)

