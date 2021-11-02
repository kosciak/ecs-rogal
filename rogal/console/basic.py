from ..geometry import Position, Size

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


class Cursor(toolkit.Renderer, toolkit.UIElement):

    def __init__(self, *, glyph=None, colors=None, position=None, blinking=None):
        super().__init__()
        self.glyph = glyph # NOTE: if glyph is set it will OVERWRITE character under cursor!
        self.colors = colors
        self.position = position or Position.ZERO
        if blinking:
            self.renderer = renderers.Blinking(self, duration=blinking)

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

