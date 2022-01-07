from ..geometry import Position, Size

from ..console.core import Align, Glyph

from . import core
from . import renderers


"""Most basic UI elements - building blocks for more complicated ones."""


class TextRenderer(core.Renderer):

    def get_txt_size(self, txt):
        lines = txt.splitlines() or ['', ]
        # TODO: Use: textwrap.wrap(line, width)
        txt_size = Size(
            max(len(line) for line in lines),
            len(lines)
        )
        return txt_size

    def render_txt(self, panel, txt, colors):
        position = panel.get_align_position(self.txt_size, self.align)
        panel.print(txt, position, colors=colors, align=self.align)

    def render(self, panel, timestamp):
        self.render_txt(panel, self.txt, self.colors)


class Text(TextRenderer, core.UIElement):

    """Text widget and renderer."""

    def __init__(self, txt, *, align=None, width=None, colors=None):
        self.txt = txt
        self.colors = colors
        self.txt_size = self.get_txt_size(self.txt)
        if width is None:
            width = self.txt_size.width
        super().__init__(
            align=align,
            width=width,
        )

    @core.UIElement.height.getter
    def height(self):
        return self.txt_size.height

    # TODO: Prevent from setting height? 


class WithTextContent:

    def __init__(self, content, *args, **kwargs):
        self.text = content
        super().__init__(
            content=self.text,
            *args, **kwargs,
        )

    def _text(self, text, *, align=None, width=None):
        if isinstance(text, str):
            text = Text(
                txt=text,
            )
        if align is not None:
            text.align = align
        if width is not None:
            text.width = width
        return text

    @property
    def txt(self):
        return self.text.txt

    @txt.setter
    def txt(self, txt):
        self.text.txt = txt
        self.redraw();


class Frame(core.Renderer, core.UIElement):

    """Frame decorations."""

    def __init__(self, decorations, *, colors=None):
        super().__init__()
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None
        self._top_left = None
        self._top_right = None
        self._bottom_left = None
        self._bottom_right = None
        self._parse_decorations(*decorations)
        self.colors = colors

        self.inner_offset = Position(
            self.left and 1 or 0,
            self.top and 1 or 0,
        )
        self.extents = Size(
            self.inner_offset.x + (self.right and 1 or 0),
            self.inner_offset.y + (self.bottom and 1 or 0)
        )

    def _parse_decorations(self,
        left=None, right=None,
        top=None, bottom=None,
        top_left=None, top_right=None,
        bottom_left=None, bottom_right=None
    ):
        self.left = Glyph(left)
        self.right = Glyph(right)
        self.top = Glyph(top)
        self.bottom = Glyph(bottom)
        self._top_left = Glyph(top_left)
        self._top_right = Glyph(top_right)
        self._bottom_left = Glyph(bottom_left)
        self._bottom_right = Glyph(bottom_right)

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

    def get_inner_panel(self, panel):
        return panel.create_panel(
            self.inner_offset,
            Size(panel.width-self.extents.width, panel.height-self.extents.height)
        )

    def render(self, panel, timestamp):
        if self.top is not None:
            panel.draw(self.top, self.colors, Position(1, 0), Size(panel.width-2, 1))
        if self.top is not None:
            panel.draw(self.bottom, self.colors, Position(1, panel.height-1), Size(panel.width-2, 1))
        if self.left is not None:
            panel.draw(self.left, self.colors, Position(0, 1), Size(1, panel.height-2))
        if self.right is not None:
            panel.draw(self.right, self.colors, Position(panel.width-1, 1), Size(1, panel.height-2))

        panel.draw(self.top_left, self.colors, Position(0, 0))
        panel.draw(self.top_right, self.colors, Position(panel.width-1, 0))
        panel.draw(self.bottom_left, self.colors, Position(0, panel.height-1))
        panel.draw(self.bottom_right, self.colors, Position(panel.width-1, panel.height-1))

    def __nonzero__(self):
        return any(self.top, self.bottom, self.left, self.right)


class Cursor(core.Renderer, core.UIElement):

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


class Spinner(core.Animated, TextRenderer, core.UIElement):

    DEFAULT_FRAME_DURATION = 100

    def __init__(self, colors, frames, *, duration=None, frame_duration=None, align=None):
        if duration is None and frame_duration is None:
            frame_duration = self.DEFAULT_FRAME_DURATION
        self.txt_size = self.get_frames_txt_size(frames)
        super().__init__(
            duration=duration, frame_duration=frame_duration,
            width=self.txt_size.width, height=self.txt_size.height, align=align,
        )
        self.colors = colors
        self.frames = frames

    def get_frames_txt_size(self, frames):
        frame_sizes = [self.get_txt_size(frame) for frame in frames]
        txt_size = Size(
            max(size.width for size in frame_sizes),
            max(size.height for size in frame_sizes),
        )
        return txt_size

    def get_frames_num(self):
        return len(self.frames)

    def render(self, panel, timestamp):
        frame_num = self.get_frame_num(timestamp)
        frame = self.frames[frame_num]
        self.render_txt(panel, frame, self.colors)


class ProgressBar(core.Renderer, core.UIElement):

    def __init__(self, value, segments, colors, *, reverse=False, align=None, width=None, height=1):
        super().__init__(
            align=align,
            width=width,
            height=height,
        )
        self.colors = colors
        self.value = value # float value from 0.0 to 1.0
        self.full = str(segments[-1])
        self.fractions = self.get_fractions(segments[1:-1])
        self.empty = str(segments[0])
        self.reverse = reverse

    def get_fractions(self, segments):
        segments = segments or []
        fraction_value = 1. / (len(segments)+1)
        fractions = [
            (i*fraction_value, str(segment))
            for i, segment in enumerate(segments, start=1)
        ]
        fractions.reverse()
        return fractions

    def render(self, panel, timestamp):
        width = panel.width * self.value

        fulls_num = int(width)
        rest = width - fulls_num
        if not self.fractions:
            fulls_num += round(rest)
        txt = self.full*fulls_num

        for value, segment in self.fractions:
            if rest >= value:
                txt += segment
                break

        empty_num = panel.width - len(txt)
        txt += self.empty * empty_num

        if self.reverse:
            txt = txt[::-1]

        if self.height > 1:
            txt = '\n'.join([txt, ]*self.height)

        panel.print(txt, Position.ZERO, colors=self.colors)


class ProgressBarAnimatedDemo(core.Animated, ProgressBar):

    def __init__(self, duration=None, frame_duration=None, *args, **kwargs):
        super().__init__(
            duration=duration, frame_duration=frame_duration,
            *args, **kwargs
        )

    def get_frames_num(self):
        return 100

    def render(self, panel, timestamp):
        frame_num = self.get_frame_num(timestamp)
        self.value = 1. - (frame_num)/self.frames_num
        super().render(panel, timestamp)

