from enum import Enum
import collections

from ..geometry import Position, Size
from ..tiles import Symbol, Tile

from .core import Align, Panel


# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations

# TODO: Keep track of Z-order of Windows?

# TODO: Scrollable Panels?
# TODO: Window/Dialog?

# TODO: frame() should produce FramedPanel with Frame and Panel inside
# TODO: Rework FramedWindow class - now it's a mess


def get_x(panel_width, width, align, padding=0):
    if align & Align.RIGHT:
        x = panel_width - width - padding
    if align & Align.CENTER:
        x = panel_width//2 - width//2
    else:
        x = padding
    return x


def get_y(panel_height, height, align, vert_padding=0):
    if align & Align.TOP:
        y = vert_padding
    elif align & Align.BOTTOM:
        y = panel_height - height - vert_padding
    elif align & Align.MIDDLE:
        y = panel_height//2 - height//2
    return y


def get_position(panel, size, align, padding=0, vert_padding=0):
    return Position(
        get_x(panel.width, size.width, align, padding),
        get_y(panel.height, size.height, align, vert_padding)
    )


class Decorations:

    __slots__ = (
        'top', 'bottom', 'left', 'right',
        '_top_left', '_top_right', '_bottom_left', '_bottom_right',
        'offset', 'width', 'height',
    )

    def __init__(self,
        top=None, bottom=None, left=None, right=None,
        top_left=None, top_right=None,
        bottom_left=None, bottom_right=None,
        colors=None,
    ):
        self.top = Tile.create(top, fg=colors and colors.fg, bg=colors and colors.bg)
        self.bottom = Tile.create(bottom, fg=colors and colors.fg, bg=colors and colors.bg)
        self.left = Tile.create(left, fg=colors and colors.fg, bg=colors and colors.bg)
        self.right = Tile.create(right, fg=colors and colors.fg, bg=colors and colors.bg)
        self._top_left = Tile.create(top_left, fg=colors and colors.fg, bg=colors and colors.bg)
        self._top_right = Tile.create(top_right, fg=colors and colors.fg, bg=colors and colors.bg)
        self._bottom_left = Tile.create(bottom_left, fg=colors and colors.fg, bg=colors and colors.bg)
        self._bottom_right = Tile.create(bottom_right, fg=colors and colors.fg, bg=colors and colors.bg)

        self.offset = Position(
            self.left and 1 or 0,
            self.top and 1 or 0,
        )
        self.width = self.offset.x + (self.right and 1 or 0)
        self.height = self.offset.y + (self.bottom and 1 or 0)

    @property
    def top_left(self):
        return self._top_left or self.top or self.left

    @property
    def top_right(self):
        return self._top_right or self.top or self.right

    @property
    def bottom_left(self):
        return self._bottom_left or self.bottom or self.left

    @property
    def bottom_right(self):
        return self._bottom_right or self.bottom or self.right

    def update(self, colors=None, **kwargs):
        return Decorations(
            kwargs.get('top', self.top), kwargs.get('bottom', self.bottom),
            kwargs.get('left', self.left), kwargs.get('right', self.right),
            kwargs.get('top_left', self._top_left), kwargs.get('top_right', self._top_right),
            kwargs.get('bottom_left', self._bottom_left), kwargs.get('bottom_right', self._bottom_right),
            colors,
        )

    def __nonzero__(self):
        return any(self.top, self.bottom, self.left, self.right)


class FrameDecorations(Decorations, Enum):
    NONE = ()

    BLOCK1 = (Symbol.BLOCK1, Symbol.BLOCK1, Symbol.BLOCK1, Symbol.BLOCK1)
    BLOCK2 = (Symbol.BLOCK2, Symbol.BLOCK2, Symbol.BLOCK2, Symbol.BLOCK2)
    BLOCK3 = (Symbol.BLOCK3, Symbol.BLOCK3, Symbol.BLOCK3, Symbol.BLOCK3)
    BLOCK4 = (Symbol.BLOCK4, Symbol.BLOCK4, Symbol.BLOCK4, Symbol.BLOCK4)

    HALFBLOCK = (
        Symbol.HALFBLOCK_S, Symbol.HALFBLOCK_N,
        Symbol.HALFBLOCK_W, Symbol.HALFBLOCK_E,
    )

    LINE = (
        Symbol.HLINE, Symbol.HLINE, Symbol.VLINE, Symbol.VLINE,
        Symbol.NW, Symbol.NE, Symbol.SW, Symbol.SE,
    )

    DLINE = (
        Symbol.DHLINE, Symbol.DHLINE, Symbol.DVLINE, Symbol.DVLINE,
        Symbol.DNW, Symbol.DNE, Symbol.DSW, Symbol.DSE,
    )

    DSLINE = (
        Symbol.DHLINE, Symbol.HLINE, Symbol.VLINE, Symbol.VLINE,
        Symbol.DSNW, Symbol.DSNE, Symbol.SW, Symbol.SE,
    )

    ASCII = tuple("=-||..`'")


