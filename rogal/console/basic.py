from ..geometry import Position, Size
from ..tiles import Tile

from .core import Align

from . import toolkit
from . import renderers


"""Most basic UI elements - building blocks for more complicated ones."""


class Text(toolkit.Renderer, toolkit.UIElement):

    """Text widget and renderer."""

    def __init__(self, txt, width=None, colors=None, *, align=None):
        self.txt = txt
        self.colors = colors
        self.txt_size = self.get_txt_size(self.txt)
        if width is None:
            width = self.txt_size.width
        super().__init__(width=width, align=align)

    def get_txt_size(self, txt):
        lines = txt.splitlines() or ['', ]
        # TODO: Use: textwrap.wrap(line, width)
        txt_size = Size(
            max(len(line) for line in lines),
            len(lines)
        )
        return txt_size

    @property
    def height(self):
        return self.txt_size.height

    def render(self, panel, timestamp):
        # TODO: panel.clear() should be done higher, on parent widget level, not here!
        # if self.colors:
        #     panel.clear(self.colors)
        position = panel.get_align_position(self.txt_size, self.align)
        panel.print(self.txt, position, colors=self.colors, align=self.align)


class Frame(toolkit.Renderer, toolkit.UIElement):

    """Frame decorations."""

    __slots__ = (
        'top', 'bottom', 'left', 'right',
        '_top_left', '_top_right', '_bottom_left', '_bottom_right',
        'inner_offset', 'size',
    )

    def __init__(self,
        left=None, right=None,
        top=None, bottom=None,
        top_left=None, top_right=None,
        bottom_left=None, bottom_right=None,
        *, colors=None,
    ):
        super().__init__()
        self.top = Tile.create(top, fg=colors and colors.fg, bg=colors and colors.bg)
        self.bottom = Tile.create(bottom, fg=colors and colors.fg, bg=colors and colors.bg)
        self.left = Tile.create(left, fg=colors and colors.fg, bg=colors and colors.bg)
        self.right = Tile.create(right, fg=colors and colors.fg, bg=colors and colors.bg)
        self._top_left = Tile.create(top_left, fg=colors and colors.fg, bg=colors and colors.bg)
        self._top_right = Tile.create(top_right, fg=colors and colors.fg, bg=colors and colors.bg)
        self._bottom_left = Tile.create(bottom_left, fg=colors and colors.fg, bg=colors and colors.bg)
        self._bottom_right = Tile.create(bottom_right, fg=colors and colors.fg, bg=colors and colors.bg)

        self.inner_offset = Position(
            self.left and 1 or 0,
            self.top and 1 or 0,
        )
        self.extents = Size(
            self.inner_offset.x + (self.right and 1 or 0),
            self.inner_offset.y + (self.bottom and 1 or 0)
        )

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
        return Frame(
            kwargs.get('top', self.top), kwargs.get('bottom', self.bottom),
            kwargs.get('left', self.left), kwargs.get('right', self.right),
            kwargs.get('top_left', self._top_left), kwargs.get('top_right', self._top_right),
            kwargs.get('bottom_left', self._bottom_left), kwargs.get('bottom_right', self._bottom_right),
            colors=colors,
        )

    def inner_panel(self, panel):
        return panel.create_panel(
            self.inner_offset,
            Size(panel.width-self.extents.width, panel.height-self.extents.height)
        )

    def render(self, panel, timestamp):
        panel.draw(self.top, Position(1, 0), Size(panel.width-2, 1))
        panel.draw(self.bottom, Position(1, panel.height-1), Size(panel.width-2, 1))
        panel.draw(self.left, Position(0, 1), Size(1, panel.height-2))
        panel.draw(self.right, Position(panel.width-1, 1), Size(1, panel.height-2))

        panel.draw(self.top_left, Position(0, 0))
        panel.draw(self.top_right, Position(panel.width-1, 0))
        panel.draw(self.bottom_left, Position(0, panel.height-1))
        panel.draw(self.bottom_right, Position(panel.width-1, panel.height-1))

    def __nonzero__(self):
        return any(self.top, self.bottom, self.left, self.right)


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

    def render(self, panel, timestamp):
        if self.glyph:
            panel.print(self.glyph.char, self.position, colors=self.colors)
        elif self.colors:
            panel.paint(self.colors, self.position)
        else:
            panel.invert(self.position)


