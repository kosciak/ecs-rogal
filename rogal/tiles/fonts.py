import logging
import string

import freetype

import numpy as np

from ..geometry import Size

from .tiles_source import TilesSource


log = logging.getLogger(__name__)


class TrueTypeFont(TilesSource):

    """True Type Font loader."""

    DEFAULT_DPI = 96
    MONOSPACE_REFERENCE_CHARS = ['@', ]
    PROPORTIONAL_REFERENCE_CHARS = string.ascii_uppercase

    def __init__(self, path, size, charset=None):
        self.face = freetype.Face(path)
        if charset is None:
            charset = [
                code_point for (code_point, char_index)
                in self.face.get_chars()
                if char_index
            ]
        super().__init__(charset)
        self._pixel_size = None
        self._is_monospace = None
        if isinstance(size, Size):
            self.set_pixel_size(size)
        else:
            self.set_char_size(size)

    def set_char_size(self, size, dpi=DEFAULT_DPI):
        self.face.set_char_size(0, int(size*64), hres=dpi, vres=dpi)
        self._pixel_size = None

    def set_pixel_size(self, size):
        min_char_size = 1
        max_char_size = 96
        guess_char_size = size.height
        correct_char_size = None

        while correct_char_size is None:
            self.set_char_size(guess_char_size)
            pixel_size = self.pixel_size
            if pixel_size.width > size.width or pixel_size.height > size.height:
                print(f'{guess_char_size} {pixel_size} too big! - {min_char_size} - {max_char_size}')
                max_char_size = guess_char_size
            elif pixel_size.width <= size.width and pixel_size.height <= size.height:
                print(f'{guess_char_size} {pixel_size} too small! - {min_char_size} - {max_char_size}')
                if guess_char_size == max_char_size or guess_char_size == min_char_size:
                    correct_char_size = guess_char_size
                    break
                min_char_size = guess_char_size
            guess_char_size = (min_char_size + max_char_size) // 2

    # TODO: Set hinting, loading flags

    def has_char(self, char):
        char_index = self.face.get_char_index(char)
        return char_index != 0

    def has_code_point(self, code_point):
        char = chr(code_point)
        return self.has_char(char)

    def load_char(self, char):
        if not isinstance(char, str):
            char = chr(char)
        # TODO: flags!
        self.face.load_char(char)

    @property
    def is_monospace(self):
        # NOTE: Size MUST be set first for this to work!
        if self._is_monospace is None:
            dot = self.load_char('.')
            dot_width = self.face.glyph.advance.x//64
            at = self.load_char('@')
            at_width = self.face.glyph.advance.x//64
            self._is_monospace = dot_width == at_width
        return self._is_monospace

    @property
    def _reference_chars(self):
        if self.is_monospace:
            return self.MONOSPACE_REFERENCE_CHARS
        else:
            return self.PROPORTIONAL_REFERENCE_CHARS

    @property
    def pixel_size(self):
        if self._pixel_size is None:
            # NOTE: face.height might be lower than ascender + descender and last line (like in "_") might be cut off
            # height = self.face.size.height//64
            height = self.face.size.ascender//64 - self.face.size.descender//64
            widths = []
            for char in self._reference_chars:
                self.load_char(char)
                widths.append(self.face.glyph.metrics.width//64)
            width = max(widths)
            self._pixel_size = Size(width, height)
        return self._pixel_size

    def get_tile(self, code_point, tile_size):
        if not self.has_code_point(code_point):
            return None

        pixel_size = self.pixel_size

        self.load_char(code_point)
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

        if self.is_monospace:
            left = self.face.glyph.bitmap_left + offset_x
        else:
            left = max(0, (pixel_size.width - self.face.glyph.metrics.width//64)//2 + offset_x)
        top = self.face.size.ascender//64 - self.face.glyph.bitmap_top + offset_y

        left += max(0, tile_size.width-pixel_size.width) // 2
        top += max(0, tile_size.height-pixel_size.height) // 2

        tile = np.zeros(tile_size, dtype=np.uint8, order="F")

        # if bitmap_array.shape[0]+left > tile.shape[0]:
        #     print('Too wide!', chr(code_point))
        # if bitmap_array.shape[1]+top > tile.shape[1]:
        #     print('Too tall!', chr(code_point))
        bitmap_array = bitmap_array[:tile.shape[0]-left, :tile.shape[1]-top]

        tile[left:left+bitmap_array.shape[0], top:top+bitmap_array.shape[1] ] = bitmap_array

        return tile.transpose()

