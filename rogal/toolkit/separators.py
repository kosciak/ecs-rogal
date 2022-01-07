from ..geometry import Position, Size

from ..console.core import Glyph

from . import core


class Separator(core.Renderer, core.UIElement):

    def __init__(self, separator, *, colors=None, align=None, width=None, height=None):
        super().__init__(
            align=align,
            width=width,
            height=height,
        )
        self.separator = Glyph(separator[0])
        if len(separator) > 1:
            self.start = Glyph(separator[1])
            self.end = Glyph(separator[-1])
        else:
            self.start = None
            self.end = None
        self.colors = colors

    def render(self, panel, timestamp):
        panel.fill(self.separator, self.colors)
        if self.start is not None:
            panel.draw(self.start, self.colors, Position.ZERO)


class HorizontalSeparator(Separator):

    def __init__(self, separator, *, colors=None, align=None, width=None):
        super().__init__(
            separator,
            colors=colors,
            align=align,
            width=width or 0,
            height=1,
        )

    @Separator.width.getter
    def width(self):
        return 0

    def get_size(self, available):
        return Size(
            self._width or available.width,
            1,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.end is not None:
            panel.draw(self.end, self.colors, Position(panel.width-1, 0))


class VerticalSeparator(Separator):

    def __init__(self, separator, *, colors=None, align=None, height=None):
        super().__init__(
            separator,
            colors=colors,
            align=align,
            width=1,
            height=height or 0,
        )

    @Separator.width.getter
    def height(self):
        return 0

    def get_size(self, available):
        return Size(
            1,
            self._height or available.height,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.end is not None:
            panel.draw(self.end, self.colors, Position(0, panel.height-1))

