import logging

from ...console import RGBConsole

from ..core import OutputWrapper


log = logging.getLogger(__name__)


class TermOutputWrapper(OutputWrapper):

    CONSOLE_CLS = RGBConsole

    def __init__(self, term, colors_manager):
        super().__init__(colors_manager)
        self.term = term
        self._prev_tiles = None

    def render_whole(self, panel):
        out = []
        out.append(self.term.clear())

        prev_fg = None
        prev_bg = None
        for x, y, ch, fg, bg in panel.console.tiles_gen(encode_ch=chr):
            if x == 0:
                out.append(self.term.cursor_move(x, y))
            if prev_fg is None or not (fg == prev_fg).all():
                out.append(self.term.fg_rgb(*fg))
                prev_fg = fg
            if prev_bg is None or not (bg == prev_bg).all():
                out.append(self.term.bg_rgb(*bg))
                prev_bg = bg
            out.append(ch)

        return out

    def render_diff(self, panel):
        out = []
        for x, y, ch, fg, bg in panel.console.tiles_diff_gen(self._prev_tiles, encode_ch=chr):
            out.append(self.term.cursor_move(x, y))
            out.append(self.term.fg_rgb(*fg))
            out.append(self.term.bg_rgb(*bg))
            out.append(ch)
        return out

    def render(self, panel):
        if self._prev_tiles is None or not self._prev_tiles.shape == panel.console.tiles.shape:
            out = self.render_whole(panel)
        else:
            out = self.render_diff(panel)

        self.term.write(''.join(out))
        self.term.write(self.term.normal())
        self.term.flush()

        self._prev_tiles = panel.console.tiles.copy()

