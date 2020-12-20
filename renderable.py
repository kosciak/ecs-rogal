import collections
from enum import IntEnum, auto


# TODO: Rename module to renderables.py ?

class Colors(collections.namedtuple(
    'Colors', [
        'fg',
        'bg',
    ])):

    def __new__(cls, fg=None, bg=None):
        if fg is None and bg is None:
            return None
        return super().__new__(cls, fg, bg)

    def invert(self):
        return Colors(self.bg, self.fg)


class Glyph:

    __slots__ = ('code_point', )

    __INSTANCES = {}

    def __new__(cls, code_point):
        if isinstance(code_point, Glyph):
            return code_point
        if isinstance(code_point, str):
            code_point = ord(code_point)
        instance = cls.__INSTANCES.get(code_point)
        if not instance:
            instance = super().__new__(cls)
            instance.code_point = code_point
            cls.__INSTANCES[code_point] = instance
        return instance

    @property
    def char(self):
        return chr(self.code_point)

    def __eq__(self, other):
        return self.code_point == other.code_point

    def __str__(self):
        return self.ch

    def __repr__(self):
        return f'<Glyph {self.code_point} = "{self.char}">'


class Tile(collections.namedtuple(
    'Tile', [
        'glyph',
        'colors',
    ])):

    @property
    def char(self):
        return self.glyph.char

    @property
    def ch(self):
        return self.glyph.code_point

    @property
    def fg(self):
        return self.colors.fg

    @property
    def bg(self):
        return self.colors.bg

    @staticmethod
    def create(ch, fg, bg=None):
        return Tile(Glyph(ch), Colors(fg, bg))


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

