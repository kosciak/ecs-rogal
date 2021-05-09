import curses
import functools
import logging
import os
import sys

from ..console import ConsoleIndexedColors, RootPanel
from ..escape_seq import term

from .core import IOWrapper
from .curses_input import CursesInputWrapper


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


class CursesRootPanel(RootPanel):

    def __init__(self, window, console, palette):
        super().__init__(console, palette)
        self.window = window

    @functools.lru_cache(maxsize=None)
    def get_color(self, color):
        if color is None:
            return None
        return self.palette.get(color)


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

    CONSOLE_CLS = ConsoleIndexedColors
    ROOT_PANEL_CLS = CursesRootPanel

    def __init__(self,
        console_size,
        palette,
        *args, **kwargs,
    ):
        super().__init__(console_size=console_size, palette=palette, *args, **kwargs)
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
        sys.stdout.write(term.save_title())
        if title:
            sys.stdout.write(term.set_title(title))
        sys.stdout.flush()

    def restore_title(self):
        sys.stdout.write(term.restore_title())
        sys.stdout.flush()

    def initialize_keyboard(self):
        # Allow 8-bit characters input
        curses.meta(True)

    def initialize_mouse(self):
        # Set the mouse events to be reported
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        # No interval for mouse clicks - separate BUTTONx_PRESSED / _RELEASED will be used!
        curses.mouseinterval(0)

    def initialize_input(self):
        self.initialize_keyboard()
        self.initialize_mouse()
        input = CursesInputWrapper(self._screen)
        return input

    def hide_cursor(self):
        curses.curs_set(0)

    def show_cursor(self):
        curses.curs_set(2)

    def initialize(self):
        if self.is_initialized:
            return
        # Mouse support?
        # See: https://stackoverflow.com/questions/5966903/how-to-get-mousemove-and-mouseclick-in-bash
        # NOTE: Seems to be messing with curses mouse support...
        # sys.stdout.write('\033[?1000h')
        # sys.stdout.write('\033[?1003h')
        # sys.stdout.write('\033[?1015h')
        # sys.stdout.write('\033[?1006h')

        self.set_title(self.title)

        self._screen = self.initialize_screen()
        self._input = self.initialize_input()

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

    def get_size(self):
        return self.screen.getmaxyx()

    def create_panel(self, size=None):
        # TODO: Ensure terminal size is big enough!
        console = self.create_console(size)
        window = self.initialize_window(
            curses.newwin(console.height, console.width)
        )
        return self.ROOT_PANEL_CLS(window, console, self.palette)

    def flush(self, panel):
        prev_fg = -1
        prev_bg = -1
        color_pair = self.color_pairs.get_pair(prev_fg, prev_bg)
        panel.window.move(0, 0)
        for ch, fg, bg in panel.console.tiles_gen(encode_ch=chr):
            if (not fg == prev_fg) or (not bg == prev_bg):
                color_pair = self.color_pairs.get_pair(fg, bg)
                panel.window.attrset(color_pair)
            try:
                panel.window.addch(ch)
            except curses.error:
                # NOTE: Writing to last column & row moves cursor outside window and raises error
                pass
        panel.window.refresh()
        curses.doupdate()

