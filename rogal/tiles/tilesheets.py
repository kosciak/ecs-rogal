import collections
import os.path

from . import charsets


ASSETS_DIR = 'assets'
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')


class TrueTypeFont(collections.namedtuple(
    'TrueTypeFont', [
        'path',
        'width',
        'height',
    ])):

    __slots__ = ()


class Tilesheet(collections.namedtuple(
    'Tilesheet', [
        'path',
        'columns',
        'rows',
        'charmap',
    ])):

    __slots__ = ()


DEJAVU_10x10_TC = Tilesheet(
    os.path.join(FONTS_DIR, "dejavu10x10_gs_tc.png"),
    32,
    8,
    charsets.TCOD,
)

TERMINAL_12x12_CP = Tilesheet(
    os.path.join(FONTS_DIR, "terminal12x12_gs_ro.png"),
    16,
    16,
    charsets.CP437,
)


# Looks BAD... :(
DEJA_VU_SANS_MONO_12x12_TTF = TrueTypeFont(
    '/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf',
    12,
    12,
)
