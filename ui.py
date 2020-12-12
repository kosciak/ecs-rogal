import collections

from geometry import Position, Size, WithSizeMixin, Rectangle
from colors import RGB
from tiles import Tile, Colors


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


class AbstractTilesGrid(WithSizeMixin):

    """Representation of rectangular Tiles based drawing area."""

    __slots__ = ()

    def empty_tile(self, colors):
        fg = (colors and colors.fg) or DEFAULT_FG
        bg = (colors and colors.bg) or DEFAULT_bG
        return Tile.create(DEFAULT_CH, fg=fg, bg=bg)

    def clear(self, colors=None, *args, **kwargs):
        """Clear whole Rectangle wigh default values."""
        tile = self.empty_tile(colors)
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

    def image(self, image, position=None, *args, **kwargs):
        """Draw image on given position."""
        raise NotImplementedError()

    # TODO: blit_from, blit_to


class Panel(AbstractTilesGrid, Rectangle):

    """Representation of rectangular Tiles based drawing area.
    
    Allows manipulation of data using local coordinates (relative to self).

    """

    def __init__(self, root, offset, size):
        # NOTE: position is relative to parent
        #       offset is relative to root
        super().__init__(offset, size)
        self.root = root

    def _root_offset(self, position):
        """Translate local coordinates (relative to self) to coordinates relative to root panel."""
        #return Position(self.offset.x+position.x, self.offset.y+position.y)
        return Position(self.x+position.x, self.y+position.y)

    # NOTE: Only position is translated, it is NOT checked if prints are outside of Panel!

    def create_panel(self, position, size):
        offset = self._root_offset(position)
        return self.root.create_panel(offset, size)

    def print(self, text, position, colors=None, alignment=None, *args, **kwargs):
        """Print text on given position using colors."""
        offset = self._root_offset(position)
        return self.root.print(text, offset, colors=colors, alignment=alignment, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        """Draw Tile on given position.

        If size provided draw rectangle filled with this Tile.

        """
        offset = self._root_offset(position)
        return self.root.draw(tile, offset, size=size, *args, **kwargs)

    def paint(self, colors, position, size=None, *args, **kwargs):
        """Paint Colors on given position.

        If size provided paint rectangle using these Colors.

        """
        offset = self._root_offset(position)
        return self.root.paint(colors, position, size=size, *args, **kwargs)

    def image(self, image, position=None, *args, **kwargs):
        """Draw image on given position."""
        position = position or Position.ZERO
        offset = self._root_offset(position)
        return self.root.image(image, offset, *args, **kwargs)

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
        height = top or bottom
        if height and height < 1:
            height = int(self.height * height)
        if top:
            top = self.create_panel(
                Position.ZERO, 
                Size(self.width, self.height-height),
            )
            bottom = self.create_panel(
                Position(0, self.height-height), 
                Size(self.width, height),
            )
            self.panels = [top, bottom]
            return top, bottom
        elif bottom:
            top = self.create_panel(
                Position.ZERO,
                Size(self.width, height),
            )
            bottom = self.create_panel(
                Position(0, height),
                Size(self.width, self.height-height),
            )
            self.panels = [top, bottom]
            return top, bottom


class VerticalContainer(Container):

    def split(self, left=None, right=None):
        width = left or right
        if width and width < 1:
            width = int(self.width * width)
        if left:
            left = self.create_panel(
                Position.ZERO,
                Size(self.width-width, self.height),
            )
            right = self.create_panel(
                Position(self.width-width, 0), 
                Size(width, self.height),
            )
            self.panels = [left, right]
            return left, right
        elif right:
            left = self.create_panel(
                Position.ZERO, 
                Size(width, self.height),
            )
            right = self.create_panel(
                Position(width, 0), 
                Size(self.width-width, self.height),
            )
            self.panels = [left, right]
            return left, right


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

    def empty_tile(self, colors):
        fg = self.rgb(colors and colors.fg) or self.palette.fg
        bg = self.rgb(colors and colors.bg) or self.palette.bg
        return Tile.create(DEFAULT_CH, fg=fg, bg=bg)

    def create_panel(self, position, size):
        return SplittablePanel(self, position, size)

    def rgb(self, color):
        if not color:
            return None
        if isinstance(color, tuple):
            if len(color) == 3:
                return color
            else:
                return color[:3]
        return self.palette.get(color).rgb


# TODO: Move to ui.tcod_wrapper ?
class TcodRootPanel(RootPanel):

    def __str__(self):
        return str(self.console)

    def clear(self, colors=None, *args, **kwargs):
        fg = self.rgb(colors and colors.fg) or self.palette.fg.rgb
        bg = self.rgb(colors and colors.bg) or self.palette.bg.rgb
        return self._clear(fg=fg, bg=bg, *args, **kwargs)

    def print(self, text, position, colors=None, alignment=None, *args, **kwargs):
        # NOTE: Do NOT change already set colors!
        fg = self.rgb(colors and colors.fg)
        bg = self.rgb(colors and colors.bg)
        alignment = alignment or Alignment.LEFT
        return self._print(
            position.x, position.y, text, fg=fg, bg=bg, alignment=alignment, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        fg = self.rgb(tile.fg)
        bg = self.rgb(tile.bg)
        if size:
            return self._draw_rect(
                position.x, position.y, size.width, size.height, tile.code_point, 
                fg=fg, bg=bg, *args, **kwargs)
        else:
            return self._print(
                position.x, position.y, tile.ch, fg=fg, bg=bg, *args, **kwargs)

    def paint(self, colors, position, size=None, *args, **kwargs):
        fg = self.rgb(colors.fg)
        bg = self.rgb(colors.bg)
        if size:
            if fg:
                self.console.fg[position.x:position.x+size.width, position.y:position.y+size.height] = fg
            if bg:
                self.console.bg[position.x:position.x+size.width, position.y:position.y+size.height] = bg
        else:
            if fg:
                self.console.fg[position] = fg
            if bg:
                self.console.bg[position] = bg

    def image(self, image, position, *args, **kwargs):
        return self._draw_semigraphics(
            image, position.x, position.y, *args, **kwargs)

    # TODO: Needs rework using Position, Size!
    def blit_from(self, x, y, src, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: src MUST be tcod.Console!
        src.blit(dest=self.console, dest_x=x, dest_y=y, *args, **kwargs)

    def blit_to(self, x, y, dest, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: dest MUST be tcod.Console!
        self.console.blit(dest=dest, src_x=x, src_y=y, *args, **kwargs)

    # NOTE: tcod.Console print/draw related methods:

    def _put_char(self, x, y, ch, *args, **kwargs):
        """tcod.Console.put_char(
            x: int, y: int, 
            ch: int, 
            bg_blend: int = 13)
        """
        return self.console.put_char(x, y, ch, *args, **kwargs)

    def _print(self, x, y, text, fg=None, bg=None, *args, **kwargs):
        """tcod.Cosole.print(
            x: int, y: int, 
            string: str, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1, 
            alignment: int = 0)
        """
        return self.console.print(
            x, y, text, fg=fg, bg=bg, *args, **kwargs)

    def _print_box(self, x, y, width, height, text, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.print_box(
            x: int, y: int, 
            width: int, height: int, 
            string: str, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1, 
            alignment: int = 0)-> int
        """
        return self.console.print_box(
            x, y, width, height, text, fg=fg, bg=bg, *args, **kwargs)

    def _get_height_rect(self, x, y, width, height, text, *args, **kwargs):
        """tcod.Console.get_height_rect(
            x: int, y: int, 
            width: int, height: int, 
            string: str)-> int
        """
        return self.console.get_height_rect(
            x, y, width, height, text, *args, **kwargs)

    def _draw_rect(self, x, y, width, height, ch, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.draw_rect(
            x: int, y: int, 
            width: int, height: int, 
            ch: int, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1)
        """
        return self.console.draw_rect(
            x, y, width, height, ch, fg=fg, bg=bg, *args, **kwargs)

    def _draw_frame(self, x, y, width, height, title=None, clear=True, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.draw_frame(
            x: int, y: int, 
            width: int, height: int, 
            title: str = '', 
            clear: bool = True, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1)
        """
        return self.console.draw_frame(
            x, y, width, height, title=title, clear=clear, fg=fg, bg=bg, *args, **kwargs)

    def _draw_semigraphics(self, pixels, x, y, *args, **kwargs):
        """tcod.Console.draw_semigraphics(
            pixels: Any, 
            x: int = 0, 
            y: int = 0)
        """
        return self.console.get_height_rect(pixels, x, y, *args, **kwargs)

    def _clear(self, ch=None, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.clear(
            ch: int = 32, 
            fg: Tuple[int, int, int] = Ellipsis, 
            bg: Tuple[int, int, int] = Ellipsis)
        """
        ch = ch or DEFAULT_CH
        return self.console.clear(ch, fg=fg, bg=bg, *args, **kwargs)

    # blit(
    #   dest: tcod.console.Console, 
    #   dest_x: int = 0, dest_y: int = 0, 
    #   src_x: int = 0, src_y: int = 0, 
    #   width: int = 0, height: int = 0, 
    #   fg_alpha: float = 1.0, 
    #   bg_alpha: float = 1.0, 
    #   key_color: Optional[Tuple[int, int, int]] = None)

    # NOTE: Direct access to console.tiles, console.tiles_rgb fragments
    # NOTE: you can acces bg, fg, chr as tiles_rgb['bg'], tiles_rgb['fg'], tiles['ch']

    @property
    def tiles(self):
        """Translate coordinates relative to self, to coordinates relative to root."""
        return self.parent.tiles[self.x:self.x2, self.y:self.y2]

    @tiles.setter
    def tiles(self, tiles):
        self.parent.tiles[self.x:self.x2, self.y:self.y2] = tiles

    @property
    def tiles_rgb(self):
        return self.parent.tiles_rgb[self.x:self.x2, self.y:self.y2]

    @tiles_rgb.setter
    def tiles_rgb(self, tiles_rgb):
        self.parent.tiles_rgb[self.x:self.x2, self.y:self.y2] = tiles_rgb

    def show(self):
        import ansi
        for row in self.console.tiles_rgb.transpose():
            row_txt = []
            for ch, fg, bg in row:
                row_txt.append(ansi.fg_rgb(*fg)+ansi.bg_rgb(*bg)+chr(ch)+ansi.reset())
            print(''.join(row_txt))


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

