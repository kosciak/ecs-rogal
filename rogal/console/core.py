from enum import IntFlag
import collections


"""Basic UI elements / building blocks, working as abstraction layer for tcod.Console.

This should make working on UI much easier, and maybe allow to use other cli/graphical engines.

"""


class Glyph(int):

    __slots__ = ()

    __INSTANCES = {}

    def __new__(cls, code_point):
        if code_point is None:
            return None
        if isinstance(code_point, Glyph):
            return code_point
        if isinstance(code_point, str):
            code_point = ord(code_point)
        instance = cls.__INSTANCES.get(code_point)
        if not instance:
            instance = super().__new__(cls, code_point)
            cls.__INSTANCES[code_point] = instance
        return instance

    @property
    def char(self):
        return chr(self)

    def __str__(self):
        return self.char

    def __repr__(self):
        return f'<Glyph {self:d} = "{self.char}">'


class Colors(collections.namedtuple(
    'Colors', [
        'fg',
        'bg',
    ])):

    def __new__(cls, fg=None, bg=None):
        if fg is None and bg is None:
            return None
        return super().__new__(cls, fg, bg)

    def invert(self):
        return Colors(self.bg, self.fg)


class HasColorsMixin:

    @property
    def fg(self):
        return self.colors and self.colors.fg

    @property
    def bg(self):
        return self.colors and self.colors.bg


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

