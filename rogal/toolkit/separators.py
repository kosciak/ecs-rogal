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


class Separator(core.Renderer, core.UIElement):

    def __init__(self, segments, *, colors=None, align=None, width=None, height=None):
        super().__init__(
            align=align,
            width=width,
            height=height,
        )
        self.style.update(
            segments=segments,
            colors=colors,
        )

    @property
    def segments(self):
        return self.style.segments

    @segments.setter
    def segments(self, segments):
        self.style.segments = segments

    @property
    def colors(self):
        return self.style.colors

    @colors.setter
    def colors(self, colors):
        self.style.colors = colors

    def render(self, panel, timestamp):
        panel.fill(self.segments.middle, self.colors)
        if self.segments.start is not None:
            panel.draw(self.segments.start, self.colors, Position.ZERO)


class HorizontalSeparator(Separator):

    def __init__(self, segments, *, colors=None, align=None, width=None):
        super().__init__(
            segments,
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
            self.style.width or available.width,
            1,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.segments.end is not None:
            panel.draw(self.segments.end, self.colors, Position(panel.width-1, 0))


class VerticalSeparator(Separator):

    def __init__(self, segments, *, colors=None, align=None, height=None):
        super().__init__(
            segments,
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
            self.style.height or available.height,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.segments.end is not None:
            panel.draw(self.segments.end, self.colors, Position(0, panel.height-1))