class Spinner(toolkit.Animated, toolkit.Renderer, toolkit.UIElement):

    DEFAULT_FRAME_DURATION = 100

    def __init__(self, colors, frames, duration=None, frame_duration=None, *, align=None):
        if duration is None and frame_duration is None:
            frame_duration = self.DEFAULT_FRAME_DURATION
        super().__init__(
            duration=duration, frame_duration=frame_duration,
            width=1, height=1, align=align,
        )
        self.colors = colors
        self.frames = frames

    def get_frames_num(self):
        return len(self.frames)

    def render(self, panel, timestamp):
        frame_num = self.get_frame_num(timestamp)
        frame = self.frames[frame_num]
        panel.print(frame, Position.ZERO, colors=self.colors)


class ProgressBar(toolkit.Renderer, toolkit.UIElement):

    EMPTY_CHAR = ' '

    def __init__(self, value, colors, full, parts=None, width=None, *, align=None):
        super().__init__(width=width, height=1, align=align)
        self.colors = colors
        self.value = value # float value from 0.0 to 1.0
        self.full = full
        self.parts_values = self.get_parts_values(parts)

    def get_parts_values(self, parts):
        parts = parts or []
        part_value = 1. / (len(parts)+1)
        parts_values = [(i*part_value, part) for i, part in enumerate(parts, start=1)]
        parts_values.reverse()
        return parts_values

    def render(self, panel, timestamp):
        width = panel.width * self.value

        fulls_num = int(width)
        if not self.parts_values:
            fulls_num += round(rest)
        txt = self.full*fulls_num

        rest = width - fulls_num
        for value, part in self.parts_values:
            if rest >= value:
                txt += part
                break

        empty_num = panel.width - len(txt)
        txt += self.EMPTY_CHAR * empty_num

        panel.print(txt, Position.ZERO, colors=self.colors)


class ProgressBarAnimatedDemo(toolkit.Animated, ProgressBar):

    def __init__(self, duration=None, frame_duration=None, *args, **kwargs):
        super().__init__(
            duration=duration, frame_duration=frame_duration,
            *args, **kwargs
        )

    def get_frames_num(self):
        return 100

    def render(self, panel, timestamp):
        frame_num = self.get_frame_num(timestamp)
        self.value = 1. - (frame_num+1)/self.frames_num
        # self.value = frame_num/100
        super().render(panel, timestamp)


class Separator(toolkit.Renderer, toolkit.UIElement):

    def __init__(self, separator, start=None, end=None, colors=None, width=None, height=None, align=None):
        super().__init__(width=width, height=height, align=align)
        self.separator = Tile.create(separator, fg=colors and colors.fg, bg=colors and colors.bg)
        self.start = Tile.create(start, fg=colors and colors.fg, bg=colors and colors.bg)
        self.end = Tile.create(end, fg=colors and colors.fg, bg=colors and colors.bg)

    def render(self, panel, timestamp):
        panel.fill(self.separator)
        if self.start:
            panel.draw(self.start, Position.ZERO)


class HorizontalSeparator(Separator):

    def __init__(self, separator, start=None, end=None, colors=None, width=None, align=None):
        super().__init__(separator, start, end, colors, width=width or 0, height=1, align=align)

    @property
    def width(self):
        return 0

    def get_size(self, panel):
        return Size(
            self._width or panel.width,
            1,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.end:
            panel.draw(self.end, Position(panel.width-1, 0))


class VerticalSeparator(Separator):

    def __init__(self, separator, start=None, end=None, colors=None, height=None, align=None):
        super().__init__(separator, start, end, colors, width=1, height=height or 0, align=align)

    @property
    def height(self):
        return 0

    def get_size(self, panel):
        return Size(
            1,
            self._height or panel.height,
        )

    def render(self, panel, timestamp):
        super().render(panel, timestamp)
        if self.end:
            panel.draw(self.end, Position(0, panel.height-1))

