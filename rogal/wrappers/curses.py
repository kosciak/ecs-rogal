import curses
import curses.ascii
import logging

from .. import events
from ..events.mouse import MouseButton

from .core import IOWrapper


log = logging.getLogger(__name__)


# NOTE: Just some biolerplate code for initialisation / closing curses screen
#       Main problem is explicit initialisation of all color pairs
#       Would need to reverse check index of color in pallette, and init_pair() for each combination


def parse_curses_event(curses_event):
    if curses_event == curses.ERR:
        # No event returned
        return
    if curses_event == curses.KEY_MOUSE:
        # NOTE: mz is always 0
        device_id, mx, my, mz, button_state = curses.getmouse()

        # NOTE: if curses.mouseinterval > 0 - only *_CLICKED is emited (instead of *_PRESSED, *_RELEASED)
        #       Otherwise separate *_PRESSED and *_RELEASED are emitted
        if button_state & curses.BUTTON1_CLICKED:
            yield events.MouseButtonPress(curses_event, mx, my, MouseButton.LEFT)
            yield events.MouseButtonUp(curses_event, mx, my, MouseButton.LEFT)
        if button_state & curses.BUTTON1_PRESSED:
            yield events.MouseButtonPress(curses_event, mx, my, MouseButton.LEFT)
        if button_state & curses.BUTTON1_RELEASED:
            yield events.MouseButtonUp(curses_event, mx, my, MouseButton.LEFT)

        if button_state & curses.BUTTON2_CLICKED:
            yield events.MouseButtonPress(curses_event, mx, my, MouseButton.MIDDLE)
            yield events.MouseButtonUp(curses_event, mx, my, MouseButton.MIDDLE)
        if button_state & curses.BUTTON2_PRESSED:
            yield events.MouseButtonPress(curses_event, mx, my, MouseButton.MIDDLE)
        if button_state & curses.BUTTON2_RELEASED:
            yield events.MouseButtonUp(curses_event, mx, my, MouseButton.MIDDLE)

        if button_state & curses.BUTTON3_CLICKED:
            yield events.MouseButtonPress(curses_event, mx, my, MouseButton.RIGHT)
            yield events.MouseButtonUp(curses_event, mx, my, MouseButton.RIGHT)
        if button_state & curses.BUTTON3_PRESSED:
            yield events.MouseButtonPress(curses_event, mx, my, MouseButton.RIGHT)
        if button_state & curses.BUTTON3_RELEASED:
            yield events.MouseButtonUp(curses_event, mx, my, MouseButton.RIGHT)

        # TODO: MouseWheel events? BUTTON4_PRESSED and 0x200000

    else:
        print('event: %r - %s %s' % (curses_event, curses.ascii.iscntrl(curses_event), curses.ascii.isctrl(curses_event)))
        if curses.ascii.isctrl(curses_event):
            curses_event = ord(curses_event)
        if isinstance(curses_event, int):
            print(curses_event, curses.keyname(curses_event))
            # TODO yield KeyPress, KeyUp
        else:
            yield events.TextInput(curses_event, curses_event)
        yield events.UnknownEvent(curses_event)


class CursesWrapper(IOWrapper):

    def __init__(self,
        console_size,
        palette,
        *args, **kwargs,
    ):
        super().__init__(console_size, palette)
        self.console_size = console_size
        self._palette = palette
        self._screen = None

    @property
    def is_initialized(self):
        return self._screen is not None

    def initialize(self):
        if self.is_initialized:
            return

        screen = curses.initscr()

        # Turn off echoing of keys
        curses.noecho()
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

        # Enter keypad mode - escape sequences for special keys will be interpreted
        screen.keypad(True)

        # Don't refresh automatically on window change
        screen.immedok(False)
        # Don't scroll on bottom line
        screen.scrollok(False)
        # Make getch() non blocking; consided curses.halfdelay()
        screen.nodelay(True)

        curses.halfdelay(2)

        self._screen = screen

    @property
    def screen(self):
        self.initialize()
        return self._screen

    def flush(self, console):
        curses.doupdate()

    def update_event(self, event):
        if event.type == events.EventType.MOUSE_MOTION or \
           event.type == events.EventType.MOUSE_BUTTON_PRESS or\
           event.type == events.EventType.MOUSE_BUTTON_UP:
            event.set_tile(*event.pixel_position)
        return event

    def process_events(self, events):
        """Process events - update, filter, merge, etc."""
        processed_events = []
        for event in list(events):
            event = self.update_event(event)
            processed_events.append(event)
        return processed_events

    def get_events_gen(self, wait=None):
        self.initialize()

        # TODO: basic curses event handling
        if wait is False:
            self.screen.nodelay(True)
        elif wait is None or wait is True:
            # NOTE: wait==None will wait forever
            self.screen.nodelay(False)
        try:
            # event = self.screen.getch()
            event = self.screen.get_wch()
            # event = self.screen.getkey()
        except curses.error:
            # if nodelay(True) -> curses.error: no input is raised!
            return
        yield from parse_curses_event(event)

    def close(self):
        if self.is_initialized:
            # Cleanup all settings back to defaults
            self._screen.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self._screen = None

