import collections
import enum
import string


ASCII_CHARS = set()
for chars in [
    string.digits,
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.punctuation,
]:
    ASCII_CHARS.update(*chars)


class Modifier(enum.IntFlag):
    NONE = 0
    SHIFT = 1
    CTRL = 2
    ALT = 4
    GUI = 8

    @classmethod
    def get(cls, name):
        return cls.__members__.get(name.upper())


# Max Unicode codepoint: 0x10ffff
# TODO: Maybe set keycodes of function keys to values above max unicode codepoint?
#       This way we can easily map all single character keys, no matter what layout is used

class Keycode(enum.IntEnum):
    UNKNOWN = 0

    BACKSPACE = ord('\b')
    TAB = ord('\t')
    RETURN = ord('\n')
    ENTER = RETURN
    ESCAPE = 27
    ESC = ESCAPE
    SPACE = ord(' ')

    # NOTE: For all printable ASCII characters use ord(char)
    EXCLAM = ord('!')
    QUOTEDBL = ord('"')
    HASH = ord('#')
    PERCENT = ord('%')
    DOLLAR = ord('$')
    AMPERSAND = ord('&')
    QUOTE = ord('\'')
    LEFTPAREN = ord('(')
    RIGHTPAREN = ord(')')
    ASTERISK = ord('*')
    PLUS = ord('+')
    COMMA = ord(',')
    MINUS = ord('-')
    PERIOD = ord('.')
    SLASH = ord('/')

    # 0 = 48
    # ...
    # 9 = 57

    COLON = ord(':')
    SEMICOLON = ord(';')
    LESS = ord('<')
    EQUALS = ord('=')
    GREATER = ord('>')
    QUESTION = ord('?')
    AT = ord('@')

    # A = 41
    # ...
    # Z = 90

    LEFTBRACKET = ord('[')
    BACKSLASH = ord('\\')
    RIGHTBRACKET = ord(']')
    CARET = ord('^')
    UNDERSCORE = ord('_')
    BACKQUOTE = ord('`')

    # a = 97
    # ...
    # z = 122

    LEFTBRACE = ord('{')
    PIPE = ord('|')
    RIGHTBRACE = ord('}')
    TILDE = ord('~')

    # As returned by xev
    F1 = 0xffbe
    F2 = 0xffbf
    F3 = 0xffc0
    F4 = 0xffc1
    F5 = 0xffc2
    F6 = 0xffc3
    F7 = 0xffc4
    F8 = 0xffc5
    F9 = 0xffc6
    F10 = 0xffc7
    F11 = 0xffc8
    F12 = 0xffc9

    # As returned by xev
    LEFT = 0xff51
    UP = 0xff52
    RIGHT = 0xff53
    DOWN = 0xff54

    INSERT = 0xff63
    DELETE = 127
    HOME = 0xff50
    END = 0xff57
    PAGE_UP = 0xff55
    PAGE_DOWN = 0xff56

    # For KP_* use 0xff00 + matching keycode from normal keyboard
    KP_0 = 0xff30
    KP_1 = 0xff31
    KP_2 = 0xff32
    KP_3 = 0xff33
    KP_4 = 0xff34
    KP_5 = 0xff35
    KP_6 = 0xff36
    KP_7 = 0xff37
    KP_8 = 0xff38
    KP_9 = 0xff39

    KP_DIVIDE = 0xff2f
    KP_MULTIPLY = 0xff2a
    KP_MINUS = 0xff2d
    KP_PLUS = 0xff2b
    KP_ENTER = 0xff0a
    KP_PERIOD = 0xff2e
    KP_COMMA = 0xff2c
    KP_CLEAR = 0xff20 # Keypad Clear key (on Mac?)

    # As returned by xev
    SHIFT_LEFT = 0xffe1
    SHIFT_RIGHT = 0xffe2
    CTRL_LEFT = 0xffe3
    CTRL_RIGHT = 0xffe4
    ALT_LEFT = 0xffe9
    ALT_RIGHT = 0xfe03 # ISO_Level3_Shift
    GUI_LEFT = 0xffeb
    GUI_RIGHT = 0xffec # Arbitrary value as I don't have right GUI

    MENU = 0xff67

    @classmethod
    def get(cls, name):
        return cls.__members__.get(name.upper())


class Key(collections.namedtuple(
    'Key', [
        'keycode',
        'modifiers',
    ])):

    __slots__ = ()

    def __new__(cls, keycode, modifiers=None, ctrl=False, alt=False, shift=False, gui=False):
        modifiers = modifiers or Modifier.NONE
        if ctrl:
            modifiers |= Modifier.CTRL
        if alt:
            modifiers |= Modifier.ALT
        if shift:
            modifiers |= Modifier.SHIFT
        if gui:
            modifiers |= Modifier.GUI
        return super().__new__(cls, keycode, modifiers)

    @property
    def is_keypad(self):
        return self.keycode.name.startswith('KP_')

    @property
    def is_modifier(self):
        if self.keycode.name.startswith('SHIFT_'):
            return True
        if self.keycode.name.startswith('CTRL_'):
            return True
        if self.keycode.name.startswith('ALT_'):
            return True
        if self.keycode.name.startswith('GUI_'):
            return True
        return False

    def replace(self, keycode):
        if keycode in ASCII_CHARS:
            keycode = ord(keycode)
        if isinstance(keycode, int) and 32 < keycode < 127:
            modifiers = self.modifiers
            if modifiers & Modifier.SHIFT:
                modifiers = self.modifiers ^ Modifier.SHIFT
            return Key(keycode, modifiers=modifiers)
        return self

    @staticmethod
    def parse(key):
        if isinstance(key, Key):
            return key

        modifiers = Modifier.NONE
        key = key.split('-')

        keycode = key[-1]
        if keycode.startswith('^'):
            keycode = keycode.strip('^')
            modifiers |= Modifier.CTRL
        if keycode in ASCII_CHARS:
            keycode = ord(keycode)
        else:
            keycode = Keycode.get(keycode) or Keycode.UNKNOWN

        for mod in key[0:-1]:
            modifier = Modifier.get(mod)
            if modifier:
                modifiers |= modifier

        return Key(keycode, modifiers=modifiers)

    def __str__(self):
        if 32 < self.keycode < 127:
            key = chr(self.keycode)
        elif isinstance(self.keycode, Keycode):
            key = self.keycode.name
        else:
            key = str(self.keycode)

        if (self.modifiers == Modifier.CTRL) and 32 < self.keycode < 127:
            key = f'^{key}'
        else:
            if self.modifiers & Modifier.SHIFT:
                key = f'Shift-{key}'
            if self.modifiers & Modifier.ALT:
                key = f'Alt-{key}'
            if self.modifiers & Modifier.CTRL:
                key = f'Ctrl-{key}'
            if self.modifiers & Modifier.GUI:
                key = f'Super-{key}'

        return key


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

