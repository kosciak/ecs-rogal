from .core import Position
from .toolkit import Renderer


class ClearPanel(Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel, timestamp):
        panel.clear(self.colors)


class PaintPanel(Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel, timestamp):
        panel.paint(self.colors, Position.ZERO, panel.size)


# TODO: FillPanel(Renderer):


class InvertColors(Renderer):

    def render(self, panel, timestamp):
        panel.invert(Position.ZERO, panel.size)


class MultiFrameRenderer(Renderer):

    def __init__(self, rate):
        super().__init__()
        self._frames_num = None
        self.rate = int(rate) # How long whole animations take in miliseconds

    def get_frames_num(self):
        return 1

    @property
    def frames_num(self):
        if self._frames_num is None:
            self._frames_num = self.get_frames_num()
        return self._frames_num

    def get_frame(self, timestamp):
        return timestamp // (self.rate // self.frames_num) % self.frames_num


# TODO: RenderEffect?
class Blinking(MultiFrameRenderer):

    BLINK_RATE = 1200

    def __init__(self, renderer, rate=BLINK_RATE):
        super().__init__(rate)
        self._renderer = renderer

    def get_frames_num(self):
        return 2

    def render(self, panel, timestamp):
        frame = self.get_frame(timestamp)
        if frame:
            self._renderer.render(panel, timestamp)

