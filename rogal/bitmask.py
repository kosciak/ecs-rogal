import enum

import numpy as np

from .tiles import Symbol


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

class Cardinal(enum.IntFlag):
    NONE = 0
    N = 1 << 0
    S = 1 << 1
    W = 1 << 2
    E = 1 << 3
    NW = N | W
    NE = N | E
    SW = S | W
    SE = S | E
    NS = N | S
    WE = W | E
    NSW = NS | W
    NSE = NS | E
    WEN = WE | N
    WES = WE | S
    NSWE = NS | WE


class Diagonal(enum.IntFlag):
    NONE = 0
    NW = 1 << 0
    SE = 1 << 1
    SW = 1 << 2
    NE = 1 << 3
    N = NW | NE
    S = SW | SE
    W = NW | SW
    E = NE | SE
    NSWE = N | S


def is_set(check, bits):
    """Return True if all bits are set."""
    return check & bits == bits


def get_cardinals(shape, padded):
    """Return bitmask for cardinal neighbours."""
    cardinals = np.zeros(shape, dtype=int)
    cardinals |= padded[ 1:-1 ,  :-2] << 0 # N
    cardinals |= padded[ 1:-1 , 2:  ] << 1 # S
    cardinals |= padded[  :-2 , 1:-1] << 2 # W
    cardinals |= padded[ 2:   , 1:-1] << 3 # E
    return cardinals


def get_diagonals(shape, padded):
    """Return bitmask for diagonal neighbours."""
    diagonals = np.zeros(shape, dtype=int)
    diagonals |= padded[  :-2 ,  :-2] << 0 # NW
    diagonals |= padded[ 2:   , 2:  ] << 1 # SE
    diagonals |= padded[  :-2 , 2:  ] << 2 # SW
    diagonals |= padded[ 2:   ,  :-2] << 3 # NE
    return diagonals


def shape_padded(array, pad_width=1, pad_value=None):
    """Return shape of array and padded array with padding of pad_with with pad_values."""
    shape = array.shape
    padded = np.pad(array, pad_width, constant_values=pad_value)
    return shape, padded


def bitmask(array, pad_value=None):
    """Return 4-bit bitmask for cardinal neighbours."""
    shape, padded = shape_padded(array, pad_value=pad_value)

    cardinals = get_cardinals(shape, padded)
    return cardinals


def bitmask_8bit(array, pad_value=None):
    """Return 8-bit bitmask for cardinal and diagonal neighbours."""
    shape, padded = shape_padded(array, pad_value=pad_value)
    cardinals = get_cardinals(shape, padded)
    diagonals = get_diagonals(shape, padded)

    # TODO: https://forum.unity.com/threads/2d-tile-bitmasking.513840/#post-3366221
    bitmask = cardinals + (diagonals << 4)
    return bitmask


def bitmask_walls(walls, revealed=None):
    """Return 4-bit bitmask for walls neighbours."""
    # First revealed walls, we are sure these are walls
    shape, padded = shape_padded(walls & revealed)
    cardinals = get_cardinals(shape, padded)
    diagonals = get_diagonals(shape, padded)

    bitmask = cardinals.copy()
    # Tees to straight lines
    bitmask ^= (is_set(cardinals, Cardinal.WEN) & is_set(diagonals, Diagonal.N)) << 0
    bitmask ^= (is_set(cardinals, Cardinal.WES) & is_set(diagonals, Diagonal.S)) << 1
    bitmask ^= (is_set(cardinals, Cardinal.NSW) & is_set(diagonals, Diagonal.W)) << 2
    bitmask ^= (is_set(cardinals, Cardinal.NSE) & is_set(diagonals, Diagonal.E)) << 3

    # Now let's assume that what is not yet revealed might be wall as well
    shape, padded = shape_padded((walls & revealed) | ~revealed, pad_value=True)
    cardinals = bitmask.copy()
    diagonals = get_diagonals(shape, padded)

    # Tees to straight lines
    bitmask ^= (is_set(cardinals, Cardinal.WEN) & is_set(diagonals, Diagonal.N)) << 0
    bitmask ^= (is_set(cardinals, Cardinal.WES) & is_set(diagonals, Diagonal.S)) << 1
    bitmask ^= (is_set(cardinals, Cardinal.NSW) & is_set(diagonals, Diagonal.W)) << 2
    bitmask ^= (is_set(cardinals, Cardinal.NSE) & is_set(diagonals, Diagonal.E)) << 3

    # Next step will mess crosses up...
    crosses = cardinals == Cardinal.NSWE

    cardinals = get_cardinals(shape, padded)

    # Tees to corners NOTE: Breaks crosses, need to fix them later!
    bitmask_nsw = is_set(bitmask, Cardinal.NSW)
    bitmask_nse = is_set(bitmask, Cardinal.NSE)
    bitmask_wen = is_set(bitmask, Cardinal.WEN)
    bitmask_wes = is_set(bitmask, Cardinal.WES)

    cardinals_ne = is_set(cardinals, Cardinal.NE)
    cardinals_nw = is_set(cardinals, Cardinal.NW)
    cardinals_se = is_set(cardinals, Cardinal.SE)
    cardinals_sw = is_set(cardinals, Cardinal.SW)

    diagonals_ne = is_set(diagonals, Diagonal.NE)
    diagonals_nw = is_set(diagonals, Diagonal.NW)
    diagonals_se = is_set(diagonals, Diagonal.SE)
    diagonals_sw = is_set(diagonals, Diagonal.SW)

    bitmask ^= (bitmask_nsw & cardinals_ne & diagonals_nw) << 0
    bitmask ^= (bitmask_nsw & cardinals_se & diagonals_sw) << 1

    bitmask ^= (bitmask_nse & cardinals_nw & diagonals_ne) << 0
    bitmask ^= (bitmask_nse & cardinals_sw & diagonals_se) << 1

    bitmask ^= (bitmask_wen & cardinals_se & diagonals_ne) << 3
    bitmask ^= (bitmask_wen & cardinals_sw & diagonals_nw) << 2

    bitmask ^= (bitmask_wes & cardinals_ne & diagonals_se) << 3
    bitmask ^= (bitmask_wes & cardinals_nw & diagonals_sw) << 2

    # Fix crosses!
    bitmask[crosses] = Cardinal.NSWE

    return bitmask

