import collections

import numpy as np

from .. import dtypes
from ..geometry import Position, Size, WithSizeMixin, Rectangular, split_rect
from ..colors import RGB, Color
from ..tiles import Tile, Colors


"""Basic UI elements / building blocks, working as abstraction layer for tcod.Console.

This should make working on UI much easier, and maybe allow to use other cli/graphical engines.

"""

DEFAULT_CH = ord(' ')
DEFAULT_FG = RGB(255, 255, 255).rgb
DEFAULT_BG = RGB(0, 0, 0).rgb


class Alignment:
    LEFT = 0    # tcod.LEFT
    RIGHT = 1   # tcod.RIGHT
    CENTER = 2  # tcod.CENTER


class Console:

    def __init__(self, size):
        self.tiles_rgb = np.zeros(size, dtype=dtypes.rgb_console_dt, order="C")
        self.ch[...] = DEFAULT_CH
        self.fg[...] = DEFAULT_FG
        self.bg[...] = DEFAULT_BG

    @property
    def width(self):
        return self.tiles_rgb.shape[1]

    @property
    def height(self):
        return self.tiles_rgb.shape[0]

    @property
    def ch(self):
        return self.tiles_rgb['ch']

    @property
    def fg(self):
        return self.tiles_rgb['fg']

    @property
    def bg(self):
        return self.tiles_rgb['bg']


class TilesGrid(WithSizeMixin):

    """Representation of rectangular Tiles based drawing area."""

    __slots__ = ()

    def _empty_tile(self, colors):
        fg = (colors and colors.fg) or DEFAULT_FG
        bg = (colors and colors.bg) or DEFAULT_BG
        return Tile.create(DEFAULT_CH, fg=fg, bg=bg)

    def clear(self, colors=None, *args, **kwargs):
        """Clear whole area with default values."""
        tile = self._empty_tile(colors)
        return self.fill(tile)

    def print(self, text, position, colors=None, alignment=None, *args, **kwargs):
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

    # NOTE: Only position is translated, it is NOT checked if prints are outside of Panel!

    def create_panel(self, position, size):
        return self.root.create_panel(self.offset(position), size)

    def split(self, left=None, right=None, top=None, bottom=None):
        """Split Panel vertically or horizontally."""
        geometries = split_rect(self, left, right, top, bottom)
        panels = [self.root.create_panel(*geometry) for geometry in geometries]
        return panels

    def print(self, text, position, colors=None, alignment=None, *args, **kwargs):
        """Print text on given position using colors."""
        return self.root.print(text, self.offset(position), colors=colors, alignment=alignment, *args, **kwargs)

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

    def _empty_tile(self, colors):
        fg = self.rgb(colors and colors.fg) or self.palette.fg
        bg = self.rgb(colors and colors.bg) or self.palette.bg
        return Tile.create(DEFAULT_CH, fg=fg, bg=bg)

    def create_panel(self, position, size):
        return Panel(self, position, size)

    def rgb(self, color):
        if not color:
            return None
        if isinstance(color, Color):
            return color.rgb
        if isinstance(color, tuple):
            if len(color) == 3:
                return color
            else:
                return color[:3]
        return self.palette.get(color).rgb

    def clear(self, colors=None, *args, **kwargs):
        fg = self.rgb(colors and colors.fg) or self.palette.fg.rgb
        bg = self.rgb(colors and colors.bg) or self.palette.bg.rgb
        self.console.tiles_rgb[...] = (DEFAULT_CH, fg, bg)

    def _draw(self, ch, colors, position, size=None, *args, **kwargs):
        fg = self.rgb(colors.fg)
        bg = self.rgb(colors.bg)
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

    def _print_line(self, text, position, colors=None, alignment=None, *args, **kwargs):
        chars = [ord(ch) for ch in text]
        fg = self.rgb(colors and colors.fg)
        bg = self.rgb(colors and colors.bg)
        alignment = alignment or Alignment.LEFT
        # NOTE: console is in order="C", so we need to do some transpositions
        j, i = position
        if alignment == Alignment.LEFT:
            max_len = self.console.width - j
            chars = chars[:max_len]
        elif alignment == Alignment.RIGHT:
            max_len = j+1
            chars = chars[len(chars)-max_len:]
            j = max(0, j-len(chars))
        elif alignment == Alignment.CENTER:
            max_len = self.console.width
            if len(chars) > max_len:
                chars = chars[len(chars)//2-(max_len//2):len(chars)//2+max_len//2+1]
            j = max(0, j-(len(chars)//2))
        self.console.ch[i, j:j+len(chars)] = chars
        if fg:
            self.console.fg[i, j:j+len(chars)] = fg
        if bg:
            self.console.bg[i, j:j+len(chars)] = bg

    def print(self, text, position, colors=None, alignment=None, *args, **kwargs):
        for line in text.splitlines():
            self._print_line(line, position, colors=colors, alignment=alignment, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        self._draw(tile.ch, tile.colors, position, size=size, *args, **kwargs)

    def paint(self, colors, position, size=None, *args, **kwargs):
        self._draw(None, colors, position, size=size, *args, **kwargs)

    def mask(self, tile, mask, position=None):
        position = position or Position.ZERO
        fg = self.rgb(tile.fg)
        bg = self.rgb(tile.bg)
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

