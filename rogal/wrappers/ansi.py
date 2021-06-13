import logging
import time
import os
import sys

# NOTE: Only on *NIX!
import select
import termios
import tty

from ..console import ConsoleRGB
from ..term import ansi
from ..term.terminal import Terminal

from .core import IOWrapper
from .term_input import TermInputWrapper


log = logging.getLogger(__name__)


class ANSIWrapper(IOWrapper):

    # NOTE: Just proof-of-concept of ansi based Console rendering

    CONSOLE_CLS = ConsoleRGB

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_initialized = False
        self.term = Terminal()
        self._prev_tiles = None

    @property
    def is_initialized(self):
        return self._is_initialized

    def initialize(self):
        # self.term.cbreak()
        self.term.raw()
        self.term.fullscreen()
        self.term.keypad()
        self.term.hide_cursor()
        self.term.report_focus()
        self.term.mouse_tracking()
        self.term.bracketed_paste()
        if self.title:
            self.term.set_title(self.title)
        self._input = TermInputWrapper(self.term)
        self._is_initialized = True

    def terminate(self):
        self.term.close()
        self._is_initialized = False

    def create_console(self, size=None):
        return super().create_console(self.console_size)

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

    def flush(self, panel):
        if self._prev_tiles is None or not self._prev_tiles.shape == panel.console.tiles.shape:
            out = self.render_whole(panel)
        else:
            out = self.render_diff(panel)

        self.term.write(''.join(out))
        self.term.write(self.term.normal())
        self.term.flush()

        self._prev_tiles = panel.console.tiles.copy()

