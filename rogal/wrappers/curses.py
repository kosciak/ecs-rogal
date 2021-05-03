import curses
import curses.ascii
import functools
import logging
import signal

from .. import events
from ..events.mouse import MouseButton
from ..events.keys import Key

from .core import IOWrapper


log = logging.getLogger(__name__)


# NOTE: Just some biolerplate code for initialisation / closing curses screen
#       Main problem is explicit initialisation of all color pairs
#       Would need to reverse check index of color in pallette, and init_pair() for each combination

CURSES_KEYCODES = {
    curses.ascii.ESC: Key.ESCAPE, # '^['

    curses.KEY_F1: Key.F1,
    curses.KEY_F2: Key.F2,
    curses.KEY_F3: Key.F3,
    curses.KEY_F4: Key.F4,
    curses.KEY_F5: Key.F5,
    curses.KEY_F6: Key.F6,
    curses.KEY_F7: Key.F7,
    curses.KEY_F8: Key.F8,
    curses.KEY_F9: Key.F9,
    curses.KEY_F10: Key.F10,
    curses.KEY_F11: Key.F11,
    curses.KEY_F12: Key.F12,

    curses.KEY_BACKSPACE: Key.BACKSPACE,
    curses.ascii.BS: Key.BACKSPACE,

    curses.ascii.TAB: Key.TAB,

    curses.KEY_ENTER: Key.RETURN,
    curses.ascii.CR: Key.RETURN,
    curses.ascii.NL: Key.RETURN,

    curses.ascii.SP: Key.SPACE,

    curses.KEY_UP: Key.UP,
    curses.KEY_DOWN: Key.DOWN,
    curses.KEY_LEFT: Key.LEFT,
    curses.KEY_RIGHT: Key.RIGHT,

    curses.KEY_IC: Key.INSERT,
    curses.KEY_DC: Key.DELETE,
    curses.KEY_HOME: Key.HOME,
    curses.KEY_END: Key.END,
    curses.KEY_PPAGE: Key.PAGE_UP,
    curses.KEY_NPAGE: Key.PAGE_DOWN,

    curses.KEY_C1: Key.KP_1,
    curses.KEY_C3: Key.KP_3,
    curses.KEY_B2: Key.KP_5,
    curses.KEY_A1: Key.KP_7,
    curses.KEY_A3: Key.KP_9,

    574: Key.KP_5,
    575: Key.KP_PLUS,
    577: Key.KP_DIVIDE,
    579: Key.KP_MULTIPLY,
    580: Key.KP_MINUS,
}


CURSES_SHIFT_KEYCODES = {
    curses.KEY_F13: Key.F1,
    curses.KEY_F14: Key.F2,
    curses.KEY_F15: Key.F3,
    curses.KEY_F16: Key.F4,
    curses.KEY_F17: Key.F5,
    curses.KEY_F18: Key.F6,
    curses.KEY_F19: Key.F7,
    curses.KEY_F20: Key.F8,
    curses.KEY_F21: Key.F9,
    curses.KEY_F22: Key.F10,
    curses.KEY_F23: Key.F11,
    curses.KEY_F24: Key.F12,

    curses.KEY_BTAB: Key.TAB,

    curses.KEY_SR: Key.UP,
    curses.KEY_SF: Key.DOWN,
    curses.KEY_SLEFT: Key.LEFT,
    curses.KEY_SRIGHT: Key.RIGHT,

    curses.KEY_SIC: Key.INSERT,
    curses.KEY_SDC: Key.DELETE,
    curses.KEY_SHOME: Key.HOME,
    curses.KEY_SEND: Key.END,
    curses.KEY_SPREVIOUS: Key.PAGE_UP,
    curses.KEY_SNEXT: Key.PAGE_DOWN,
}


@functools.lru_cache(maxsize=None)
def get_key(sym, mod):
    key = None
    with_ctrl = False
    with_shift = False
    # NOTE: Not able to get ALT modifier; GUI key is not supported at all

    if not isinstance(sym, int):
        if not curses.ascii.isascii(sym):
            # Non-ASCII wide character
            return
        sym = ord(sym)

    # ASCII characters
    if 32 <= sym <= 126:
        key = chr(sym)

    # Non alphanumeric keys
    if key is None:
        key = CURSES_KEYCODES.get(sym)

    # Non alphanumeric keys with SHIFT
    if key is None:
        key = CURSES_SHIFT_KEYCODES.get(sym)
        if key:
            with_shift = True

    # Keys with CTRL
    if key is None and curses.ascii.isctrl(sym):
        with_ctrl = True
        key = curses.ascii.unctrl(sym).lower().strip('^')

    # Not able to match to any other key (for example some keypad keys without NumLock)
    if key is None:
        print(curses.keyname(sym))
        key = str(sym)

    return Key.with_modifiers(
        key,
        ctrl=with_ctrl,
        # alt=False,
        shift=with_shift,
        # gui=False,
    )


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

        # TODO: MouseWheel events? WheelUp seems to be: BUTTON4_PRESSED and WheelDown: 0x200000

    else:
        # print('event: %r - %s %s' % (curses_event, curses.ascii.iscntrl(curses_event), curses.ascii.isctrl(curses_event) and curses.ascii.unctrl(curses_event)))
        key = get_key(curses_event, None)
        if key:
            yield events.KeyPress(curses_event, key)
        if not isinstance(curses_event, int) and not curses.ascii.isctrl(curses_event):
            yield events.TextInput(curses_event, curses_event)
        if key:
            yield events.KeyUp(curses_event, key)


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

    def _signal_handler(self, signal_no, frame):
        if signal_no == signal.SIGINT:
            curses.ungetch(3)
        elif signal_no == signal.SIGTSTP:
            curses.ungetch(26)

    @property
    def is_initialized(self):
        return self._screen is not None

    def initialize(self):
        if self.is_initialized:
            return

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

        # Enter keypad mode - escape sequences for special keys will be interpreted
        screen.keypad(True)

        # Don't refresh automatically on window change
        screen.immedok(False)
        # Don't scroll on bottom line
        screen.scrollok(False)
        # Make getch() non blocking; consided curses.halfdelay()
        screen.nodelay(True)

        curses.halfdelay(2)

        # Catch ^c
        signal.signal(signal.SIGINT, self._signal_handler)
        # Catch ^z - doesn't seem to work properly...
        # signal.signal(signal.SIGTSTP, self._signal_handler)

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

