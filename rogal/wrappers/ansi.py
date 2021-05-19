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

    def flush(self, panel):
        self.term.write(self.term.clear())

        columns = panel.console.width
        prev_fg = None
        prev_bg = None
        lines = []
        line = []
        column = 0
        for ch, fg, bg in panel.console.tiles_gen(encode_ch=chr):
            column += 1
            if prev_fg is None or not (fg == prev_fg).all():
                line.append(self.term.fg_rgb(*fg))
                prev_fg = fg
            if prev_bg is None or not (bg == prev_bg).all():
                line.append(self.term.bg_rgb(*bg))
                prev_bg = bg
            line.append(ch)
            if column >= columns:
                lines.append(''.join(line))
                line = []
                column = 0

        # NOTE: in raw mode \r\n MUST be used, in cbreak mode \n is enough
        self.term.write('\r\n'.join(lines))
        self.term.write(self.term.normal())
        self.term.flush()

