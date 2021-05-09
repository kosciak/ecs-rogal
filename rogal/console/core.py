from enum import IntFlag
import collections
import functools

import numpy as np

from .. import dtypes
from ..geometry import Position, Size, WithSizeMixin, Rectangular, split_rect
from ..colors import RGB, Color
from ..tiles import Tile, Colors


"""Basic UI elements / building blocks, working as abstraction layer for tcod.Console.

This should make working on UI much easier, and maybe allow to use other cli/graphical engines.

"""


DEFAULT_CH = ord(' ')


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


def get_x(panel_width, width, align, padding=Padding.ZERO):
    if align & Align.RIGHT:
        x = panel_width - width - padding.right
    elif align & Align.CENTER:
        x = panel_width//2 - width//2 - padding.right + padding.left
    else:
        x = padding.left
    return x


def get_align_x(panel_width, width, align, padding=Padding.ZERO):
    if align & Align.RIGHT:
        x = panel_width - padding.right - 1
    elif align & Align.CENTER:
        x = panel_width//2 - padding.right + padding.left
    else:
        x = padding.left
    return x


def get_y(panel_height, height, align, padding=Padding.ZERO):
    if align & Align.TOP:
        y = padding.top
    elif align & Align.BOTTOM:
        y = panel_height - height - padding.bottom
    elif align & Align.MIDDLE:
        y = panel_height//2 - height//2 - padding.bottom + padding.top
    else:
        y = padding.top
    return y


class Console:

    TILES_DTYPE = None
    DEFAULT_FG = None
    DEFAULT_BG = None

    def __init__(self, size):
        size = Size(size.height, size.width)
        self.tiles = np.zeros(size, dtype=self.TILES_DTYPE, order="C")
        self.tiles[...] = (DEFAULT_CH, self.DEFAULT_FG, self.DEFAULT_BG)

    @property
    def width(self):
        return self.tiles.shape[1]

    @property
    def height(self):
        return self.tiles.shape[0]

    @property
    def ch(self):
        return self.tiles['ch']

    @property
    def fg(self):
        return self.tiles['fg']

    @property
    def bg(self):
        return self.tiles['bg']


class ConsoleRGB(Console):

    TILES_DTYPE = dtypes.CONSOLE_RGB_DT
    DEFAULT_FG = RGB(255, 255, 255).rgb
    DEFAULT_BG = RGB(0, 0, 0).rgb

    def tiles_gen(self, encode_ch=int):
        for tile in np.nditer(self.tiles, flags=['refs_ok']):
            # yield encode_ch(tile['ch']), int(tile['fg']), int(tile['bg'])
            yield encode_ch(tile['ch']), tile['fg'], tile['bg']


class ConsoleIndexedColors(Console):

    TILES_DTYPE = dtypes.TILES_INDEXED_COLORS_DT
    DEFAULT_FG = -1
    DEFAULT_BG = -1

    def tiles_gen(self, encode_ch=int):
        for tile in np.nditer(self.tiles, flags=['refs_ok']):
            yield encode_ch(tile['ch']), int(tile['fg']), int(tile['bg'])


class TilesGrid(WithSizeMixin):

    """Representation of rectangular Tiles based drawing area."""

    __slots__ = ()

    def _empty_tile(self, colors):
        fg = (colors and colors.fg)# or DEFAULT_FG
        bg = (colors and colors.bg)# or DEFAULT_BG
        return Tile.create(DEFAULT_CH, fg=fg, bg=bg)

    def clear(self, colors=None, *args, **kwargs):
        """Clear whole area with default values."""
        tile = self._empty_tile(colors)
        return self.fill(tile)

    def print(self, text, position, colors=None, align=None, *args, **kwargs):
        """Print text on given Position.

        Use Colors if provided, otherwise don't change alredy defined fg and bg.

        """
        raise NotImplementedError()

    def draw(self, tile, position, size=None, *args, **kwargs):
        """Draw Tile on given position.

        If size provided draw rectangle filled with this Tile.

        """
        raise NotImplementedError()

    def fill(self, tile, *args, **kwargs):
        """Fill whole area with given Tile."""
        return self.draw(tile, Position.ZERO, size=self.size, *args, **kwargs)

    def paint(self, colors, position, size=None, *args, **kwargs):
        """Paint Colors on given position.

        If size provided paint rectangle using these Colors.

        """
        raise NotImplementedError()

    def invert(self, position, size=None, *args, **kwargs):
        """Invert Colors on given position.

        If size provided invert color on rectangle.

        """
        raise NotImplementedError()

    def mask(self, tile, mask, position=None, *args, **kwargs):
        """Draw Tile on positions where mask is True, startig on position."""
        raise NotImplementedError()

    def image(self, image, position=None, *args, **kwargs):
        """Draw image on given position."""
        raise NotImplementedError()

    # TODO: blit_from, blit_to