class TitleDecorations(Decorations, Enum):
    NONE = ()

    SPACE = (None, None, ' ', ' ')

    PIPE = (None, None, '|', '|')
    SLASH = (None, None, '/', '/')
    BACKSLASH = (None, None, '\\', '\\')

    BRACKETS = (None, None, '(', ')')
    BRACKETS_ROUND = BRACKETS
    BRACKETS_SQUARE = (None, None, '[', ']')
    BRACKETS_ANGLE = (None, None, '<', '>')
    BRACKETS_CURLY = (None, None, '<', '>')

    BLOCK1 = (None, None, Symbol.BLOCK1, Symbol.BLOCK1)
    BLOCK2 = (None, None, Symbol.BLOCK2, Symbol.BLOCK2)
    BLOCK3 = (None, None, Symbol.BLOCK3, Symbol.BLOCK3)
    BLOCK4 = (None, None, Symbol.BLOCK4, Symbol.BLOCK4)

    LINE = (None, None, Symbol.TEEW, Symbol.TEEE)
    DLINE = (None, None, Symbol.DTEEW, Symbol.DTEEE)
    DSLINE = (None, None, Symbol.DSTEEW, Symbol.DSTEEE)


class Frame(Panel):
    # TODO: Setting title, adding buttons(?) on top/bottom border, scrollbars?
    #       For example setting things like: 
    #       .= Title ======[X]=.
    #       |                  |
    #       '-----------(more)-'

    def __init__(self, panel, decorations=None):
        super().__init__(panel.root, panel.position, panel.size)
        self.decorations = decorations

    @property
    def inner(self):
        return self.create_panel(
            self.decorations.offset,
            Size(self.width-self.decorations.width, self.height-self.decorations.height)
        )

    def render(self):
        if not self.decorations:
            return

        self.draw(self.decorations.top, Position(1, 0), Size(self.width-2, 1))
        self.draw(self.decorations.bottom, Position(1, self.height-1), Size(self.width-2, 1))
        self.draw(self.decorations.left, Position(0, 1), Size(1, self.height-2))
        self.draw(self.decorations.right, Position(self.width-1, 1), Size(1, self.height-2))

        self.draw(self.decorations.top_left, Position(0, 0))
        self.draw(self.decorations.top_right, Position(self.width-1, 0))
        self.draw(self.decorations.bottom_left, Position(0, self.height-1))
        self.draw(self.decorations.bottom_right, Position(self.width-1, self.height-1))


class Title:

    def __init__(self, panel, title, decorations=None, align=Align.LEFT, colors=None):
        size = Size(len(title) + (decorations and decorations.width or 0), 1)
        position = Position(get_x(panel.width, size.width, align, padding=1), 0)
        self.frame = Frame(panel.create_panel(position, size), decorations)
        self.panel = self.frame.inner
        self.title = title
        self.colors = colors

    def render(self):
        self.frame.render()
        self.panel.print(self.title, Position.ZERO, colors=self.colors)


class Window(Panel):

    def __init__(self, panel,
                 frame_decorations=FrameDecorations.DSLINE,
                 title=None, title_align=Align.TOP_CENTER,
                 title_decorations=TitleDecorations.DSLINE):
        self.frame = Frame(panel, frame_decorations)
        self.title = title and Title(self.frame, title, title_decorations, align=title_align)
        inner = self.frame.inner
        super().__init__(inner.root, inner.position, inner.size)

    def render(self):
        self.frame.render()
        if self.title:
            self.title.render()


class Button(Window):

    def __init__(self, panel,
                 msg,
                 frame_decorations=FrameDecorations.LINE):
        super().__init__(panel, frame_decorations=frame_decorations)
        self.msg = msg

    def render(self):
        super().render()
        self.print(self.msg, Position(self.width//2, 0), align=Align.CENTER)


class YesNoPrompt(Window):

    def __init__(self, panel, title, msg):
        size = Size(40, 8)
        position = get_position(panel.root, size, align=Align.TOP_CENTER, vert_padding=12)
        super().__init__(panel.root.create_panel(position, size), title=title)

        self.msg = msg

        button_size = Size(10, 3)
        position = get_position(self, Size(button_size.width*2, button_size.height), align=Align.BOTTOM_CENTER)
        self.buttons = []
        for msg in ['Yes', 'No']:
            if self.buttons:
                position += Position(button_size.width, 0)
            button = Button(self.create_panel(position, button_size), msg=msg)
            self.buttons.append(button)

    def render(self):
        super().render()

        position = get_position(self, Size(len(self.msg), 1), align=Align.TOP_CENTER, vert_padding=1)
        self.print(self.msg, position)

        for button in self.buttons:
            button.render()

