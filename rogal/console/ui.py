from enum import Enum

from ..geometry import Position, Size, WithSizeMixin
from ..tiles import Symbol, Tile

from .core import Align, Padding, Panel
from .toolkit import Decorations, Text, Decorated, Row, get_position


# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations

# TODO: Keep track of Z-order of Windows?

# TODO: Scrollable Panels?
# TODO: Window/Dialog?

# TODO: frame() should produce FramedPanel with Frame and Panel inside
# TODO: Rework FramedWindow class - now it's a mess


# TODO: Use ecs.resources...something...decorations.*
class FullDecorations(Decorations, Enum):
    NONE = ()

    BLOCK1 = (Symbol.BLOCK1, Symbol.BLOCK1, Symbol.BLOCK1, Symbol.BLOCK1)
    BLOCK2 = (Symbol.BLOCK2, Symbol.BLOCK2, Symbol.BLOCK2, Symbol.BLOCK2)
    BLOCK3 = (Symbol.BLOCK3, Symbol.BLOCK3, Symbol.BLOCK3, Symbol.BLOCK3)
    BLOCK4 = (Symbol.BLOCK4, Symbol.BLOCK4, Symbol.BLOCK4, Symbol.BLOCK4)

    HALFBLOCK = (
        Symbol.HALFBLOCK_W, Symbol.HALFBLOCK_E,
        Symbol.HALFBLOCK_S, Symbol.HALFBLOCK_N,
    )

    SUBP_INNER = (
        Symbol.HALFBLOCK_E, Symbol.HALFBLOCK_W,
        Symbol.HALFBLOCK_S, Symbol.HALFBLOCK_N,
        Symbol.SUBP_SE, Symbol.SUBP_SW, Symbol.SUBP_NE, Symbol.SUBP_NW,
    )

    SUBP_OUTER = (
        Symbol.HALFBLOCK_W, Symbol.HALFBLOCK_E,
        Symbol.HALFBLOCK_N, Symbol.HALFBLOCK_S,
        # NOTE: Corners would need inverted colors!
        Symbol.SUBP_SE, Symbol.SUBP_SW, Symbol.SUBP_NE, Symbol.SUBP_NW,
    )

    LINE = (
        Symbol.VLINE, Symbol.VLINE,
        Symbol.HLINE, Symbol.HLINE,
        Symbol.NW, Symbol.NE, Symbol.SW, Symbol.SE,
    )

    DLINE = (
        Symbol.DVLINE, Symbol.DVLINE,
        Symbol.DHLINE, Symbol.DHLINE,
        Symbol.DNW, Symbol.DNE, Symbol.DSW, Symbol.DSE,
    )

    DSLINE = (
        Symbol.VLINE, Symbol.VLINE,
        Symbol.DHLINE, Symbol.HLINE,
        Symbol.DSNW, Symbol.DSNE, Symbol.SW, Symbol.SE,
    )

    ASCII = tuple("||=-..`'")


class HorizontalDecorations(Decorations, Enum):
    NONE = ()

    SPACE = (' ', ' ')

    PIPE = ('|', '|')
    SLASH = ('/', '/')
    BACKSLASH = ('\\', '\\')

    BRACKETS = ('(', ')')
    BRACKETS_ROUND = BRACKETS
    BRACKETS_SQUARE = ('[', ']')
    BRACKETS_ANGLE = ('<', '>')
    BRACKETS_CURLY = ('<', '>')

    BLOCK1 = (Symbol.BLOCK1, Symbol.BLOCK1)
    BLOCK2 = (Symbol.BLOCK2, Symbol.BLOCK2)
    BLOCK3 = (Symbol.BLOCK3, Symbol.BLOCK3)
    BLOCK4 = (Symbol.BLOCK4, Symbol.BLOCK4)

    HALFBLOCK = (Symbol.HALFBLOCK_W, Symbol.HALFBLOCK_E)

    SUBP_OUTER = (Symbol.SUBP_NW, Symbol.SUBP_NE)
    SUBP_INNER = (Symbol.SUBP_SW, Symbol.SUBP_SE)

    LINE = (Symbol.TEEW, Symbol.TEEE)
    DLINE = (Symbol.DTEEW, Symbol.DTEEE)
    DSLINE = (Symbol.DSTEEW, Symbol.DSTEEE)


class Window:

    def __init__(self,
                 frame_decorations=FullDecorations.DSLINE,
                 title=None, title_align=Align.TOP_CENTER,
                 title_decorations=HorizontalDecorations.DSLINE):
        self.decorations = frame_decorations
        self.frame = []
        if title:
            self.frame.append(
                Decorated(
                    Text(title, align=title_align),
                    title_decorations,
                    align=title_align, padding=Padding(0, 1)
                )
            )
        self.content = []

    def layout(self, panel):
        yield from self.decorations.layout(panel)
        for widget in self.frame:
            yield from widget.layout(panel)
        panel = self.decorations.inner_panel(panel)
        for widget in self.content:
            yield from widget.layout(panel)


class YesNoPrompt(Window):

    def __init__(self, title, msg):
        super().__init__(title=title)

        msg = Text(f'\n{msg}', align=Align.TOP_CENTER)

        buttons = Row(align=Align.BOTTOM_CENTER)
        for button_msg in ['Yes', 'No']:
            buttons.append(
                Decorated(
                    Text(button_msg, align=Align.CENTER, width=8),
                    FullDecorations.LINE,
                    align=Align.TOP_LEFT,
                )
            )

        self.content = [msg, buttons, ]

    def layout(self, panel):
        size = Size(40, 8)
        position = get_position(panel.root, size, align=Align.TOP_CENTER, padding=Padding(12, 0))
        panel = panel.create_panel(position, size)
        yield from super().layout(panel)

