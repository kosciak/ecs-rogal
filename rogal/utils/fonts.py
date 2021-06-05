import logging

import freetype

import numpy as np

from ..colors import RGB

from ..geometry import Size

from ..term import ansi

from ..tiles.charsets import CP437


log = logging.getLogger(__name__)


GRAYSCALE = []
for i in range(256):
    GRAYSCALE.append(RGB(i, i, i).rgb)

BLOCK = chr(9608)
# BLOCK = ' '


PATH = '/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf'
# PATH = '/usr/share/fonts/google-droid-sans-mono-fonts/DroidSansMono.ttf'
SIZE = 11
DPI = 96


def render_ba(ba):
    for row in ba.transpose():
        r = []
        for value in row:
            r.append(f'{ansi.fg_rgb(*GRAYSCALE[255-value])}{BLOCK}')
        r.append(ansi.reset())
        print(''.join(r))
    # print(ba.transpose())


def show(size=SIZE, dpi=DPI, render=False):
    ttf = freetype.Face(PATH)
    ttf.set_char_size(0, size * 64, hres=dpi, vres=dpi)
    # ttf.set_pixel_sizes(size, size)

    for ch in CP437:
        char = chr(ch)
        ttf.load_char(char)
        bitmap = ttf.glyph.bitmap
        ba = np.asarray(bitmap.buffer).reshape(bitmap.width, bitmap.rows, order='F')
        print(
            char,
            ba.shape,
            ttf.glyph.bitmap_left, ttf.glyph.bitmap_top,
        )
        if render:
            render_ba(ba)
    print( ttf.size.height//64, ttf.size.descender//64, ttf.size.ascender//64 )


class TrueTypeFont:

    DPI = 96

    def __init__(self, path):
        self.face = freetype.Face(path)
        self._pixel_size = None

    def set_char_size(self, size, dpi=DPI):
        self.face.set_char_size(0, size*64, hres=dpi, vres=dpi)
        self._pixel_size = None

    # TODO: Set hinting, loading flags

    def has_char(self, char):
        if not isinstance(char, str):
            char = chr(char)
        char_index = self.face.get_char_index(char)
        return char_index != 0

    def load_char(self, char):
        if not isinstance(char, str):
            char = chr(char)
        # TODO: flags!
        self.face.load_char(char)

    @property
    def is_monospace(self):
        dot = self.load_char('.')
        dot_width = self.face.glyph.advance.x//64
        at = self.load_char('@')
        at_width = self.face.glyph.advance.x//64
        return dot_width == at_width

    @property
    def pixel_size(self):
        if self._pixel_size is None:
            # height = self.face.size.height//64
            height = self.face.size.ascender//64 - self.face.size.descender//64
            widths = []
            # for char in ['@', '_', 'W']:
            for char in ['@', ]:
                self.load_char(char)
                widths.append(self.face.glyph.metrics.width//64)
            width = max(widths)
            self._pixel_size = Size(width, height)
        return self._pixel_size

    def get_tile(self, char):
        if not self.has_char(char):
            return None

        tile = np.zeros(self.pixel_size, dtype=np.uint8, order="F")

        self.load_char(char)
        bitmap = self.face.glyph.bitmap
        if not bitmap.pixel_mode == freetype.FT_PIXEL_MODE_GRAY:
            raise ValueError(
                "Invalid pixel_mode! got: %s, expected: %s" % (bitmap.pixel_mode, freetype.FT_PIXEL_MODE_GRAY)
            )

        bitmap_array = np.asarray(bitmap.buffer).reshape(
            (bitmap.width, bitmap.rows), order="F"
        )
        if bitmap_array.size == 0:
            return None

        offset_x = 0
        if self.face.glyph.bitmap_left < 0:
            offset_x = self.face.glyph.bitmap_left * -1
            bitmap_array = bitmap_array[offset_x:, :]
        offset_y = 0
        if self.face.glyph.bitmap_top > self.face.size.ascender//64:
            offset_y = self.face.glyph.bitmap_top - self.face.size.ascender//64
            bitmap_array = bitmap_array[:, offset_y:]

        left = self.face.glyph.bitmap_left + offset_x
        top = self.face.size.ascender//64 - self.face.glyph.bitmap_top + offset_y

        # if bitmap_array.shape[0]+left > tile.shape[0]:
        #     print('Too wide!', chr(char))
        # if bitmap_array.shape[1]+top > tile.shape[1]:
        #     print('Too tall!', chr(char))
        bitmap_array = bitmap_array[:tile.shape[0]-left, :tile.shape[1]-top]

        # print(chr(char), tile.shape, bitmap_array.shape, (left, top))
        tile[left:left+bitmap_array.shape[0], top:top+bitmap_array.shape[1] ] = bitmap_array

        return tile.transpose()


