import time

from .core import Position
from .toolkit import Renderer


class ClearPanel(Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel):
        panel.clear(self.colors)


class PaintPanel(Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel):
        panel.paint(self.colors, Position.ZERO, panel.size)


# TODO: FillPanel(Renderer):


class InvertColors(Renderer):

    def render(self, panel):
        panel.invert(Position.ZERO, panel.size)


# TODO: RenderEffect?
class Blinking(Renderer):

    BLINK_RATE = 1200

    def __init__(self, renderer, rate=BLINK_RATE):
        super().__init__()
        self._renderer = renderer
        self.rate = rate // 2

    def render(self, panel):
        # TODO: blinking MUST be synchronized (during a frame) between ALL renderers!
        #       Maybe should be done on System level? NOT calling render if Blinking component present?
        # rate < 0 should mean inverted blinking
        if int((time.time()*1000) / self.rate) % 2 == 0:
            return
        return self._renderer.render(panel)

