from enum import IntFlag
import collections

from ..tiles import Glyph


"""Basic UI elements / building blocks, working as abstraction layer for tcod.Console.

This should make working on UI much easier, and maybe allow to use other cli/graphical engines.

"""


EMPTY_TILE = Glyph(' ')


class ZOrder:
    BASE = 1
    MODAL = 100


class Align(IntFlag):
    # Horizontal alignment
    LEFT = 0    # tcod.LEFT
    RIGHT = 1   # tcod.RIGHT
    CENTER = 2  # tcod.CENTER

    # Vertical alignment
    TOP = 4
    BOTTOM = 8
    MIDDLE = CENTER

    # Horizontal + Vertical combinations
    TOP_LEFT = LEFT | TOP
    TOP_CENTER = CENTER | TOP
    TOP_RIGHT = RIGHT | TOP

    MIDDLE_LEFT = LEFT | MIDDLE
    CENTERED = CENTER | MIDDLE
    MIDDLE_RIGHT = RIGHT | MIDDLE

    BOTTOM_LEFT = LEFT | BOTTOM
    BOTTOM_CENTER = CENTER | BOTTOM
    BOTTOM_RIGHT = RIGHT | BOTTOM


class Padding(collections.namedtuple(
    'Padding', [
        'top', 'right', 'bottom', 'left',
    ])):

    __slots__ = ()

    def __new__(cls, top=None, right=None, bottom=None, left=None):
        top = top or 0
        if right is None:
            right = top
        if bottom is None:
            bottom = top
        if left is None:
            left = right
        return super().__new__(cls, top, right, bottom, left)

Padding.ZERO = Padding(0, 0, 0, 0)

