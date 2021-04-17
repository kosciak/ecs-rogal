import curses
import logging

from .core import IOWrapper


log = logging.getLogger(__name__)


# NOTE: Just some biolerplate code for initialisation / closing curses screen
#       Main problem is explicit initialisation of all color pairs
#       Would need to reverse check index of color in pallette, and init_pair() for each combination


class CursesWrapper(IOWrapper):

    def __init__(self,
        console_size,
        palette,
    ):
        super().__init__(console_size, palette)
        self.console_size = console_size
        self._palette = palette
        self._screen = None

    @property
    def is_initialized(self):
        return self._screen is not None

    @property
    def screen(self):
        if not self.is_initialized:
            screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.keypad(True)
            try:
                curses.start_color()
                curses.use_default_colors()
            except:
                pass

            # TODO: Is it needed?
            screen.keypad(True)
            screen.immedok(False)
            screen.scrollok(False) 

            self._screen = screen

    def flush(self, console):
        curses.doupdate()

    def close(self):
        if self.is_initialized:
            self._screen.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self._screen = None

