from ..geometry import Position

from . import toolkit


class ClearPanel(toolkit.Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel, timestamp):
        panel.clear(self.colors)


class PaintPanel(toolkit.Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel, timestamp):
        panel.paint(self.colors, Position.ZERO, panel.size)


# TODO: FillPanel(toolkit.Renderer):


class InvertColors(toolkit.Renderer):

    def render(self, panel, timestamp):
        panel.invert(Position.ZERO, panel.size)


# TODO: RenderEffect?
class Blinking(toolkit.Animated, toolkit.Renderer):

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

