import collections
import string
import time


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
    GUI = 'Super-'
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
    KP_CLEAR = 'KeyPad Clear' # Keypad Clear key (on Mac?)

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
    def _with_gui(cls, key, with_modifiers):
        return f'{Modifier.GUI}{with_modifiers}'

    @classmethod
    def with_modifiers(cls, key, ctrl=False, alt=False, shift=False, gui=False):
        with_modifiers = key
        if shift:
            with_modifiers = cls._with_shift(key, with_modifiers)
        if alt:
            with_modifiers = cls._with_alt(key, with_modifiers)
        if ctrl:
            with_modifiers = cls._with_ctrl(key, with_modifiers)
        if gui:
            with_modifiers = cls._with_gui(key, with_modifiers)
        return with_modifiers

    @staticmethod
    def parse(key):
        modifiers, sep, key = key.rpartition('-')
        key = getattr(Key, key, key)
        if modifiers:
            key = f'{modifiers}-{key}'
        return key


class KeyboardState:

    def __init__(self, max_repeat_rate=None):
        self.max_repeat_rate = max_repeat_rate
        self._last_valid_press = {}
        self.pressed_keys = set()

    def is_valid_press(self, key):
        if not self.max_repeat_rate:
            return True
        now = time.time()
        prev_time = self._last_valid_press.get(key)
        if prev_time and now - prev_time < self.max_repeat_rate:
            return False
        self._last_valid_press[key] = now
        return True

    def update(self, press_event=None, up_event=None):
        if press_event:
            self.pressed_keys.add(press_event.key)
        if up_event:
            self.pressed_keys.discard(up_event.key)
            self._last_valid_press.pop(up_event.key, None)


class Bindings(collections.defaultdict):

    def __init__(self):
        super().__init__(set)

    def __getattr__(self, name):
        return self[name]

    @staticmethod
    def parse(data):
        bindings = Bindings()
        for name, keys in data.items():
            bindings[name].update(map(Key.parse, keys))
        return bindings


class KeyBindings:

    def __init__(self, loader):
        self.loader = loader
        self._bindings = None

    @property
    def bindings(self):
        if self._bindings is None:
            data = self.loader.load()
            self._bindings = self.parse_bindings(data)
        return self._bindings

    def parse_bindings(self, data):
        bindings = collections.defaultdict(Bindings)
        for category, bindings_data in data.items():
            bindings[category] = Bindings.parse(bindings_data)
        return bindings

    def get(self, key_binding):
        if not isinstance(key_binding, str):
            return key_binding
        category, sep, name = key_binding.partition('.')
        bindings = self.bindings[category]
        return bindings[name]

    def __getattr__(self, name):
        return self.bindings[name]

