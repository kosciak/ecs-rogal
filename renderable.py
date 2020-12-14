import collections
from enum import IntEnum, auto


# TODO: Rename module to renderables.py ?

class Colors(collections.namedtuple(
    'Colors', [
        'fg',
        'bg',
    ])):

    def __new__(cls, fg=None, bg=None):
        if not (fg or bg):
            return None
        return super().__new__(cls, fg, bg)

    def invert(self):
        return Colors(self.bg, self.fg)


class Character:

    __slots__ = ('code_point', )

    __INSTANCES = {}

    def __new__(cls, code_point):
        if isinstance(code_point, Character):
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
    def ch(self):
        return chr(self.code_point)

    def __eq__(self, other):
        return self.code_point == other.code_point

    def __str__(self):
        return self.ch

    def __repr__(self):
        return f'<Character {self.code_point} = "{self.ch}">'


class Tile(collections.namedtuple(
    'Tile', [
        'character',
        'colors',
    ])):

    @property
    def ch(self):
        return self.character.ch

    @property
    def code_point(self):
        return self.character.code_point

    @property
    def fg(self):
        return self.colors.fg

    @property
    def bg(self):
        return self.colors.bg

    @staticmethod
    def create(ch, fg, bg=None):
        return Tile(Character(ch), Colors(fg, bg))


class RenderOrder(IntEnum):
    # Terrain tiles
    TERRAIN = auto()
    # Terrian foliage (grass, bushes, flowers, etc)
    FOLIAGE = auto()
    # Props - furniture, statues, doors, stairs, etc
    PROPS = auto()
    # Items on floor
    ITEMS = auto()
    # Player, monsters, NPCs
    ACTORS = auto()
    # Particle effects
    PARTICLES = auto()

