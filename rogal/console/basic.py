from ..geometry import Position, Size

from .core import Align, Padding

from . import toolkit
from . import renderers


"""Most basic widgets - building blocks for more complicated ones."""


class Cursor(toolkit.Renderer, toolkit.UIElement):

    def __init__(self, *, glyph=None, colors=None, position=None, blinking=None):
        super().__init__()
        self.glyph = glyph # NOTE: if glyph is set it will OVERWRITE character under cursor!
        self.colors = colors
        self.position = position or Position.ZERO
        if blinking:
            self.renderer = renderers.Blinking(self, rate=blinking)

    def move(self, vector):
        self.position = self.position.move(vector)

    def render(self, panel):
        if self.glyph:
            panel.print(self.glyph.char, self.position, colors=self.colors)
        elif self.colors:
            panel.paint(self.colors, self.position)
        else:
            panel.invert(self.position)


class Text(toolkit.Renderer, toolkit.Widget):

    """Text widget and renderer."""

    def __init__(self, txt, width=None, colors=None, *, align=Align.TOP_LEFT, padding=Padding.ZERO):
        super().__init__(align=align, padding=padding)
        self.txt = txt
        self.colors = colors

        lines = self.txt.splitlines() or ['', ]
        self.txt_size = Size(
            max(len(line) for line in lines),
            len(lines)
        )
        self.size = Size(
            max(width or 0, self.txt_size.width),
            len(lines)
        )

    def get_layout_panel(self, panel):
        panel = panel.create_panel(Position.ZERO, Size(panel.width, self.padded_height))
        # position = panel.get_position(self.size, self.align)
        # panel = panel.create_panel(position, self.size)
        return panel

    def render(self, panel):
        if self.colors:
            panel.clear(self.colors)
        position = panel.get_align_position(self.txt_size, self.align, self.padding)
        panel.print(self.txt, position, colors=self.colors, align=self.align)

