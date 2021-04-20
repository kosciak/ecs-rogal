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

            # Turn off echoing of keys
            curses.noecho()
            # No buffering on keyboard input
            curses.cbreak()
            # Set the mouse events to be reported
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
            # Enter keypad mode - escape sequences for special keys will be interpreted
            screen.keypad(True)

            # Initialize colors and set default console colors as color_pair(0)
            try:
                curses.start_color()
                curses.use_default_colors()
            except:
                pass

            # Don't refresh automatically on window change
            screen.immedok(False)
            # Don't scroll on bottom line
            screen.scrollok(False)
            # Make getch() non blocking; consided curses.halfdelay()
            screen.nodelay(True)

            self._screen = screen

    def flush(self, console):
        curses.doupdate()

    def events(self, wait=None):
        # TODO: basic curses event handling
        if wait is False:
            self.screen.nodelay(True)
        elif wait is None or wait is True:
            # NOTE: wait==None will wait forever
            self.screen.nodelay(False)
        # curses.halfdelay(2)
        try:
            # event = stdscr.getch()
            event = stdscr.get_wch()
            # event = stdscr.getkey()
        except curses.error:
            # if nodelay(True) -> curses.error: no input is raised!
            continue
        if event == curses.ERR:
            # No event returned
            continue
        if event == curses.KEY_MOUSE:
            # NOTE: mz is always 0
            device_id, mx, my, mz, button_state = curses.getmouse()
        else:
            return event

    def close(self):
        if self.is_initialized:
            # Cleanup all settings back to defaults
            self._screen.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self._screen = None

