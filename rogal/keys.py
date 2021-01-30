import string

import tcod.event

from .geometry import Direction


ASCII_CHARS = set()
for chars in [
    string.digits,
    string.ascii_lowercase,
    string.punctuation,
]:
    ASCII_CHARS.update(*chars)


class Modifier:
    SHIFT = 'Shift-'
    CTRL = 'Ctrl-'
    ALT = 'Alt-'
    CTRL_SHORT = '^'
    ALT_SHORT = '!'


class Key:
    ESCAPE = 'Escape'

    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    F4 = 'F4'
    F5 = 'F5'
    F6 = 'F6'
    F7 = 'F7'
    F8 = 'F8'
    F9 = 'F9'
    F10 = 'F10'
    F11 = 'F11'
    F12 = 'F12'

    BACKSPACE = 'Backspace'

    TAB = 'Tab'
    SHIFT_TAB = f'{Modifier.SHIFT}{TAB}'

    RETURN = 'Return'
    ENTER = RETURN

    SPACE = 'Space'

    UP = 'Up'
    DOWN = 'Down'
    LEFT = 'Left'
    RIGHT = 'Right'

    INSERT = 'Insert'
    DELETE = 'Delete'
    HOME = 'Home'
    END = 'End'
    PAGE_UP = 'PageUp'
    PAGE_DOWN = 'PageDown'

    KP_0 = 'KeyPad 0'
    KP_1 = 'KeyPad 1'
    KP_2 = 'KeyPad 2'
    KP_3 = 'KeyPad 3'
    KP_4 = 'KeyPad 4'
    KP_5 = 'KeyPad 5'
    KP_6 = 'KeyPad 6'
    KP_7 = 'KeyPad 7'
    KP_8 = 'KeyPad 8'
    KP_9 = 'KeyPad 9'

    KP_DIVIDE = 'KeyPad Divide'
    KP_MULTIPLY = 'KeyPad Multiply'
    KP_MINUS = 'KeyPad Minus'
    KP_PLUS = 'KeyPad Plus'
    KP_ENTER = 'KeyPad Enter'
    KP_PERIOD = 'KeyPad Period'
    KP_COMMA = 'KeyPad Comma'
    CLEAR = 'KeyPad Clear' # Keypad Clear key (on Mac?)

    UNKNOWN = 'Unknown'

    @classmethod
    def _with_shift(cls, key, with_modifiers):
        if key in string.ascii_lowercase:
            return key.upper()
        else:
            return f'{Modifier.SHIFT}{with_modifiers}'

    @classmethod
    def _with_alt(cls, key, with_modifiers):
        if key in ASCII_CHARS:
            modifier = Modifier.ALT_SHORT
        else:
            modifier = Modifier.ALT
        return f'{modifier}{with_modifiers}'

    @classmethod
    def _with_ctrl(cls, key, with_modifiers):
        if key in ASCII_CHARS:
            modifier = Modifier.CTRL_SHORT
        else:
            modifier = Modifier.CTRL
        return f'{modifier}{with_modifiers}'

    @classmethod
    def with_modifiers(cls, key, ctrl=False, alt=False, shift=False):
        with_modifiers = key
        if shift:
            with_modifiers = cls._with_shift(key, with_modifiers)
        if alt:
            with_modifiers = cls._with_alt(key, with_modifiers)
        if ctrl:
            with_modifiers = cls._with_ctrl(key, with_modifiers)
        return with_modifiers


# *_MOVE_KEYS = {key_symbol: (dx, dy), }
ARROW_MOVE_KEYS = {
    Key.LEFT: Direction.W,
    Key.RIGHT: Direction.E,
    Key.UP: Direction.N,
    Key.DOWN: Direction.S,
    Key.HOME: Direction.NW,
    Key.END: Direction.SW,
    Key.PAGE_UP: Direction.NE,
    Key.PAGE_DOWN: Direction.SE,
}
NUMPAD_MOVE_KEYS = {
    Key.KP_1: Direction.SW,
    Key.KP_2: Direction.S,
    Key.KP_3: Direction.SE,
    Key.KP_4: Direction.W,
    Key.KP_6: Direction.E,
    Key.KP_7: Direction.NW,
    Key.KP_8: Direction.N,
    Key.KP_9: Direction.NE,
}
VI_MOVE_KEYS = {
    'h': Direction.W,
    'j': Direction.S,
    'k': Direction.N,
    'l': Direction.E,
    'y': Direction.NW,
    'u': Direction.NE,
    'b': Direction.SW,
    'n': Direction.SE,
}

MOVE_KEYS = {}
MOVE_KEYS.update(ARROW_MOVE_KEYS)
MOVE_KEYS.update(NUMPAD_MOVE_KEYS)
MOVE_KEYS.update(VI_MOVE_KEYS)


WAIT_KEYS = {
    '.',
    Key.KP_5,
    Key.CLEAR,
}


CONFIRM_KEYS = {
    Key.RETURN,
    Key.KP_ENTER,
}


ESCAPE_KEY = Key.ESCAPE


# TODO: !!!
MODIFIER_SHIFT_KEYS = {
    tcod.event.K_LSHIFT,
    tcod.event.K_RSHIFT,
}
MODIFIER_CTRL_KEYS = {
    tcod.event.K_LCTRL,
    tcod.event.K_RCTRL,
}
MODIFIER_ALT_KEYS = {
    tcod.event.K_LALT,
    tcod.event.K_RALT,
}

MODIFIER_KEYS = MODIFIER_SHIFT_KEYS | MODIFIER_CTRL_KEYS | MODIFIER_ALT_KEYS

