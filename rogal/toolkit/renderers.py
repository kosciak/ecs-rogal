from ..geometry import Position

from . import core


class Chain(core.Renderer):

    def __init__(self, renderers=None):
        super().__init__()
        self.renderers = renderers or []

    def render(self, panel, timestamp):
        for renderer in self.renderers:
            renderer.render(panel, timestamp)


class ClearPanel(core.WithColors, core.Renderer):

    def render(self, panel, timestamp):
        panel.clear(self.colors)


class PaintPanel(core.WithColors, core.Renderer):

    def render(self, panel, timestamp):
        if self.colors:
            panel.paint(self.colors, Position.ZERO, panel.size)


# TODO: FillPanel(core.Renderer):


class InvertColors(core.Renderer):

    def render(self, panel, timestamp):
        panel.invert(Position.ZERO, panel.size)


# TODO: RenderEffect?
class Blinking(core.Animated, core.Renderer):

    BLINK_RATE = 1200

    def __init__(self, renderer, rate=BLINK_RATE):
        super().__init__(duration=rate)
        self._renderer = renderer

    def get_frames_num(self):
        return 2

    def render(self, panel, timestamp):
        frame_num = self.get_frame_num(timestamp)
        if frame_num:
            self._renderer.render(panel, timestamp)

