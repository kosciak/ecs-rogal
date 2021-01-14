import collections
import os.path

import tcod


ASSETS_DIR = 'assets'
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')



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
    tcod.tileset.CHARMAP_TCOD,
)

TERMINAL_12x12_CP = Tilesheet(
    os.path.join(FONTS_DIR, "terminal12x12_gs_ro.png"),
    16,
    16,
    tcod.tileset.CHARMAP_CP437,
)

