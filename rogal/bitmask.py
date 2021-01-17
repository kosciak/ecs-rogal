import numpy as np

from .glyphs import Glyph


"""
# Bitmasking / bitshifting

Technique used to alter tile appearance depending on it's neighbours.

## Cardinal bitmasking

Bitmask values for cardinal directions:
- NORT  = 1
- SOUTH = 2
- WEST  = 4
- EAST  = 8

 - - -    - - -    - - -    - - -
|  1  |  |  1  |  |  1  |  |x 1 x|
|4 ┘  |  |  │  |  |  └ 8|  |4 ┴ 8|
|     |  |     |  |     |  |     |
 - - -    - - -    - - -    - - -
 = 5      = 1      = 9      = 13

 - - -    - - -    - - -    - - -
|     |  |     |  |     |  |     |
|4 ─  |  |  ○  |  |  ─ 8|  |4 ─ 8|
|     |  |     |  |     |  |     |
 - - -    - - -    - - -    - - -
 = 6      = 0      = 8      = 12

 - - -    - - -    - - -    - - -
|     |  |     |  |     |  |     |
|4 ┐  |  |  │  |  |  ┌ 8|  |4 ┬ 8|
|  2  |  |  2  |  |  2  |  |x 2 x|
 - - -    - - -    - - -    - - -
= 6       = 2      = 10     = 14

 - - -    - - -    - - -    - - -
|x 1  |  |  1  |  |  1 x|  |  1  |
|4 ┤  |  |  │  |  |  ├ 8|  |4 ┼ 8|
|x 2  |  |  2  |  |  2 x|  |  2  |
 - - -    - - -    - - -    - - -
 = 7      = 3      = 11     = 15


## Diagonal bitmasking

Similar to cardinal, but use diagonal directions. Bitmask values:

 - - -
|1   8| = 9
|  X  |
|4   2| = 6
 - - -
 =   =
 5   10


## Walls bitmasking


**PROBLEM:** For tees (7, 11, 13, 14) and crossing (15) we don't want to draw perpendicular connector
if there are walls on positions marked with "x" as it creates ugly artifacts:

  ┌┬┬┬┬┐
  └┴┴┴┴┘

That's why we use diagonal bitmasking to fix it


"""


BITMASK_LINE = {
    0:  Glyph.RADIO_UNSET,
    1:  Glyph.VLINE,    # N
    2:  Glyph.VLINE,    #   S
    3:  Glyph.VLINE,    # N+S
    4:  Glyph.HLINE,    #     W
    5:  Glyph.SE,       # N  +W
    6:  Glyph.NE,       # S  +W
    7:  Glyph.TEEW,     # N+S+W
    8:  Glyph.HLINE,    #       E
    9:  Glyph.SW,       # N    +E
    10: Glyph.NW,       #   S  +E
    11: Glyph.TEEE,     # N+S  +E
    12: Glyph.HLINE,    #     W+E
    13: Glyph.TEEN,     # N  +W+E
    14: Glyph.TEES,     #   S+W+E
    15: Glyph.CROSS,    # N+S+W+E
}

BITMASK_DLINE = {
    0:  Glyph.BULLET_SQUARE,
    1:  Glyph.DVLINE,   # N
    2:  Glyph.DVLINE,   #   S
    3:  Glyph.DVLINE,   # N+S
    4:  Glyph.DHLINE,   #     W
    5:  Glyph.DSE,      # N  +W
    6:  Glyph.DNE,      # S  +W
    7:  Glyph.DTEEW,    # N+S+W
    8:  Glyph.DHLINE,   #       E
    9:  Glyph.DSW,      # N    +E
    10: Glyph.DNW,      #   S  +E
    11: Glyph.DTEEE,    # N+S  +E
    12: Glyph.DHLINE,   #     W+E
    13: Glyph.DTEEN,    # N  +W+E
    14: Glyph.DTEES,    #   S+W+E
    15: Glyph.DCROSS,   # N+S+W+E
}


def cardinal_bitmask(shape, padded):
    cardinal = np.zeros(shape, dtype=int)
    cardinal += padded[ 1:-1 ,  :-2] << 0 # N
    cardinal += padded[ 1:-1 , 2:  ] << 1 # S
    cardinal += padded[  :-2 , 1:-1] << 2 # W
    cardinal += padded[ 2:   , 1:-1] << 3 # E
    return cardinal


def diagonal_bitmask(shape, padded):
    diagonal = np.zeros(shape, dtype=int)
    diagonal += padded[  :-2 ,  :-2] << 0 # NW
    diagonal += padded[ 2:   , 2:  ] << 1 # SE
    diagonal += padded[  :-2 , 2:  ] << 2 # SW
    diagonal += padded[ 2:   ,  :-2] << 3 # NE
    return diagonal


def walls_bitmask(walls):
    shape = walls.shape
    padded = np.pad(walls, 1)

    cardinal = cardinal_bitmask(shape, padded)
    diagonal = diagonal_bitmask(shape, padded)

    bitmask = cardinal.copy()
    bitmask -= ((cardinal & 13 == 13) & (diagonal & 9 == 9)) << 0
    bitmask -= ((cardinal & 14 == 14) & (diagonal & 6 == 6)) << 1
    bitmask -= ((cardinal & 7 == 7) & (diagonal & 5 == 5)) << 2
    bitmask -= ((cardinal & 11 == 11) & (diagonal & 10 == 10)) << 3

    return bitmask