class Panel(Rectangular, TilesGrid):

    """Representation of rectangular part of Tiles based drawing area.

    Allows manipulation of data using local coordinates (relative to self).
    NOTE: center() returns Position relative to self so it can be used in draw/paint methods.

    """

    __slots__ = ('position', 'size', 'root', )

    def __init__(self, root, offset, size):
        self.position = offset
        self.size = size
        self.root = root

    @property
    def center(self):
        """Return center Position relative to self!"""
        return super(Rectangular, self).center

    def offset(self, position, root=None):
        """Return Position relative to root.

        self.offset(local_pos) -> pos relative to root
        root.offset(pos, panel) -> local_pos relative to panel
        self.offset(local_pos, other) -> pos relative to other

        """
        offset = self.position + position
        if root and not root == self.root:
            offset -= root
        return offset

    def get_position(self, size, align, padding=Padding.ZERO):
        """Return Position (top-left) where widget would be placed."""
        return Position(
            get_x(self.width, size.width, align, padding),
            get_y(self.height, size.height, align, padding)
        )

    def get_align_position(self, size, align, padding=Padding.ZERO):
        """Return Position (of alignment point) where widget would be placed."""
        return Position(
            get_align_x(self.width, size.width, align, padding),
            get_y(self.height, size.height, align, padding)
        )

    # NOTE: Only position is translated, it is NOT checked if prints are outside of Panel!

    def create_panel(self, position, size):
        return self.root.create_panel(self.offset(position), size)

    def split(self, left=None, right=None, top=None, bottom=None):
        """Split Panel vertically or horizontally."""
        geometries = split_rect(self, left, right, top, bottom)
        panels = [self.root.create_panel(*geometry) for geometry in geometries]
        return panels

    def print(self, text, position, colors=None, align=None, *args, **kwargs):
        """Print text on given position using colors."""
        align = (align or Align.LEFT) & (Align.LEFT|Align.RIGHT|Align.CENTER)
        return self.root.print(text, self.offset(position), colors=colors, align=align, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        """Draw Tile on given position.

        If size provided draw rectangle filled with this Tile.

        """
        if not tile:
            return
        return self.root.draw(tile, self.offset(position), size=size, *args, **kwargs)

    def paint(self, colors, position, size=None, *args, **kwargs):
        """Paint Colors on given position.

        If size provided paint rectangle using these Colors.

        """
        return self.root.paint(colors, self.offset(position), size=size, *args, **kwargs)

    def invert(self, position, size=None, *args, **kwargs):
        """Invert Colors on given position.

        If size provided invert color on rectangle.

        """
        return self.root.invert(self.offset(position), size=size, *args, **kwargs)

    def mask(self, tile, mask, position=None, *args, **kwargs):
        """Draw Tile on positions where mask is True, startig on position."""
        position = position or Position.ZERO
        return self.root.mask(tile, mask, self.offset(position), *args, **kwargs)

    def image(self, image, position=None, *args, **kwargs):
        """Draw image on given position."""
        position = position or Position.ZERO
        return self.root.image(image, self.offset(position), *args, **kwargs)

    # Other methods

    # TODO: get_tile(self, position)
    # TODO: get_char(self, position)
    # TODO: get_colors(self, position)

    def __repr__(self):
        return f'<{self.__class__.__name__} x={self.x}, y={self.y}, width={self.width}, height={self.height}>'


class RootPanel(Panel):

    def __init__(self, console, palette):
        super().__init__(self, Position.ZERO, Size(console.width, console.height))
        self.console = console
        self.palette = palette
        self.clear()

    def get_fg_bg(self, colors):
        fg = self.get_color(colors and colors.fg)
        if fg is None:
            fg = self.get_color(self.palette.fg)
        bg = self.get_color(colors and colors.bg)
        if bg is None:
            bg = self.get_color(self.palette.bg)
        return fg, bg

    def _empty_tile(self, colors):
        fg, bg = self.get_fg_bg(colors)
        return Tile.create(DEFAULT_CH, fg=fg, bg=bg)

    def create_panel(self, position, size):
        return Panel(self, position, size)

    @functools.lru_cache(maxsize=None)
    def get_color(self, color):
        if color is None:
            return None
        if isinstance(color, Color):
            return color.rgb
        if isinstance(color, (tuple, list)):
            if len(color) == 3:
                return color
            else:
                return color[:3]
        return self.palette.get(color).rgb

    def clear(self, colors=None, *args, **kwargs):
        fg, bg = self.get_fg_bg(colors)
        self.console.tiles[...] = (DEFAULT_CH, fg, bg)

    def _draw(self, ch, colors, position, size=None, *args, **kwargs):
        fg = self.get_color(colors and colors.fg)
        bg = self.get_color(colors and colors.bg)
        # NOTE: console is in order="C", so we need to do some transpositions
        j, i = position
        if size:
            height, width = size
            if ch is not None:
                self.console.ch[i:i+width, j:j+height] = ch
            if fg:
                self.console.fg[i:i+width, j:j+height] = fg
            if bg:
                self.console.bg[i:i+width, j:j+height] = bg
        else:
            if ch is not None:
                self.console.ch[i, j] = ch
            if fg:
                self.console.fg[i, j] = fg
            if bg:
                self.console.bg[i, j] = bg

    def _print_line(self, text, position, colors=None, align=None, *args, **kwargs):
        chars = [ord(ch) for ch in text]
        fg = self.get_color(colors and colors.fg)
        bg = self.get_color(colors and colors.bg)
        align = align or Align.LEFT
        # NOTE: console is in order="C", so we need to do some transpositions
        j, i = position
        if align & Align.RIGHT:
            max_len = j+1
            chars = chars[len(chars)-max_len:]
            j = max(0, j-len(chars))
        elif align & Align.CENTER:
            max_len = self.console.width
            if len(chars) > max_len:
                chars = chars[len(chars)//2-(max_len//2):len(chars)//2+max_len//2+1]
            j = max(0, j-(len(chars)//2))
        else:
            max_len = self.console.width - j
            chars = chars[:max_len]
        self.console.ch[i, j:j+len(chars)] = chars
        if fg:
            self.console.fg[i, j:j+len(chars)] = fg
        if bg:
            self.console.bg[i, j:j+len(chars)] = bg

    def print(self, text, position, colors=None, align=None, *args, **kwargs):
        for line in text.splitlines():
            self._print_line(line, position, colors=colors, align=align, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        self._draw(tile.ch, tile.colors, position, size=size, *args, **kwargs)

    def paint(self, colors, position, size=None, *args, **kwargs):
        self._draw(None, colors, position, size=size, *args, **kwargs)

    def invert(self, position, size=None, *args, **kwargs):
        # NOTE: console is in order="C", so we need to do some transpositions
        j, i = position
        if size:
            height, width = size
            fg = self.console.fg[i:i+width, j:j+height].copy()
            bg = self.console.bg[i:i+width, j:j+height].copy()
            self.console.fg[i:i+width, j:j+height] = bg
            self.console.bg[i:i+width, j:j+height] = fg
        else:
            fg = np.copy(self.console.fg[i, j])
            bg = np.copy(self.console.bg[i, j])
            self.console.fg[i, j] = bg
            self.console.bg[i, j] = fg

    def mask(self, tile, mask, position=None):
        position = position or Position.ZERO
        fg = self.get_color(tile.fg)
        bg = self.get_color(tile.bg)
        # NOTE: console is in order="C", so we need to do some transpositions
        j, i = position
        mask = mask.transpose()
        width, height = mask.shape
        self.console.ch[i:i+width, j:j+height][mask] = tile.ch
        if fg:
            self.console.fg[i:i+width, j:j+height][mask] = fg
        if bg:
            self.console.bg[i:i+width, j:j+height][mask] = bg


# TODO: Support for bg_blend, learn how it works in tcod

# TODO: ansi-like color control codes - "%c%c%c%cFoo%c" % (tcod.COLCTRL_FORE_RGB, *tcod.white, tcod.COLCTRL_STOP)

