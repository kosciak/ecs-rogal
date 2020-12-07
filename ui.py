import collections

from geometry import Position, Size, Rectangle


"""Basic UI elements / building blocks, working as abstraction layer for tcod.Console.

This should make working on UI much easier, and maybe use other cli/graphical engines.

"""


class TilesGrid(Rectangle):

    """Representation of rectangular drawing area.
    
    Allows manipulation of data using local coordinates (relative to self).
    Using print/draw methods from tcod.Console.

    """

    def __init__(self, parent, position, size):
        # NOTE: position is relative to parent
        super().__init__(position, size)
        self.parent = parent

    # TODO: Rename to: _parent_offset(self, x, y)
    def _translate_parent(self, x, y):
        """Translate local coordinates (relative to self) to coordinates relative to parent."""
        parent_x = self.x + x
        parent_y = self.y + y
        #print('_translate_parent:',x,y,'->',parent_x,parent_y, '?', self)
        return parent_x, parent_y

    # TODO: Rename to: _root_offset(self, x, y)
    def _translate_root(self, x, y):
        """Translate local coordinates (relative to self) to coordinates relative to root panel."""
        return self.parent._translate_root(self.x+x, self.y+y)

    # NOTE: Direct access to console.tiles, console.tiles_rgb fragments

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

    # NOTE: you can acces bg, fg, chr as tiles_rgb['bg'], tiles_rgb['fg'], tiles['ch']

    def __repr__(self):
        return f'<{self.__class__.__name__} x={self.x}, y={self.y}, width={self.width}, height={self.height}>'

    # NOTE: tcod.Console print/draw related methods:
    # NOTE: Only x,y coordinates are translated, it is NOT checked if prints are outside of Panel!

    # put_char(
    #   x: int, y: int, 
    #   ch: int, 
    #   bg_blend: int = 13)
    def put_char(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.put_char(parent_x, parent_y, *args, **kwargs)

    # print(
    #   x: int, y: int, 
    #   string: str, 
    #   fg: Optional[Tuple[int, int, int]] = None, 
    #   bg: Optional[Tuple[int, int, int]] = None, 
    #   bg_blend: int = 1, 
    #   alignment: int = 0)
    def print(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.print(parent_x, parent_y, *args, **kwargs)

    # print_box(
    #   x: int, y: int, 
    #   width: int, height: int, 
    #   string: str, 
    #   fg: Optional[Tuple[int, int, int]] = None, 
    #   bg: Optional[Tuple[int, int, int]] = None, 
    #   bg_blend: int = 1, 
    #   alignment: int = 0) 
    #   -> int
    def print_box(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.print_box(parent_x, parent_y, *args, **kwargs)

    # get_height_rect(
    #   x: int, y: int, 
    #   width: int, height: int, 
    #   string: str) 
    #   -> int
    def get_height_rect(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.get_height_rect(parent_x, parent_y, *args, **kwargs)

    # draw_rect(
    #   x: int, y: int, 
    #   width: int, height: int, 
    #   ch: int, 
    #   fg: Optional[Tuple[int, int, int]] = None, 
    #   bg: Optional[Tuple[int, int, int]] = None, 
    #   bg_blend: int = 1)
    def draw_rect(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.draw_rect(parent_x, parent_y, *args, **kwargs)

    # draw_frame(
    #   x: int, y: int, 
    #   width: int, height: int, 
    #   title: str = '', 
    #   clear: bool = True, 
    #   fg: Optional[Tuple[int, int, int]] = None, 
    #   bg: Optional[Tuple[int, int, int]] = None, 
    #   bg_blend: int = 1)
    def draw_frame(self, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.draw_frame(parent_x, parent_y, *args, **kwargs)

    # draw_semigraphics(
    #   pixels: Any, 
    #   x: int = 0, 
    #   y: int = 0)
    def draw_semigraphics(self, pixels, x, y, *args, **kwargs):
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.get_height_rect(pixels, parent_x, parent_y, *args, **kwargs)

    # blit(
    #   dest: tcod.console.Console, 
    #   dest_x: int = 0, dest_y: int = 0, 
    #   src_x: int = 0, src_y: int = 0, 
    #   width: int = 0, height: int = 0, 
    #   fg_alpha: float = 1.0, 
    #   bg_alpha: float = 1.0, 
    #   key_color: Optional[Tuple[int, int, int]] = None)
    def blit_from(self, x, y, src, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: src MUST be tcod.Console!
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.blit_from(parent_x, parent_y, src, *args, **kwargs)

    def blit_to(self, x, y, dest, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: dest MUST be tcod.Console!
        parent_x, parent_y = self._translate_parent(x, y)
        return self.parent.blit_to(parent_x, parent_y, dest, *args, **kwargs)

    # Other methods

    def fill(self, char, *args, **kwargs):
        return self.draw_rect(0, 0, ch=ord(char), width=self.width, height=self.height, *args, **kwargs)


class Container(TilesGrid):

    def __init__(self, parent, position, size):
        super().__init__(parent, position, size)
        self.panels = []


class HorizontalContainer(Container):

    def split(self, top=None, bottom=None):
        height = top or bottom
        if height and height < 1:
            height = int(self.height * height)
        if top:
            top = Panel(
                self, 
                Position(0, 0), 
                Size(self.width, self.height-height),
            )
            bottom = Panel(
                self, 
                Position(0, self.height-height), 
                Size(self.width, height),
            )
            self.panels = [top, bottom]
            return top, bottom
        elif bottom:
            top = Panel(
                self, 
                Position(0, 0),
                Size(self.width, height),
            )
            bottom = Panel(
                self, 
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
            left = Panel(
                self, 
                Position(0, 0),
                Size(self.width-width, self.height),
            )
            right = Panel(
                self, 
                Position(self.width-width, 0), 
                Size(width, self.height),
            )
            self.panels = [left, right]
            return left, right
        elif right:
            left = Panel(
                self, 
                Position(0, 0), 
                Size(width, self.height),
            )
            right = Panel(
                self, 
                Position(width, 0), 
                Size(self.width-width, self.height),
            )
            self.panels = [left, right]
            return left, right


class Panel(TilesGrid):

    def split_vertical(self, left=None, right=None):
        width = left or right
        container = VerticalContainer(
            isinstance(self, RootPanel) and self or self.parent,
            self.position,
            self.size,
        )
        return container.split(left=right and width, right=left and width)

    def split_horizontal(self, top=None, bottom=None):
        height = top or bottom
        container = HorizontalContainer(
            isinstance(self, RootPanel) and self or self.parent,
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


class Window:
    # TODO: For now it's just proof of concept
    # NOTE: splitting window.panel leaves original panel reference!

    def __init__(self, parent, x, y, width, height, decorations):
        self.frame = Frame(parent, Position(x, y), Size(width, height))
        self.frame.draw_decorations(decorations)
        self.panel = Panel(self.frame, Position(1, 1), Size(width-2, height-2))
        self.frame.panels.append(self.panel)


class RootPanel(Panel):

    def __init__(self, console):
        super().__init__(console, Position(0, 0), Size(console.width, console.height))

    def __str__(self):
        return str(self.parent)

    def _translate_root(self, x, y):
        return x, y

    def blit_from(self, x, y, src, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: src MUST be tcod.Console!
        src.blit(dest=self.parent, dest_x=x, dest_y=y, *args, **kwargs)

    def blit_to(self, x, y, dest, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: dest MUST be tcod.Console!
        self.parent.blit(dest=dest, src_x=x, src_y=y, *args, **kwargs)

    def create_window(self, x, y, width, height, decorations=None):
        return Window(self, x, y, width, height, decorations)

    # clear(
    #   ch: int = 32, 
    #   fg: Tuple[int, int, int] = Ellipsis, 
    #   bg: Tuple[int, int, int] = Ellipsis)
    def clear(self, *args, **kwargs):
        return self.parent.clear(*args, **kwargs)


# TODO: Instead of x,y, width,height use geometry.Position, Size, Geometry(?) in print/draw methods???

# TODO: Rework Window class - now it's a mess

# TODO: frame() should produce FramedPanel with Frame and Panel inside
# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations

# TODO: Keep track of Z-order of Windows?

# TODO: Scrollable Panels?
# TODO: Window/Dialog?
# TODO: event handlers?
