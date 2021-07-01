import collections
from enum import IntEnum, auto


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


class Glyph(int):

    __slots__ = ()

    __INSTANCES = {}

    def __new__(cls, code_point):
        if isinstance(code_point, Glyph):
            return code_point
        if isinstance(code_point, Tile):
            return code_point.glyph
        if isinstance(code_point, str):
            code_point = ord(code_point)
        instance = cls.__INSTANCES.get(code_point)
        if not instance:
            instance = super().__new__(cls, code_point)
            cls.__INSTANCES[code_point] = instance
        return instance

    @property
    def char(self):
        return chr(self)

    def __str__(self):
        return self.char

    def __repr__(self):
        return f'<Glyph {self:d} = "{self.char}">'


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


class HasColorsMixin:

    @property
    def fg(self):
        return self.colors and self.colors.fg

    @property
    def bg(self):
        return self.colors and self.colors.bg


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

