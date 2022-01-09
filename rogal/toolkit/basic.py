import collections

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
        self._txt = txt
        self.txt_size = self.get_txt_size(self._txt)
        super().__init__(
            align=align,
            width=width,
        )
        self.style.update(
            colors=colors,
        )

    @property
    def txt(self):
        return self._txt

    @txt.setter
    def txt(self, txt):
        self._txt = txt
        self.txt_size = self.get_txt_size(self._txt)

    @property
    def colors(self):
        return self.style.colors

    @colors.setter
    def colors(self, colors):
        self.style.colors = colors

    @core.UIElement.width.getter
    def width(self):
        if self.style.width is not None:
            return self.style.width
        return self.txt_size.width

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
        # TODO: Don't like setting text.<property> here...
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


class Decorations(collections.namedtuple(
    'Decorations', [
        'left', 'right',
        'top', 'bottom',
        'tl', 'tr',
        'bl', 'br',
    ])):

    __slots__ = ()

    def __new__(cls,
        left=None, right=None,
        top=None, bottom=None,
        top_left=None, top_right=None,
        bottom_left=None, bottom_right=None
    ):
        return super().__new__(
            cls,
            Glyph(left), Glyph(right),
            Glyph(top), Glyph(bottom),
            Glyph(top_left), Glyph(top_right),
            Glyph(bottom_left), Glyph(bottom_right),
        )

    @property
    def top_left(self):
        return self.tl or self.top or self.left

    @property
    def top_right(self):
        return self.tr or self.top or self.right

    @property
    def bottom_left(self):
        return self.bl or self.bottom or self.left

    @property
    def bottom_right(self):
        return self.br or self.bottom or self.right

Decorations.NONE = Decorations()


class Frame(core.Renderer, core.UIElement):

    """Frame decorations."""

    def __init__(self, decorations, *, colors=None):
        super().__init__()
        self.style.update(
            decorations=decorations or Decorations.NONE,
            colors=colors,
        )

    @property
    def decorations(self):
        return self.style.decorations

    @decorations.setter
    def decorations(self, decorations):
        self.style.decorations = decorations

    @property
    def colors(self):
        return self.style.colors

    @colors.setter
    def colors(self, colors):
        self.style.colors = colors

    @property
    def inner_offset(self):
        inner_offset = Position(
            self.decorations.left and 1 or 0,
            self.decorations.top and 1 or 0,
        )
        return inner_offset

    @property
    def extents(self):
        offset = self.inner_offset
        extents = Size(
            offset.x + (self.decorations.right and 1 or 0),
            offset.y + (self.decorations.bottom and 1 or 0)
        )
        return extents

    def get_inner_panel(self, panel):
        offset = self.inner_offset
        extents = self.extents
        return panel.create_panel(
            offset,
            Size(panel.width-extents.width, panel.height-extents.height)
        )

    def render(self, panel, timestamp):
        if self.decorations.top is not None:
            panel.draw(
                self.decorations.top, self.colors,
                Position(1, 0), Size(panel.width-2, 1),
            )
        if self.decorations.bottom is not None:
            panel.draw(
                self.decorations.bottom, self.colors,
                Position(1, panel.height-1), Size(panel.width-2, 1),
            )
        if self.decorations.left is not None:
            panel.draw(
                self.decorations.left, self.colors,
                Position(0, 1), Size(1, panel.height-2),
            )
        if self.decorations.right is not None:
            panel.draw(
                self.decorations.right, self.colors,
                Position(panel.width-1, 1), Size(1, panel.height-2),
            )

        panel.draw(
            self.decorations.top_left, self.colors,
            Position(0, 0),
        )
        panel.draw(
            self.decorations.top_right, self.colors,
            Position(panel.width-1, 0),
        )
        panel.draw(
            self.decorations.bottom_left, self.colors,
            Position(0, panel.height-1),
        )
        panel.draw(
            self.decorations.bottom_right, self.colors,
            Position(panel.width-1, panel.height-1),
        )

    def __nonzero__(self):
        return any(
            self.decorations.top, self.decorations.bottom,
            self.decorations.left, self.decorations.right,
        )


# TODO: Needs rewrite!
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
        super().__init__(
            duration=duration, frame_duration=frame_duration,
            # width=self.txt_size.width,
            # height=self.txt_size.height,
            align=align,
        )
        self.style.update(
            frames = frames,
            colors = colors,
        )
        self.txt_size = self.get_frames_txt_size(self.style.frames)

    @property
    def frames(self):
        return self.style.frames

    @frames.setter
    def frames(self, frames):
        self.style.frames = frames
        self.txt_size = self.get_frames_txt_size(self.style.frames)

    @core.UIElement.width.getter
    def width(self):
        if self.style.width is not None:
            return self.style.width
        return self.txt_size.width

    @core.UIElement.width.getter
    def height(self):
        if self.style.height is not None:
            return self.style.height
        return self.txt_size.height

    @property
    def colors(self):
        return self.style.colors

    @colors.setter
    def colors(self, colors):
        self.style.colors = colors

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


class ProgressBarSegments(collections.namedtuple(
    'ProgressBarSegments', [
        'empty',
        'full',
        'fractions',
    ])):

    def __new__(cls, segments):
        empty = str(segments[0])
        fractions = cls.get_fractions(segments[1:-1])
        full = str(segments[-1])
        return super().__new__(cls, empty, full, fractions)

    @staticmethod
    def get_fractions(segments):
        segments = segments or []
        fraction_value = 1. / (len(segments)+1)
        fractions = [
            (i*fraction_value, str(segment))
            for i, segment in enumerate(segments, start=1)
        ]
        fractions.reverse()
        return fractions


class ProgressBar(core.Renderer, core.UIElement):

    def __init__(self, value, segments, colors, *, reverse=False, align=None, width=None, height=1):
        super().__init__(
            align=align,
            width=width,
            height=height,
        )
        self.value = value # float value from 0.0 to 1.0
        self.style.update(
            segments=segments,
            colors=colors,
            reverse=reverse,
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
        width = panel.width * self.value

        fulls_num = int(width)
        rest = width - fulls_num
        if not self.segments.fractions:
            fulls_num += round(rest)
        txt = self.segments.full*fulls_num

        for value, segment in self.segments.fractions:
            if rest >= value:
                txt += segment
                break

        empty_num = panel.width - len(txt)
        txt += self.segments.empty * empty_num

        if self.style.reverse:
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

