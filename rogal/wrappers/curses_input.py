import curses
import curses.ascii
import logging
import functools
import signal

from .. import events
from ..events.mouse import MouseButton
from ..events.keys import Key, Keycode, Modifier

from .core import InputWrapper


log = logging.getLogger(__name__)


# NOTE: For ALT modifier to work use Left-ALT
# NOTE: GUI key is not supported at all

# NOTE: Left ALT + key -> separate events ^[ + key (ESCAPE + key)

CURSES_KEYCODES = {
    curses.ascii.ESC:   (Keycode.ESCAPE, Modifier.NONE), # '^['

    curses.KEY_F1:      (Keycode.F1, Modifier.NONE),
    curses.KEY_F2:      (Keycode.F2, Modifier.NONE),
    curses.KEY_F3:      (Keycode.F3, Modifier.NONE),
    curses.KEY_F4:      (Keycode.F4, Modifier.NONE),
    curses.KEY_F5:      (Keycode.F5, Modifier.NONE),
    curses.KEY_F6:      (Keycode.F6, Modifier.NONE),
    curses.KEY_F7:      (Keycode.F7, Modifier.NONE),
    curses.KEY_F8:      (Keycode.F8, Modifier.NONE),
    curses.KEY_F9:      (Keycode.F9, Modifier.NONE),
    curses.KEY_F10:     (Keycode.F10, Modifier.NONE),
    curses.KEY_F11:     (Keycode.F11, Modifier.NONE),
    curses.KEY_F12:     (Keycode.F12, Modifier.NONE),

    curses.KEY_BACKSPACE:   (Keycode.BACKSPACE, Modifier.NONE),
    curses.ascii.BS:        (Keycode.BACKSPACE, Modifier.NONE),

    curses.ascii.TAB:   (Keycode.TAB, Modifier.NONE),

    curses.KEY_ENTER:   (Keycode.RETURN, Modifier.NONE),
    curses.ascii.CR:    (Keycode.RETURN, Modifier.NONE),
    curses.ascii.NL:    (Keycode.RETURN, Modifier.NONE),

    curses.ascii.SP:    (Keycode.SPACE, Modifier.NONE),

    curses.KEY_UP:      (Keycode.UP, Modifier.NONE),
    curses.KEY_DOWN:    (Keycode.DOWN, Modifier.NONE),
    curses.KEY_LEFT:    (Keycode.LEFT, Modifier.NONE),
    curses.KEY_RIGHT:   (Keycode.RIGHT, Modifier.NONE),

    curses.KEY_IC:      (Keycode.INSERT, Modifier.NONE),
    curses.KEY_DC:      (Keycode.DELETE, Modifier.NONE),
    curses.KEY_HOME:    (Keycode.HOME, Modifier.NONE),
    curses.KEY_END:     (Keycode.END, Modifier.NONE),
    curses.KEY_PPAGE:   (Keycode.PAGE_UP, Modifier.NONE),
    curses.KEY_NPAGE:   (Keycode.PAGE_DOWN, Modifier.NONE),

    curses.KEY_C1:      (Keycode.KP_1, Modifier.NONE),
    curses.KEY_C3:      (Keycode.KP_3, Modifier.NONE),
    curses.KEY_B2:      (Keycode.KP_5, Modifier.NONE),
    curses.KEY_A1:      (Keycode.KP_7, Modifier.NONE),
    curses.KEY_A3:      (Keycode.KP_9, Modifier.NONE),

    curses.KEY_F13:     (Keycode.F1, Modifier.SHIFT),
    curses.KEY_F14:     (Keycode.F2, Modifier.SHIFT),
    curses.KEY_F15:     (Keycode.F3, Modifier.SHIFT),
    curses.KEY_F16:     (Keycode.F4, Modifier.SHIFT),
    curses.KEY_F17:     (Keycode.F5, Modifier.SHIFT),
    curses.KEY_F18:     (Keycode.F6, Modifier.SHIFT),
    curses.KEY_F19:     (Keycode.F7, Modifier.SHIFT),
    curses.KEY_F20:     (Keycode.F8, Modifier.SHIFT),
    curses.KEY_F21:     (Keycode.F9, Modifier.SHIFT),
    curses.KEY_F22:     (Keycode.F10, Modifier.SHIFT),
    curses.KEY_F23:     (Keycode.F11, Modifier.SHIFT),
    curses.KEY_F24:     (Keycode.F12, Modifier.SHIFT),

    curses.KEY_BTAB:    (Keycode.TAB, Modifier.SHIFT),

    curses.KEY_SR:      (Keycode.UP, Modifier.SHIFT),
    curses.KEY_SF:      (Keycode.DOWN, Modifier.SHIFT),
    curses.KEY_SLEFT:   (Keycode.LEFT, Modifier.SHIFT),
    curses.KEY_SRIGHT:  (Keycode.RIGHT, Modifier.SHIFT),

    curses.KEY_SIC:     (Keycode.INSERT, Modifier.SHIFT),
    curses.KEY_SDC:     (Keycode.DELETE, Modifier.SHIFT),
    curses.KEY_SHOME:   (Keycode.HOME, Modifier.SHIFT),
    curses.KEY_SEND:    (Keycode.END, Modifier.SHIFT),
    curses.KEY_SPREVIOUS:   (Keycode.PAGE_UP, Modifier.SHIFT),
    curses.KEY_SNEXT:   (Keycode.PAGE_DOWN, Modifier.SHIFT),

    curses.KEY_F25:     (Keycode.F1, Modifier.CTRL),
    curses.KEY_F26:     (Keycode.F2, Modifier.CTRL),
    curses.KEY_F27:     (Keycode.F3, Modifier.CTRL),
    curses.KEY_F28:     (Keycode.F4, Modifier.CTRL),
    curses.KEY_F29:     (Keycode.F5, Modifier.CTRL),
    curses.KEY_F30:     (Keycode.F6, Modifier.CTRL),
    curses.KEY_F31:     (Keycode.F7, Modifier.CTRL),
    curses.KEY_F32:     (Keycode.F8, Modifier.CTRL),
    curses.KEY_F33:     (Keycode.F9, Modifier.CTRL),
    curses.KEY_F34:     (Keycode.F10, Modifier.CTRL),
    curses.KEY_F35:     (Keycode.F11, Modifier.CTRL),
    curses.KEY_F36:     (Keycode.F12, Modifier.CTRL),

    curses.KEY_F37:     (Keycode.F1, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F38:     (Keycode.F2, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F39:     (Keycode.F3, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F40:     (Keycode.F4, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F41:     (Keycode.F5, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F42:     (Keycode.F6, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F43:     (Keycode.F7, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F44:     (Keycode.F8, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F45:     (Keycode.F9, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F46:     (Keycode.F10, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F47:     (Keycode.F11, Modifier.CTRL | Modifier.SHIFT),
    curses.KEY_F48:     (Keycode.F12, Modifier.CTRL | Modifier.SHIFT),
}


# NOTE: These keys might have different codes depending on term settings, better to use keyname
CURSES_KEYNAMES = {
    b'kf1':     (Keycode.F1, Modifier.NONE),
    b'kf2':     (Keycode.F2, Modifier.NONE),
    b'kf3':     (Keycode.F3, Modifier.NONE),
    b'kf4':     (Keycode.F4, Modifier.NONE),

    b'kp0':     (Keycode.KP_0, Modifier.NONE),
    b'kp1':     (Keycode.KP_1, Modifier.NONE),
    b'kp2':     (Keycode.KP_2, Modifier.NONE),
    b'kp3':     (Keycode.KP_3, Modifier.NONE),
    b'kp4':     (Keycode.KP_4, Modifier.NONE),
    b'kp5':     (Keycode.KP_5, Modifier.NONE),
    b'kp6':     (Keycode.KP_6, Modifier.NONE),
    b'kp7':     (Keycode.KP_7, Modifier.NONE),
    b'kp8':     (Keycode.KP_8, Modifier.NONE),
    b'kp9':     (Keycode.KP_9, Modifier.NONE),

    b'kpDIV':   (Keycode.KP_DIVIDE, Modifier.NONE),
    b'kpMUL':   (Keycode.KP_MULTIPLY, Modifier.NONE),
    b'kpSUB':   (Keycode.KP_MINUS, Modifier.NONE),
    b'kpADD':   (Keycode.KP_PLUS, Modifier.NONE),
    b'kpDOT':   (Keycode.KP_PERIOD, Modifier.NONE),
    b'kpZRO':   (Keycode.KP_0, Modifier.NONE), # NOT sure about this one
    b'kpCMA':   (Keycode.KP_COMMA, Modifier.NONE), # NOT sure about this one

    b'kUP3':    (Keycode.UP, Modifier.ALT),
    b'kDN3':    (Keycode.DOWN, Modifier.ALT),
    b'kLFT3':   (Keycode.LEFT, Modifier.ALT),
    b'kRIT3':   (Keycode.RIGHT, Modifier.ALT),

    b'kIC3':    (Keycode.INSERT, Modifier.ALT),
    b'kDC3':    (Keycode.DELETE, Modifier.ALT),
    b'kHOM3':   (Keycode.HOME, Modifier.ALT),
    b'kEND3':   (Keycode.END, Modifier.ALT),
    b'kPRV3':   (Keycode.PAGE_UP, Modifier.ALT),
    b'kNXT3':   (Keycode.PAGE_DOWN, Modifier.ALT),

    b'kUP4':    (Keycode.UP, Modifier.ALT | Modifier.SHIFT),
    b'kDN4':    (Keycode.DOWN, Modifier.ALT | Modifier.SHIFT),
    b'kLFT4':   (Keycode.LEFT, Modifier.ALT | Modifier.SHIFT),
    b'kRIT4':   (Keycode.RIGHT, Modifier.ALT | Modifier.SHIFT),

    b'kIC4':    (Keycode.INSERT, Modifier.ALT | Modifier.SHIFT),
    b'kDC4':    (Keycode.DELETE, Modifier.ALT | Modifier.SHIFT),
    b'kHOM4':   (Keycode.HOME, Modifier.ALT | Modifier.SHIFT),
    b'kEND4':   (Keycode.END, Modifier.ALT | Modifier.SHIFT),
    b'kPRV4':   (Keycode.PAGE_UP, Modifier.ALT | Modifier.SHIFT),
    b'kNXT4':   (Keycode.PAGE_DOWN, Modifier.ALT | Modifier.SHIFT),

    b'kUP5':    (Keycode.UP, Modifier.CTRL),
    b'kDN5':    (Keycode.DOWN, Modifier.CTRL),
    b'kLFT5':   (Keycode.LEFT, Modifier.CTRL),
    b'kRIT5':   (Keycode.RIGHT, Modifier.CTRL),

    b'kIC5':    (Keycode.INSERT, Modifier.CTRL),
    b'kDC5':    (Keycode.DELETE, Modifier.CTRL),
    b'kHOM5':   (Keycode.HOME, Modifier.CTRL),
    b'kEND5':   (Keycode.END, Modifier.CTRL),
    b'kPRV5':   (Keycode.PAGE_UP, Modifier.CTRL),
    b'kNXT5':   (Keycode.PAGE_DOWN, Modifier.CTRL),

    b'kUP6':    (Keycode.UP, Modifier.CTRL | Modifier.SHIFT),
    b'kDN6':    (Keycode.DOWN, Modifier.CTRL | Modifier.SHIFT),
    b'kLFT6':   (Keycode.LEFT, Modifier.CTRL | Modifier.SHIFT),
    b'kRIT6':   (Keycode.RIGHT, Modifier.CTRL | Modifier.SHIFT),

    b'kIC6':    (Keycode.INSERT, Modifier.CTRL | Modifier.SHIFT),
    b'kDC6':    (Keycode.DELETE, Modifier.CTRL | Modifier.SHIFT),
    b'kHOM6':   (Keycode.HOME, Modifier.CTRL | Modifier.SHIFT),
    b'kEND6':   (Keycode.END, Modifier.CTRL | Modifier.SHIFT),
    b'kPRV6':   (Keycode.PAGE_UP, Modifier.CTRL | Modifier.SHIFT),
    b'kNXT6':   (Keycode.PAGE_DOWN, Modifier.CTRL | Modifier.SHIFT),

    b'kUP7':    (Keycode.UP, Modifier.CTRL | Modifier.ALT),
    b'kDN7':    (Keycode.DOWN, Modifier.CTRL | Modifier.ALT),
    b'kLFT7':   (Keycode.LEFT, Modifier.CTRL | Modifier.ALT),
    b'kRIT7':   (Keycode.RIGHT, Modifier.CTRL | Modifier.ALT),

    b'kIC7':    (Keycode.INSERT, Modifier.CTRL | Modifier.ALT),
    b'kDC7':    (Keycode.DELETE, Modifier.CTRL | Modifier.ALT),
    b'kHOM7':   (Keycode.HOME, Modifier.CTRL | Modifier.ALT),
    b'kEND7':   (Keycode.END, Modifier.CTRL | Modifier.ALT),
    b'kPRV7':   (Keycode.PAGE_UP, Modifier.CTRL | Modifier.ALT),
    b'kNXT7':   (Keycode.PAGE_DOWN, Modifier.CTRL | Modifier.ALT),
}


CURSES_ESCAPE_SEQUENCES = {
    'OP':   (Keycode.F1, Modifier.NONE),
    'OQ':   (Keycode.F2, Modifier.NONE),
    'OR':   (Keycode.F3, Modifier.NONE),
    'OS':   (Keycode.F4, Modifier.NONE),

    'Op':   (Keycode.KP_0, Modifier.NONE),
    'Oq':   (Keycode.KP_1, Modifier.NONE),
    'Or':   (Keycode.KP_2, Modifier.NONE),
    'Os':   (Keycode.KP_3, Modifier.NONE),
    'Ot':   (Keycode.KP_4, Modifier.NONE),
    'Ou':   (Keycode.KP_5, Modifier.NONE),
    'Ov':   (Keycode.KP_6, Modifier.NONE),
    'Ow':   (Keycode.KP_7, Modifier.NONE),
    'Ox':   (Keycode.KP_8, Modifier.NONE),
    'Oy':   (Keycode.KP_9, Modifier.NONE),

    'Oo':   (Keycode.KP_DIVIDE, Modifier.NONE),
    'Oj':   (Keycode.KP_MULTIPLY, Modifier.NONE),
    'Om':   (Keycode.KP_MINUS, Modifier.NONE),
    'Ok':   (Keycode.KP_PLUS, Modifier.NONE),
    'On':   (Keycode.KP_PERIOD, Modifier.NONE),
    'Ol':   (Keycode.KP_COMMA, Modifier.NONE), # NOT sure about this one

    'OM':   (Keycode.ENTER, Modifier.NONE), # NOT sure about this one

    # urxvt
    '[a':   (Keycode.UP, Modifier.SHIFT),
    '[b':   (Keycode.DOWN, Modifier.SHIFT),
    'Oa':   (Keycode.UP, Modifier.CTRL),
    'Ob':   (Keycode.DOWN, Modifier.CTRL),
    'Od':   (Keycode.LEFT, Modifier.CTRL),
    'Oc':   (Keycode.RIGHT, Modifier.CTRL),
}


@functools.lru_cache(maxsize=None)
def get_key(key, escaped=False):
    # Escape sequences not recognised properly by curses
    if escaped and isinstance(key, tuple):
        keycode, modifiers = CURSES_ESCAPE_SEQUENCES.get(''.join(key), (None, None))
        if keycode:
            return Key(keycode, modifiers=modifiers)
        else:
            return

    if not isinstance(key, int):
        if not curses.ascii.isascii(key):
            # Non-ASCII wide character
            return
        key = ord(key)

    # ASCII characters
    if 32 < key < 127:
        keycode = key
        return Key(keycode, alt=escaped)

    # Non alphanumeric keys
    keycode, modifiers = CURSES_KEYCODES.get(key, (None, None))
    if keycode:
        return Key(keycode, modifiers=modifiers, alt=escaped)

    # Keys with CTRL
    if curses.ascii.isctrl(key):
        key = curses.ascii.unctrl(key).lower().strip('^')
        keycode = ord(key)
        return Key(keycode, ctrl=True)

    # Named keycodes, integer value may vary between terminals
    name = curses.keyname(key)
    keycode, modifiers = CURSES_KEYNAMES.get(name, (None, None))
    if keycode:
        return Key(keycode, modifiers=modifiers)

    # Not able to match to any other key
    keycode = key
    return Key(keycode)


def parse_mouse_event(event):
    # NOTE: mz is always 0
    device_id, mx, my, mz, button_state = curses.getmouse()

    # TODO: MouseButton + Modifers? curses.BUTTON_SHIFT, curses.BUTTON_ALT, curses.BUTTON_CTRL flags
    modifiers = Modifier.NONE
    if button_state & curses.BUTTON_CTRL:
        modifiers |= Modifier.CTRL
    if button_state & curses.BUTTON_ALT:
        modifiers |= Modifier.ALT
    if button_state & curses.BUTTON_SHIFT:
        modifiers |= Modifier.SHIFT

    # NOTE: if curses.mouseinterval > 0 - only *_CLICKED is emited (instead of *_PRESSED, *_RELEASED)
    #       Otherwise separate *_PRESSED and *_RELEASED are emitted
    if button_state & curses.BUTTON1_CLICKED:
        yield events.MouseButtonPress(event, mx, my, MouseButton.LEFT)
        yield events.MouseButtonUp(event, mx, my, MouseButton.LEFT)
    if button_state & curses.BUTTON1_PRESSED:
        yield events.MouseButtonPress(event, mx, my, MouseButton.LEFT)
    if button_state & curses.BUTTON1_RELEASED:
        yield events.MouseButtonUp(event, mx, my, MouseButton.LEFT)

    if button_state & curses.BUTTON2_CLICKED:
        yield events.MouseButtonPress(event, mx, my, MouseButton.MIDDLE)
        yield events.MouseButtonUp(event, mx, my, MouseButton.MIDDLE)
    if button_state & curses.BUTTON2_PRESSED:
        yield events.MouseButtonPress(event, mx, my, MouseButton.MIDDLE)
    if button_state & curses.BUTTON2_RELEASED:
        yield events.MouseButtonUp(event, mx, my, MouseButton.MIDDLE)

    if button_state & curses.BUTTON3_CLICKED:
        yield events.MouseButtonPress(event, mx, my, MouseButton.RIGHT)
        yield events.MouseButtonUp(event, mx, my, MouseButton.RIGHT)
    if button_state & curses.BUTTON3_PRESSED:
        yield events.MouseButtonPress(event, mx, my, MouseButton.RIGHT)
    if button_state & curses.BUTTON3_RELEASED:
        yield events.MouseButtonUp(event, mx, my, MouseButton.RIGHT)

    # TODO: BUTTON*_DOUBLE_CLICKED
    # TODO: MouseWheel events? WheelUp seems to be: BUTTON4_PRESSED and WheelDown: 0x200000


def parse_event(event, escaped=False):
    if event == curses.ERR:
        # No event returned
        return

    if event == curses.KEY_RESIZE:
        # TODO: yield Window resize event
        return

    if event == curses.KEY_MOUSE:
        yield from parse_mouse_event(event)
        return

    key = get_key(event, escaped=escaped)
    if key:
        yield events.KeyPress(event, key)
    if isinstance(event, str) and not curses.ascii.isctrl(event) and not escaped:
        yield events.TextInput(event, event)
    if key:
        yield events.KeyUp(event, key)


class CursesInputWrapper(InputWrapper):

    def __init__(self, screen):
        super().__init__()
        self.screen = screen

        # Catch ^c
        signal.signal(signal.SIGINT, self._signal_handler)
        # Catch ^z - doesn't seem to work properly...
        # signal.signal(signal.SIGTSTP, self._signal_handler)

    def _signal_handler(self, signal_no, frame):
        if signal_no == signal.SIGINT:
            curses.ungetch(3)
        elif signal_no == signal.SIGTSTP:
            curses.ungetch(26)

    def _get_event(self, window):
        try:
            # event = self.screen.getch()
            event = window.get_wch()
            # event = self.screen.getkey()
        except curses.error:
            # if nodelay(True) -> curses.error: no input is raised!
            return
        return event

    def _get_escape_sequence(self, window):
        self.screen.nodelay(True)
        sequence = []
        event = True
        while event:
            event = self._get_event(window)
            if event:
                sequence.append(event)
        return sequence

    def get_events_gen(self, wait=None):
        # TODO: Needs some more testing... halfdelay vs nodelay vs notimeout vs timeout
        if wait is False:
            self.screen.nodelay(True)
        elif wait is None or wait is True:
            # NOTE: wait==None will wait forever
            self.screen.nodelay(False)
        else:
            # Read: https://linux.die.net/man/3/nodelay
            # Not sure why all libraries use halfdelay, instead of timeout...
            self.screen.nodelay(False)
            timeout = min(int(wait*10), 255) or 1
            curses.halfdelay(timeout)
            # self.screen.nodelay(True)
            # timeout = int(wait*1000)
            # self.screen.timeout(timeout)

        escaped = False
        event = self._get_event(self.screen)
        if not event:
            return
        if event == chr(curses.ascii.ESC):
            sequence = self._get_escape_sequence(self.screen)
            if len(sequence) == 1:
                escaped = True
                event = sequence[-1]
            elif len(sequence) > 1:
                event = tuple(sequence)
                escaped = True
            # If not sequence -> It was just ESC key, no other codes followed

        yield from parse_event(event, escaped=escaped)

