import collections
from enum import IntEnum, auto
import importlib
import os.path

from .data_loaders import DATA_DIR, YAMLDataLoader
from . import glyphs


# TODO: Rename module to renderables.py ?


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


class ReplaceForeground:

    def __init__(self, fg):
        self.fg = fg

    def __call__(self, tile):
        return Tile.create(tile.ch, fg=self.fg, bg=tile.bg)


RenderableTile = collections.namedtuple(
    'RenderableTile', [
        'name',
        'visible',
        'revealed',
    ])


class Tileset(YAMLDataLoader):

    def __init__(self):
        self.fn = os.path.join(
            DATA_DIR,
            'tiles.yaml'
        )
        self._palette = None
        self._revealed_fn = None
        self._tiles = {}

    @property
    def tiles(self):
        if not self._tiles:
            data = self.load_data(self.fn)
            self.parse_data(data)
        return self._tiles

    @property
    def palette(self):
        if self._palette is None:
            data = self.load_data(self.fn)
            self.parse_data(data)
        return self._palette

    @property
    def revealed_fn(self):
        if self._revealed_fn is None:
            data = self.load_data(self.fn)
            self.parse_data(data)
        return self._revealed_fn

    def parse_palette(self, data):
        name = data['palette']
        module_name, sep, palette_name = name.rpartition('.')
        module = importlib.import_module(module_name)
        palette = getattr(module, palette_name)
        return palette

    def parse_revealed_fn(self, data):
        for name, value in data['revealed'].items():
            return globals()[name](self.palette.get(value))

    def parse_tiles(self, data):
        tiles = {}
        for name, values in data['tiles'].items():
            if len(values) == 3:
                ch, fg, bg = values
            else:
                ch, fg = values
                bg = None
            visible = Tile.create(
                glyphs.get(ch),
                self.palette.get(fg),
                self.palette.get(bg)
            )
            revealed = self.revealed_fn(visible)
            tile = RenderableTile(name, visible, revealed)
            tiles[name] = tile
        return tiles

    def parse_data(self, data):
        self._palette = self.parse_palette(data)
        self._revealed_fn = self.parse_revealed_fn(data)
        self._tiles = self.parse_tiles(data)

    def get(self, name):
        return self.tiles.get(name)

