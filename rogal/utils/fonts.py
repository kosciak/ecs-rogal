import logging

import freetype
from fclist import fclist, fcmatch

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

