import collections

import tcod


class Tileset(collections.namedtuple(
    'Tileset', [
        'path',
        'columns',
        'rows',
        'charmap',
    ])):

    __slots__ = ()


DEJAVU_10x10_TC = Tileset(
    "data/fonts/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD,
)

TERMINAL_12x12_CP = Tileset(
    "data/fonts/terminal12x12_gs_ro.png", 16, 16, tcod.tileset.CHARMAP_CP437,
)

