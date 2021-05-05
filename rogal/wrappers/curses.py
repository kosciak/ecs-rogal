import curses
import logging
import os

from .core import IOWrapper
from .curses_input import CursesInputWrapper


log = logging.getLogger(__name__)


# NOTE: Just some biolerplate code for initialisation / closing curses screen
#       Main problem is explicit initialisation of all color pairs
#       Would need to reverse check index of color in pallette, and init_pair() for each combination

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


class ColorPairsManager:

    MAX_PAIR_NUMS = 256

    def __init__(self):
        self.color_pairs = {}

    def set_pair(self, color_pair):
        next_pair_num = len(self.color_pairs) + 1 # NOTE: pair 0 is (-1, -1)
        if next_pair_num > self.MAX_PAIR_NUMS:
            raise ValueError(f'Max color pairs number exceeded! {next_pair_num}')
        curses.init_pair(next_pair_num, color_pair[0], color_pair[1])
        self.color_pairs[color_pair] = next_pair_num

    def get_pair(self, fg, bg):
        color_pair = tuple(sorted([fg, bg]))
        pair_num = self.color_pairs.get(color_pair)
        if pair_num:
            if color_pair[0] == fg:
                return curses.color_pair(pair_num)
            else:
                return curses.color_pair(pair_num) | curses.A_REVERSE

        self.set_pair(color_pair)
        return self.get_pair(fg, bg)


class CursesWrapper(IOWrapper):

    def __init__(self,
        console_size,
        palette,
        *args, **kwargs,
    ):
        super().__init__(console_size=console_size, palette=palette)
        self._indexed_palette = None
        self.color_pairs = ColorPairsManager()
        self._screen = None
        self.__prev_esc_delay = None

    def initialize_palette(self):
        self.initialize()
        max_colors = curses.COLORS
        can_change_color = curses.can_change_color()
        rgb_factor = 1000 / 255
        palette = self._palette.invert()
        # palette.fg = -1
        # palette.bg = -1
        for i, color in enumerate(palette.colors):
            if can_change_color and i < max_colors:
                rgb = color.to_rgb()
                curses.init_color(i, round(rgb.r*rgb_factor), round(rgb.g*rgb_factor), round(rgb.b*rgb_factor))
            # palette.colors[i] = i
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
        return window

    def initialize(self):
        if self.is_initialized:
            return

        # Set ESC key delay
        self.__prev_escdelay = os.environ.get('ESCDELAY')
        os.environ['ESCDELAY'] = '25'

        screen = curses.initscr()

        # Turn off echoing of keys
        curses.noecho()
        # Raw mode - this will catch ^q and ^s (but still not ^z and ^c)
        curses.raw()
        # No buffering on keyboard input
        curses.cbreak()
        # Set the mouse events to be reported
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        # No interval for mouse clicks - separate BUTTONx_PRESSED / _RELEASED will be used!
        curses.mouseinterval(0)

        # Initialize colors and set default console colors as color_pair(0)
        try:
            curses.start_color()
            curses.use_default_colors()
        except:
            pass

        self._screen = self.initialize_window(screen)
        self._input = CursesInputWrapper(self._screen)
        dump_capabilities(self._screen)

    @property
    def screen(self):
        return self._screen

    def flush(self, console):
        curses.doupdate()

    def close(self):
        if self.is_initialized:
            # Cleanup all settings back to defaults
            self._screen.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            # Set ESCDELAY back if it was altered
            if 'ESCDELAY' in os.environ:
                del os.environ['ESCDELAY']
                if self.__prev_escdelay:
                    os.environ['ESCDELAY'] = self.__prev_escdelay
            self._screen = None

