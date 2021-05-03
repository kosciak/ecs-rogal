import curses
import curses.ascii
import functools
import logging
import os
import signal

from .. import events
from ..events.mouse import MouseButton
from ..events.keys import Key, Keycode

from .core import IOWrapper


log = logging.getLogger(__name__)


# NOTE: Just some biolerplate code for initialisation / closing curses screen
#       Main problem is explicit initialisation of all color pairs
#       Would need to reverse check index of color in pallette, and init_pair() for each combination

CURSES_KEYCODES = {
    curses.ascii.ESC: Keycode.ESCAPE, # '^['

    curses.KEY_F1: Keycode.F1,
    curses.KEY_F2: Keycode.F2,
    curses.KEY_F3: Keycode.F3,
    curses.KEY_F4: Keycode.F4,
    curses.KEY_F5: Keycode.F5,
    curses.KEY_F6: Keycode.F6,
    curses.KEY_F7: Keycode.F7,
    curses.KEY_F8: Keycode.F8,
    curses.KEY_F9: Keycode.F9,
    curses.KEY_F10: Keycode.F10,
    curses.KEY_F11: Keycode.F11,
    curses.KEY_F12: Keycode.F12,

    curses.KEY_BACKSPACE: Keycode.BACKSPACE,
    curses.ascii.BS: Keycode.BACKSPACE,

    curses.ascii.TAB: Keycode.TAB,

    curses.KEY_ENTER: Keycode.RETURN,
    curses.ascii.CR: Keycode.RETURN,
    curses.ascii.NL: Keycode.RETURN,

    curses.ascii.SP: Keycode.SPACE,

    curses.KEY_UP: Keycode.UP,
    curses.KEY_DOWN: Keycode.DOWN,
    curses.KEY_LEFT: Keycode.LEFT,
    curses.KEY_RIGHT: Keycode.RIGHT,

    curses.KEY_IC: Keycode.INSERT,
    curses.KEY_DC: Keycode.DELETE,
    curses.KEY_HOME: Keycode.HOME,
    curses.KEY_END: Keycode.END,
    curses.KEY_PPAGE: Keycode.PAGE_UP,
    curses.KEY_NPAGE: Keycode.PAGE_DOWN,

    curses.KEY_C1: Keycode.KP_1,
    curses.KEY_C3: Keycode.KP_3,
    curses.KEY_B2: Keycode.KP_5,
    curses.KEY_A1: Keycode.KP_7,
    curses.KEY_A3: Keycode.KP_9,

    574: Keycode.KP_5,
    575: Keycode.KP_PLUS,
    577: Keycode.KP_DIVIDE,
    579: Keycode.KP_MULTIPLY,
    580: Keycode.KP_MINUS,
}


CURSES_SHIFT_KEYCODES = {
    curses.KEY_F13: Keycode.F1,
    curses.KEY_F14: Keycode.F2,
    curses.KEY_F15: Keycode.F3,
    curses.KEY_F16: Keycode.F4,
    curses.KEY_F17: Keycode.F5,
    curses.KEY_F18: Keycode.F6,
    curses.KEY_F19: Keycode.F7,
    curses.KEY_F20: Keycode.F8,
    curses.KEY_F21: Keycode.F9,
    curses.KEY_F22: Keycode.F10,
    curses.KEY_F23: Keycode.F11,
    curses.KEY_F24: Keycode.F12,

    curses.KEY_BTAB: Keycode.TAB,

    curses.KEY_SR: Keycode.UP,
    curses.KEY_SF: Keycode.DOWN,
    curses.KEY_SLEFT: Keycode.LEFT,
    curses.KEY_SRIGHT: Keycode.RIGHT,

    curses.KEY_SIC: Keycode.INSERT,
    curses.KEY_SDC: Keycode.DELETE,
    curses.KEY_SHOME: Keycode.HOME,
    curses.KEY_SEND: Keycode.END,
    curses.KEY_SPREVIOUS: Keycode.PAGE_UP,
    curses.KEY_SNEXT: Keycode.PAGE_DOWN,
}


@functools.lru_cache(maxsize=None)
def get_key(key):
    keycode = None
    with_ctrl = False
    with_shift = False
    # NOTE: Not able to get ALT modifier; GUI key is not supported at all

    if not isinstance(key, int):
        if not curses.ascii.isascii(key):
            # Non-ASCII wide character
            return
        key = ord(key)

    # ASCII characters
    if 32 <= key <= 126:
        keycode = key

    # Non alphanumeric keys
    if keycode is None:
        keycode = CURSES_KEYCODES.get(key)

    # Non alphanumeric keys with SHIFT
    if keycode is None:
        keycode = CURSES_SHIFT_KEYCODES.get(key)
        if keycode:
            with_shift = True

    # Keys with CTRL
    if keycode is None and curses.ascii.isctrl(key):
        with_ctrl = True
        key = curses.ascii.unctrl(key).lower().strip('^')
        keycode = ord(key)

    # Not able to match to any other key (for example some keypad keys without NumLock)
    if keycode is None:
        # print(curses.keyname(key))
        keycode = key

    return Key(
        keycode,
        ctrl=with_ctrl,
        shift=with_shift,
        # alt=False,
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
        key = get_key(curses_event)
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
        self.__prev_esc_delay = None
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
            del os.environ['ESCDELAY']
            if self.__prev_escdelay:
                os.environ['ESCDELAY'] = self.__prev_escdelay
            self._screen = None

