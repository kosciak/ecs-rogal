import collections
from enum import IntEnum, auto

from ..console.core import Glyph, Colors, HasColorsMixin


class RenderOrder(IntEnum):
    # Terrain tiles
    TERRAIN = auto()
    # Terrian foliage (grass, bushes, flowers, etc)
    FOLIAGE = auto()
    # Props - furniture, statues, altars, doors, stairs, etc
    PROPS = auto()
    # Items on floor
    ITEMS = auto()
    # Player, monsters, NPCs
    ACTORS = auto()
    # Particle effects
    PARTICLES = auto()


class Tile(HasColorsMixin, collections.namedtuple(
    'Tile', [
        'glyph',
        'colors',
    ])):

    @property
    def char(self):
        return self.glyph.char

    @property
    def ch(self):
        return self.glyph

    @staticmethod
    def create(ch, fg=None, bg=None):
        if ch is None:
            return None
        return Tile(Glyph(ch), Colors(fg, bg))

