import numpy as np

from .. import dtypes

from ..colors import RGB
from ..geometry import Size

from .core import Glyph


EMPTY_TILE = Glyph(' ')


class Console:

    TILES_DTYPE = None
    DEFAULT_FG = None
    DEFAULT_BG = None

    def __init__(self, size):
        size = Size(size.height, size.width)
        self.tiles = np.zeros(size, dtype=self.TILES_DTYPE, order="C")
        self.tiles[...] = (EMPTY_TILE, self.DEFAULT_FG, self.DEFAULT_BG)

    @property
    def width(self):
        return self.tiles.shape[1]

    @property
    def height(self):
        return self.tiles.shape[0]

    @property
    def ch(self):
        return self.tiles['ch']

    @property
    def fg(self):
        return self.tiles['fg']

    @property
    def bg(self):
        return self.tiles['bg']

    def encode_tile_data(self, tile, encode_ch):
        return encode_ch(tile['ch']), tile['fg'], tile['bg']

    def tiles_gen(self, encode_ch=int):
        tiles = np.nditer(self.tiles, flags=['refs_ok', 'multi_index', ])
        for tile in tiles:
            y, x = tiles.multi_index
            yield x, y, *self.encode_tile_data(tile, encode_ch)

    def tiles_diff_gen(self, other, encode_ch=int):
        if other is None or not self.tiles.shape == other.shape:
            yield from self.tiles_gen(encode_ch)
            return

        diff = self.tiles != other
        # for x, y in np.nditer(diff.nonzero(), flags=['zerosize_ok', ]):
        for x, y in np.transpose(diff.nonzero()):
            tile = self.tiles[x, y]
            # yield int(y), int(x), *self.encode_tile_data(tile, encode_ch)
            yield y, x, *self.encode_tile_data(tile, encode_ch)


class RGBConsole(Console):

    TILES_DTYPE = dtypes.CONSOLE_RGB_DT
    DEFAULT_FG = RGB(255, 255, 255).rgb
    DEFAULT_BG = RGB(0, 0, 0).rgb


class IndexedColorsConsole(Console):

    TILES_DTYPE = dtypes.TILES_INDEXED_COLORS_DT
    DEFAULT_FG = -1
    DEFAULT_BG = -1

    def encode_tile_data(self, tile, encode_ch):
        return encode_ch(tile['ch']), int(tile['fg']), int(tile['bg'])


