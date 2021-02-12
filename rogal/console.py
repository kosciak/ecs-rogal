import collections

import numpy as np

from . import dtypes

from .geometry import Position, Size, WithSizeMixin, Rectangular, Rectangle
from .geometry import split_vertical, split_horizontal
from .colors import RGB, Color
from .renderable import Tile, Colors


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
        # NOTE: position is relative to parent
        #       offset is relative to root
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

    def framed(self, title=None):
        """Draw generic frame (with optional title) and return panel inside the frame."""
        # TODO: !!!
        self.root._draw_frame(self.position.x, self.position.y, self.width, self.height,
                              title=title, clear=False)
        return self.create_panel(Position(1,1), Size(self.width-2, self.height-2))

    def print(self, text, position, colors=None, alignment=None, *args, **kwargs):
        """Print text on given position using colors."""
        return self.root.print(text, self.offset(position), colors=colors, alignment=alignment, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        """Draw Tile on given position.

        If size provided draw rectangle filled with this Tile.

        """
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


class Container(Panel):

    def __init__(self, root, offset, size):
        super().__init__(root, offset, size)
        self.panels = []


class HorizontalContainer(Container):

    def split(self, top=None, bottom=None):
        top, bottom = split_horizontal(self, top=top, bottom=bottom)
        self.panels = [
            self.root.create_panel(top.position, top.size),
            self.root.create_panel(bottom.position, bottom.size),
        ]
        return self.panels


class VerticalContainer(Container):

    def split(self, left=None, right=None):
        left, right = split_vertical(self, left=left, right=right)
        self.panels = [
            self.root.create_panel(left.position, left.size),
            self.root.create_panel(right.position, right.size),
        ]
        return self.panels


class SplittablePanel(Panel):

    def split_vertical(self, left=None, right=None):
        width = left or right
        container = VerticalContainer(
            self.root,
            self.position,
            self.size,
        )
        return container.split(left=right and width, right=left and width)

    def split_horizontal(self, top=None, bottom=None):
        height = top or bottom
        container = HorizontalContainer(
            self.root,
            self.position,
            self.size,
        )
        return container.split(top=bottom and height, bottom=top and height)

    def split(self, left=None, right=None, top=None, bottom=None):
        """Split Panel vertically or horizontally by providing width of new Panel
           placed to the right / left / top / bottom."""
        if left or right:
            return self.split_vertical(left=left, right=right)
        if top or bottom:
            return self.split_horizontal(top=top, bottom=bottom)


class RootPanel(SplittablePanel):

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
        return SplittablePanel(self, position, size)

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

# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations

# TODO: Keep track of Z-order of Windows?

# TODO: Scrollable Panels?
# TODO: Window/Dialog?
# TODO: event handlers?


# TODO: frame() should produce FramedPanel with Frame and Panel inside
# TODO: Rework FramedWindow class - now it's a mess

FrameDecorations = collections.namedtuple(
    'FrameDecorations', [
        'top', 'bottom', 'side',
        'top_left', 'top_right',
        'bottom_left', 'bottom_right',
    ])


DECORATIONS_ASCII = FrameDecorations(*"=-|..''")


class Frame(Container):
    # TODO: Custom window decorations?
    # TODO: Setting title, adding buttons(?) on top/bottom border, scrollbars?
    #       For example setting things like: 
    #       .- Title ------[X]-.
    #       |                  |
    #       '-----------(more)-'

    def draw_decorations(self, decorations=None, *args, **kwargs):
        if not decorations:
            self.draw_frame(0, 0, width=self.width, height=self.height, *args, **kwargs)
        else:
            self.draw_rect(1, 0, width=self.width-2, height=1, ch=ord(decorations.top))
            self.draw_rect(1, self.height-1, width=self.width-2, height=1, ch=ord(decorations.bottom))
            self.draw_rect(0, 1, width=1, height=self.height-2, ch=ord(decorations.side))
            self.draw_rect(self.width-1, 1, width=1, height=self.height-2, ch=ord(decorations.side))
            self.put_char(0, 0, ord(decorations.top_left))
            self.put_char(self.width-1, 0, ord(decorations.top_right))
            self.put_char(0, self.height-1, ord(decorations.bottom_left))
            self.put_char(self.width-1, self.height-1, ord(decorations.bottom_right))


class FramedWindow:
    # TODO: For now it's just proof of concept
    # NOTE: splitting window.panel leaves original panel reference!

    def __init__(self, parent, x, y, width, height, decorations):
        self.frame = Frame(parent, Position(x, y), Size(width, height))
        self.frame.draw_decorations(decorations)
        self.panel = SplittablePanel(self.frame, Position(1, 1), Size(width-2, height-2))
        self.frame.panels.append(self.panel)

