import collections

from ..geometry import Position, Size

from ..console.core import Glyph

from . import core


class SeparatorSegments(collections.namedtuple(
    'SeparatorSegments', [
        'middle',
        'start',
        'end',
    ])):

    __slots__ = ()

    def __new__(cls, segments):
        middle = Glyph(segments[0])
        if len(segments) > 1:
            start = Glyph(segments[1])
            end = Glyph(segments[-1])
        else:
            start = None
            end = None
        return super().__new__(cls, middle, start, end)


# TODO: add widgets.WithOverlay?
class Separator(core.Renderer, core.UIElement):

    def set_style(self, *, segments=None, colors=None, **style):
        self.style.update(
            segments=segments,
            colors=colors,
        )
        super().set_style(**style)

    @property
    def segments(self):
        return self.style.segments

    @property
    def colors(self):
        return self.style.colors

    def render(self, panel, timestamp):
        panel.fill(self.segments.middle, self.colors)
        if self.segments.start is not None:
            panel.draw(self.segments.start, self.colors, Position.ZERO)


class HorizontalSeparator(Separator):

    DEFAULT_HEIGHT = 1

    @property
    def width(self):
        return 0

    def get_size(self, available):
        return Size(
            self.style.width or available.width,
            self.height,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.segments.end is not None:
            panel.draw(self.segments.end, self.colors, Position(panel.width-1, 0))


class VerticalSeparator(Separator):

    DEFAULT_WIDTH = 1

    @property
    def height(self):
        return 0

    def get_size(self, available):
        return Size(
            self.width,
            self.style.height or available.height,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.segments.end is not None:
            panel.draw(self.segments.end, self.colors, Position(0, panel.height-1))

