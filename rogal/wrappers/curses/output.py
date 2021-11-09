import curses
import functools
import logging

from ...console.consoles import IndexedColorsConsole
from ...console.panels import RootPanel

from ..core import OutputWrapper


log = logging.getLogger(__name__)


class CursesRootPanel(RootPanel):

    def __init__(self, window, console, colors_manager):
        super().__init__(console, colors_manager)
        self.window = window

    def get_color(self, color):
        if color is None:
            return None
        return self.colors_manager.get(color)


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

    @functools.lru_cache(maxsize=None)
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


class CursesOutputWrapper(OutputWrapper):

    CONSOLE_CLS = IndexedColorsConsole
    ROOT_PANEL_CLS = CursesRootPanel

    def __init__(self, colors_manager):
        super().__init__(colors_manager)
        self.color_pairs = ColorPairsManager()

    def create_panel(self, window, size):
        # TODO: Ensure terminal size is big enough!
        console = self.create_console(size)
        return self.ROOT_PANEL_CLS(window, console, self.colors_manager)

    def render(self, panel):
        prev_fg = -1
        prev_bg = -1
        color_pair = self.color_pairs.get_pair(prev_fg, prev_bg)
        panel.window.move(0, 0)
        # NOTE: That's... slow... very slow...
        for x, y, ch, fg, bg in panel.console.tiles_gen(encode_ch=chr):
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

