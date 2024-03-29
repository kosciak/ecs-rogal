import collections
import importlib

from ..collections.attrdict import AttrDict
from ..data import Glyphs, TilesSources, ColorPalettes

from .core import Tile


class ReplaceForeground:

    def __init__(self, palette, fg):
        # self.fg = palette.get(fg)
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
        self._tiles_sources = None
        self._palette = None
        self._revealed_fn = None
        self._tiles = {}

    @property
    def tiles_sources(self):
        if self._tiles_sources is None:
            data = self.loader.load()
            self.parse_data(data)
        return self._tiles_sources

    @property
    def palette(self):
        if self._palette is None:
            data = self.loader.load()
            self.parse_data(data)
        return self._palette

    @property
    def tiles(self):
        if not self._tiles:
            data = self.loader.load()
            self.parse_data(data)
        return self._tiles

    @property
    def revealed_fn(self):
        if self._revealed_fn is None:
            data = self.loader.load()
            self.parse_data(data)
        return self._revealed_fn

    def parse_tiles_sources(self, data):
        tiles_sources = []
        for name in data['tiles_sources']:
            tiles_sources.append(TilesSources.get(name))
        return tiles_sources

    def parse_palette(self, data):
        name = data['palette']
        return ColorPalettes.get(name)

    def parse_revealed_fn(self, data):
        for name, value in data['revealed'].items():
            return globals()[name](self.palette, value)

    def parse_tiles(self, data):
        tiles = {}
        for name, values in data['tiles'].items():
            if len(values) == 3:
                ch, fg, bg = values
            else:
                ch, fg = values
                bg = None
            visible = Tile.create(
                Glyphs.get(ch, ch),
                fg, bg,
            )
            # TODO: Only name, and visible color should be stored, revealed or any other effect
            #       should be done on map rendering level
            revealed = self.revealed_fn(visible) # TODO: Don't like it... It assumes it will work with Color
            tile = RenderableTile(name, visible, revealed)
            tiles[name] = tile
        return tiles

    def parse_data(self, data):
        self._tiles_sources = self.parse_tiles_sources(data)
        self._palette = self.parse_palette(data)
        self._revealed_fn = self.parse_revealed_fn(data)
        self._tiles = self.parse_tiles(data)

    def get(self, name):
        return self.tiles.get(name)

