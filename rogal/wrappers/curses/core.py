import curses
import logging
import os
import sys

from ...term import term_seq

from ..core import IOWrapper

from .input import CursesInputWrapper
from .output import CursesOutputWrapper


log = logging.getLogger(__name__)


def dump_capabilities(window):
    capabilities = dict(
        termname=curses.termname().decode('utf-8'),
        longname=curses.longname().decode('utf-8'),
        has_colors=curses.has_colors(),
        can_change_color=curses.can_change_color(),
        COLORS=curses.COLORS,
        COLOR_PAIRS=curses.COLOR_PAIRS,
    )
    for color in range(capabilities['COLORS']):
        capabilities[f'color_{color}'] = curses.color_content(color)

    fn = f'capabilities-{capabilities["termname"]}.txt'
    f = open(fn, 'w')
    for key, value in capabilities.items():
        f.write(f'{key} = {value}\n')
    f.close()


class CursesWrapper(IOWrapper):

    def __init__(self,
        console_size,
        palette,
        *args, **kwargs,
    ):
        super().__init__(console_size=console_size, palette=palette, *args, **kwargs)
        self._indexed_palette = None
        self._screen = None
        self.__prev_escdelay = None

    def initialize_palette(self):
        self.initialize()
        max_colors = curses.COLORS
        can_change_color = curses.can_change_color()
        rgb_factor = 1000 / 255
        palette = self._palette.invert()
        if self._palette.fg in self._palette.colors:
            palette.fg = self._palette.colors.index(self._palette.fg)
        else:
            palette.fg = -1
        if self._palette.bg in self._palette.colors:
            palette.bg = self._palette.colors.index(self._palette.bg)
        else:
            palette.bg = -1
        for i, color in enumerate(palette.colors):
            if can_change_color and i < max_colors:
                rgb = color.to_rgb()
                curses.init_color(i, round(rgb.r*rgb_factor), round(rgb.g*rgb_factor), round(rgb.b*rgb_factor))
            palette.colors[i] = i
        return palette

    @property
    def palette(self):
        if self._indexed_palette is None:
            self._indexed_palette = self.initialize_palette()
        return self._indexed_palette

    @palette.setter
    def palette(self, palette):
        # TODO: Some event on palette change forcing everything to redraw?
        self._palette = palette
        self._indexed_palette = None

    @property
    def is_initialized(self):
        return self._screen is not None

    def initialize_window(self, window):
        # Enter keypad mode - escape sequences for special keys will be interpreted
        window.keypad(True)

        # Don't refresh automatically on window change
        window.immedok(False)
        # Don't scroll on bottom line
        window.scrollok(False)
        # Make getch() non blocking; consider curses.halfdelay()
        window.nodelay(True)
        # Reduce cursor movement
        window.leaveok(True)
        return window

    def set_escdelay(self, delay):
        self.__prev_escdelay = os.environ.get('ESCDELAY')
        os.environ['ESCDELAY'] = str(delay)

    def restore_escdelay(self):
        if 'ESCDELAY' in os.environ:
            del os.environ['ESCDELAY']
            if self.__prev_escdelay:
                os.environ['ESCDELAY'] = self.__prev_escdelay

    def initialize_colors(self):
        # Initialize colors and set default console colors as color_pair(0)
        try:
            curses.start_color()
            curses.use_default_colors()
        except:
            pass

    def initialize_screen(self):
        self.set_escdelay(25) # NOTE: Must be called before initscr()!

        screen = curses.initscr()

        # Turn off echoing of keys
        curses.noecho()

        # Raw mode - this will catch ^q and ^s (but still not ^z and ^c)
        curses.raw()
        # No buffering on keyboard input
        # curses.cbreak()

        self.initialize_colors()

        return self.initialize_window(screen)

    def restore_screen(self):
        self._screen.keypad(False)
        curses.echo()
        curses.noraw()
        curses.nocbreak()
        curses.endwin()

        self.restore_escdelay()

    def set_title(self, title):
        sys.stdout.write(term_seq.save_title())
        if title:
            sys.stdout.write(term_seq.set_title(title))
        sys.stdout.flush()

    def restore_title(self):
        sys.stdout.write(term_seq.restore_title())
        sys.stdout.flush()

    def hide_cursor(self):
        curses.curs_set(0)

    def show_cursor(self):
        curses.curs_set(2)

    def initialize(self):
        if self.is_initialized:
            return

        if self.title:
            self.set_title(self.title)

        self._screen = self.initialize_screen()

        self._input = CursesInputWrapper(self.screen)
        self._output = CursesOutputWrapper()

        self.hide_cursor()
        # dump_capabilities(self._screen)

    def terminate(self):
        # Cleanup all settings back to defaults
        self.restore_screen()
        self.restore_title()
        self._screen = None

    @property
    def screen(self):
        return self._screen

    def create_panel(self, size=None):
        size = size or self.console_size
        window = self.initialize_window(
            curses.newwin(size.height, size.width)
        )
        return self._output.create_panel(window, size, self.palette)

    def get_size(self):
        return self.screen.getmaxyx()

