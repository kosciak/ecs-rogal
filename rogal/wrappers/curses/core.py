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
        colors_manager,
        *args, **kwargs,
    ):
        super().__init__(console_size=console_size, colors_manager=colors_manager, *args, **kwargs)
        self._screen = None
        self.__prev_escdelay = None

    def get_index_palette(self, palette):
        self.initialize()
        max_colors = curses.COLORS
        can_change_color = curses.can_change_color()
        rgb_factor = 1000 / 255
        indexed_palette = palette.invert() # TODO: Why? Just to copy?
        if palette.fg in palette.colors:
            indexed_palette.fg = palette.colors.index(palette.fg)
        else:
            indexed_palette.fg = -1
        if palette.bg in palette.colors:
            indexed_palette.bg = palette.colors.index(palette.bg)
        else:
            indexed_palette.bg = -1
        for i, color in enumerate(indexed_palette.colors):
            if can_change_color and i < max_colors:
                rgb = color.to_rgb()
                curses.init_color(i, round(rgb.r*rgb_factor), round(rgb.g*rgb_factor), round(rgb.b*rgb_factor))
            indexed_palette.colors[i] = i
        return indexed_palette

    def set_palette(self, palette):
        self.colors_manager.palette = self.get_index_palette(palette)

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

        self.set_palette(self.colors_manager.palette)
        self._input = CursesInputWrapper(self.screen)
        self._output = CursesOutputWrapper(self.colors_manager)

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
        return self._output.create_panel(window, size)

    def get_size(self):
        return self.screen.getmaxyx()

