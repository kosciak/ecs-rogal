from enum import Enum
import collections

from ..geometry import Position, Size
from ..tiles import Symbol, Tile

from .core import Alignment, Panel


# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations

# TODO: Keep track of Z-order of Windows?

# TODO: Scrollable Panels?
# TODO: Window/Dialog?

# TODO: frame() should produce FramedPanel with Frame and Panel inside
# TODO: Rework FramedWindow class - now it's a mess


class Decorations:

    __slots__ = (
        'top', 'bottom', 'left', 'right',
        '_top_left', '_top_right', '_bottom_left', '_bottom_right',
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
        x = 0
        y = 0
        width = 0
        height = 0
        if self.decorations.top:
            y = 1
            height += 1
        if self.decorations.left:
            x = 1
            width += 1
        if self.decorations.bottom:
            height += 1
        if self.decorations.right:
            width += 1
        return self.create_panel(Position(x, y), Size(self.width-width, self.height-height))

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

    def __init__(self, panel, title, decorations=None, alignment=Alignment.LEFT, colors=None):
        self.panel = panel
        self.title = title
        self.decorations = decorations
        self.alignment = alignment
        self.colors = colors

    def render(self):
        if self.alignment == Alignment.LEFT:
            position = Position(1, 0)
        elif self.alignment == Alignment.RIGHT:
            position = Position(self.panel.width-2, 0)
        elif self.alignment == Alignment.CENTER:
            position = Position(self.panel.width//2, 0)
        prefix = self.decorations and self.decorations.left and self.decorations.left.char or ''
        postfix = self.decorations and self.decorations.right and self.decorations.right.char or ''
        title = f'{prefix}{self.title}{postfix}'
        self.panel.print(title, position, alignment=self.alignment, colors=self.colors)


class Window(Panel):

    # TODO: !!!

    def __init__(self, panel, decorations):
        super().__init__(panel.root, panel.position, panel.size)
        self.frame = Frame(panel, decorations)
        self.frame.render()
        self.panels = [
            self.frame.create_panel(Position(1, 1), Size(self.frame.width-2, self.frame.height-2)),
        ]

