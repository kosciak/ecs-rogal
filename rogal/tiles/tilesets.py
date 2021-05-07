import collections
import importlib

from ..collections.attrdict import AttrDict

from .core import Tile
from .symbols import Symbol
from . import tilesheets


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


class Tileset:

    def __init__(self, loader):
        self.loader = loader
        self._tilesheet = None
        self._palette = None
        self._revealed_fn = None
        self._tiles = {}
        self._bitmasks = {}
        self._decorations = {}

    @property
    def tilesheet(self):
        if self._tilesheet is None:
            data = self.load_data(self.fn)
            self.parse_data(data)
        return self._tilesheet

    @property
    def palette(self):
        if self._palette is None:
            data = self.load_data(self.fn)
            self.parse_data(data)
        return self._palette

    @property
    def tiles(self):
        if not self._tiles:
            data = self.loader.load()
            self.parse_data(data)
        return self._tiles

    @property
    def bitmasks(self):
        if not self._bitmasks:
            data = self.loader.load()
            self.parse_data(data)
        return self._bitmasks

    @property
    def decorations(self):
        if not self._decorations:
            data = self.loader.load()
            self.parse_data(data)
        return self._decorations

    @property
    def revealed_fn(self):
        if self._revealed_fn is None:
            data = self.load_data(self.fn)
            self.parse_data(data)
        return self._revealed_fn

    def parse_tilesheet(self, data):
        name = data['tilesheet']
        tilesheet = getattr(tilesheets, name)
        return tilesheet

    def parse_palette(self, data):
        name = data['palette']
        module_name, sep, palette_name = name.rpartition('.')
        module = importlib.import_module(module_name)
        palette = getattr(module, palette_name)
        return palette

    def parse_revealed_fn(self, data):
        for name, value in data['revealed'].items():
            return globals()[name](value)

    def parse_tiles(self, data):
        tiles = {}
        for name, values in data['tiles'].items():
            if len(values) == 3:
                ch, fg, bg = values
            else:
                ch, fg = values
                bg = None
            visible = Tile.create(Symbol.get(ch), fg, bg)
            revealed = self.revealed_fn(visible) # TODO: Don't like it... It assumes it will work with Color
            tile = RenderableTile(name, visible, revealed)
            tiles[name] = tile
        return tiles

    def parse_symbols(self, data, category):
        symbols = AttrDict()
        for name, values in data[category].items():
            symbols[name] = [Symbol.get(ch) for ch in values]
        return symbols

    def parse_data(self, data):
        self._tilesheet = self.parse_tilesheet(data)
        self._palette = self.parse_palette(data)
        self._revealed_fn = self.parse_revealed_fn(data)
        self._tiles = self.parse_tiles(data)
        self._bitmasks = self.parse_symbols(data, 'bitmasks')
        self._decorations = self.parse_symbols(data, 'decorations')

    def get(self, name):
        return self.tiles.get(name)

