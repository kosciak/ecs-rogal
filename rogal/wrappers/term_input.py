import functools
import logging

from ..term.escape_seq import ControlChar
from ..term.capabilities import Capability

from .. import events
from ..events.keys import Key, Keycode, Modifier

from .core import InputWrapper


log = logging.getLogger(__name__)


FOCUS_CHANGE = {
    Capability.focus_in,
    Capability.focus_out,
}


MOUSE_REPORT = Capability.mouse_report


SEQUENCE_KEYCODES = {
    ControlChar.BS:     (Keycode.BACKSPACE, Modifier.NONE),
    ControlChar.HT:     (Keycode.TAB, Modifier.NONE),
    ControlChar.CR:     (Keycode.ENTER, Modifier.NONE),
    ControlChar.LF:     (Keycode.ENTER, Modifier.NONE),
    ControlChar.ESC:    (Keycode.ESC, Modifier.NONE),
    ControlChar.SP:     (Keycode.SPACE, Modifier.NONE),
    # ControlChar.DEL:    (Keycode.DELETE, Modifier.NONE),
    ControlChar.DEL:    (Keycode.BACKSPACE, Modifier.NONE),
}


KEY_KEYCODES = {
    Capability.key_f1:      (Keycode.F1, Modifier.NONE),
    Capability.key_f2:      (Keycode.F2, Modifier.NONE),
    Capability.key_f3:      (Keycode.F3, Modifier.NONE),
    Capability.key_f4:      (Keycode.F4, Modifier.NONE),
    Capability.key_f5:      (Keycode.F5, Modifier.NONE),
    Capability.key_f6:      (Keycode.F6, Modifier.NONE),
    Capability.key_f7:      (Keycode.F7, Modifier.NONE),
    Capability.key_f8:      (Keycode.F8, Modifier.NONE),
    Capability.key_f9:      (Keycode.F9, Modifier.NONE),
    Capability.key_f10:     (Keycode.F10, Modifier.NONE),
    Capability.key_f11:     (Keycode.F11, Modifier.NONE),
    Capability.key_f12:     (Keycode.F12, Modifier.NONE),

    Capability.key_f13:     (Keycode.F1, Modifier.SHIFT),
    Capability.key_f14:     (Keycode.F2, Modifier.SHIFT),
    Capability.key_f15:     (Keycode.F3, Modifier.SHIFT),
    Capability.key_f16:     (Keycode.F4, Modifier.SHIFT),
    Capability.key_f17:     (Keycode.F5, Modifier.SHIFT),
    Capability.key_f18:     (Keycode.F6, Modifier.SHIFT),
    Capability.key_f19:     (Keycode.F7, Modifier.SHIFT),
    Capability.key_f20:     (Keycode.F8, Modifier.SHIFT),
    Capability.key_f21:     (Keycode.F9, Modifier.SHIFT),
    Capability.key_f22:     (Keycode.F10, Modifier.SHIFT),
    Capability.key_f23:     (Keycode.F11, Modifier.SHIFT),
    Capability.key_f24:     (Keycode.F12, Modifier.SHIFT),

    Capability.key_f25:     (Keycode.F1, Modifier.CTRL),
    Capability.key_f26:     (Keycode.F2, Modifier.CTRL),
    Capability.key_f27:     (Keycode.F3, Modifier.CTRL),
    Capability.key_f28:     (Keycode.F4, Modifier.CTRL),
    Capability.key_f29:     (Keycode.F5, Modifier.CTRL),
    Capability.key_f30:     (Keycode.F6, Modifier.CTRL),
    Capability.key_f31:     (Keycode.F7, Modifier.CTRL),
    Capability.key_f32:     (Keycode.F8, Modifier.CTRL),
    Capability.key_f33:     (Keycode.F9, Modifier.CTRL),
    Capability.key_f34:     (Keycode.F10, Modifier.CTRL),
    Capability.key_f35:     (Keycode.F11, Modifier.CTRL),
    Capability.key_f36:     (Keycode.F12, Modifier.CTRL),

    Capability.key_f37:     (Keycode.F1, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f38:     (Keycode.F2, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f39:     (Keycode.F3, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f40:     (Keycode.F4, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f41:     (Keycode.F5, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f42:     (Keycode.F6, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f43:     (Keycode.F7, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f44:     (Keycode.F8, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f45:     (Keycode.F9, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f46:     (Keycode.F10, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f47:     (Keycode.F11, Modifier.CTRL | Modifier.SHIFT),
    Capability.key_f48:     (Keycode.F12, Modifier.CTRL | Modifier.SHIFT),

    Capability.key_btab:    (Keycode.TAB, Modifier.SHIFT),

    Capability.key_backspace:   (Keycode.BACKSPACE, Modifier.NONE),

    Capability.key_enter:   (Keycode.RETURN, Modifier.NONE),

    Capability.key_up:      (Keycode.UP, Modifier.NONE),
    Capability.key_down:    (Keycode.DOWN, Modifier.NONE),
    Capability.key_left:    (Keycode.LEFT, Modifier.NONE),
    Capability.key_right:   (Keycode.RIGHT, Modifier.NONE),

    Capability.key_ic:      (Keycode.INSERT, Modifier.NONE),
    Capability.key_dc:      (Keycode.DELETE, Modifier.NONE),
    Capability.key_home:    (Keycode.HOME, Modifier.NONE),
    Capability.key_end:     (Keycode.END, Modifier.NONE),
    Capability.key_ppage:   (Keycode.PAGE_UP, Modifier.NONE),
    Capability.key_npage:   (Keycode.PAGE_DOWN, Modifier.NONE),

    Capability.kUP:         (Keycode.UP, Modifier.SHIFT),
    Capability.kDN:         (Keycode.DOWN, Modifier.SHIFT),
    Capability.kLFT:        (Keycode.LEFT, Modifier.SHIFT),
    Capability.kRIT:        (Keycode.RIGHT, Modifier.SHIFT),

    Capability.kIC:         (Keycode.INSERT, Modifier.SHIFT),
    Capability.kDC:         (Keycode.DELETE, Modifier.SHIFT),
    Capability.kHOM:        (Keycode.HOME, Modifier.SHIFT),
    Capability.kEND:        (Keycode.END, Modifier.SHIFT),
    Capability.kPRV:        (Keycode.PAGE_UP, Modifier.SHIFT),
    Capability.kNXT:        (Keycode.PAGE_DOWN, Modifier.SHIFT),

    Capability.kUP3:        (Keycode.UP, Modifier.ALT),
    Capability.kDN3:        (Keycode.DOWN, Modifier.ALT),
    Capability.kLFT3:       (Keycode.LEFT, Modifier.ALT),
    Capability.kRIT3:       (Keycode.RIGHT, Modifier.ALT),

    Capability.kIC3:        (Keycode.INSERT, Modifier.ALT),
    Capability.kDC3:        (Keycode.DELETE, Modifier.ALT),
    Capability.kHOM3:       (Keycode.HOME, Modifier.ALT),
    Capability.kEND3:       (Keycode.END, Modifier.ALT),
    Capability.kPRV3:       (Keycode.PAGE_UP, Modifier.ALT),
    Capability.kNXT3:       (Keycode.PAGE_DOWN, Modifier.ALT),

    Capability.kUP4:        (Keycode.UP, Modifier.ALT | Modifier.SHIFT),
    Capability.kDN4:        (Keycode.DOWN, Modifier.ALT | Modifier.SHIFT),
    Capability.kLFT4:       (Keycode.LEFT, Modifier.ALT | Modifier.SHIFT),
    Capability.kRIT4:       (Keycode.RIGHT, Modifier.ALT | Modifier.SHIFT),

    Capability.kIC4:        (Keycode.INSERT, Modifier.ALT | Modifier.SHIFT),
    Capability.kDC4:        (Keycode.DELETE, Modifier.ALT | Modifier.SHIFT),
    Capability.kHOM4:       (Keycode.HOME, Modifier.ALT | Modifier.SHIFT),
    Capability.kEND4:       (Keycode.END, Modifier.ALT | Modifier.SHIFT),
    Capability.kPRV4:       (Keycode.PAGE_UP, Modifier.ALT | Modifier.SHIFT),
    Capability.kNXT4:       (Keycode.PAGE_DOWN, Modifier.ALT | Modifier.SHIFT),

    Capability.kUP5:        (Keycode.UP, Modifier.CTRL),
    Capability.kDN5:        (Keycode.DOWN, Modifier.CTRL),
    Capability.kLFT5:       (Keycode.LEFT, Modifier.CTRL),
    Capability.kRIT5:       (Keycode.RIGHT, Modifier.CTRL),

    Capability.kIC5:        (Keycode.INSERT, Modifier.CTRL),
    Capability.kDC5:        (Keycode.DELETE, Modifier.CTRL),
    Capability.kHOM5:       (Keycode.HOME, Modifier.CTRL),
    Capability.kEND5:       (Keycode.END, Modifier.CTRL),
    Capability.kPRV5:       (Keycode.PAGE_UP, Modifier.CTRL),
    Capability.kNXT5:       (Keycode.PAGE_DOWN, Modifier.CTRL),

    Capability.kUP6:        (Keycode.UP, Modifier.CTRL | Modifier.SHIFT),
    Capability.kDN6:        (Keycode.DOWN, Modifier.CTRL | Modifier.SHIFT),
    Capability.kLFT6:       (Keycode.LEFT, Modifier.CTRL | Modifier.SHIFT),
    Capability.kRIT6:       (Keycode.RIGHT, Modifier.CTRL | Modifier.SHIFT),

    Capability.kIC6:        (Keycode.INSERT, Modifier.CTRL | Modifier.SHIFT),
    Capability.kDC6:        (Keycode.DELETE, Modifier.CTRL | Modifier.SHIFT),
    Capability.kHOM6:       (Keycode.HOME, Modifier.CTRL | Modifier.SHIFT),
    Capability.kEND6:       (Keycode.END, Modifier.CTRL | Modifier.SHIFT),
    Capability.kPRV6:       (Keycode.PAGE_UP, Modifier.CTRL | Modifier.SHIFT),
    Capability.kNXT6:       (Keycode.PAGE_DOWN, Modifier.CTRL | Modifier.SHIFT),

    Capability.kUP7:        (Keycode.UP, Modifier.CTRL | Modifier.ALT),
    Capability.kDN7:        (Keycode.DOWN, Modifier.CTRL | Modifier.ALT),
    Capability.kLFT7:       (Keycode.LEFT, Modifier.CTRL | Modifier.ALT),
    Capability.kRIT7:       (Keycode.RIGHT, Modifier.CTRL | Modifier.ALT),

    Capability.kIC7:        (Keycode.INSERT, Modifier.CTRL | Modifier.ALT),
    Capability.kDC7:        (Keycode.DELETE, Modifier.CTRL | Modifier.ALT),
    Capability.kHOM7:       (Keycode.HOME, Modifier.CTRL | Modifier.ALT),
    Capability.kEND7:       (Keycode.END, Modifier.CTRL | Modifier.ALT),
    Capability.kPRV7:       (Keycode.PAGE_UP, Modifier.CTRL | Modifier.ALT),
    Capability.kNXT7:       (Keycode.PAGE_DOWN, Modifier.CTRL | Modifier.ALT),

    Capability.kUP8:        (Keycode.UP, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kDN8:        (Keycode.DOWN, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kLFT8:       (Keycode.LEFT, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kRIT8:       (Keycode.RIGHT, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),

    Capability.kIC8:        (Keycode.INSERT, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kDC8:        (Keycode.DELETE, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kHOM8:       (Keycode.HOME, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kEND8:       (Keycode.END, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kPRV8:       (Keycode.PAGE_UP, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kNXT8:       (Keycode.PAGE_DOWN, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),

    Capability.kp0:         (Keycode.KP_0, Modifier.NONE),
    Capability.kp1:         (Keycode.KP_1, Modifier.NONE),
    Capability.kp2:         (Keycode.KP_2, Modifier.NONE),
    Capability.kp3:         (Keycode.KP_3, Modifier.NONE),
    Capability.kp4:         (Keycode.KP_4, Modifier.NONE),
    Capability.kp5:         (Keycode.KP_5, Modifier.NONE),
    Capability.kp6:         (Keycode.KP_6, Modifier.NONE),
    Capability.kp7:         (Keycode.KP_7, Modifier.NONE),
    Capability.kp8:         (Keycode.KP_8, Modifier.NONE),
    Capability.kp9:         (Keycode.KP_9, Modifier.NONE),

    Capability.ka1:         (Keycode.KP_1, Modifier.NONE),
    Capability.ka2:         (Keycode.KP_2, Modifier.NONE),
    Capability.ka3:         (Keycode.KP_3, Modifier.NONE),
    Capability.kb1:         (Keycode.KP_4, Modifier.NONE),
    Capability.kb2:         (Keycode.KP_5, Modifier.NONE),
    Capability.kb3:         (Keycode.KP_6, Modifier.NONE),
    Capability.kc1:         (Keycode.KP_7, Modifier.NONE),
    Capability.kc2:         (Keycode.KP_8, Modifier.NONE),
    Capability.kc3:         (Keycode.KP_9, Modifier.NONE),

    Capability.kpDIV:       (Keycode.KP_DIVIDE, Modifier.NONE),
    Capability.kpMUL:       (Keycode.KP_MULTIPLY, Modifier.NONE),
    Capability.kpSUB:       (Keycode.KP_MINUS, Modifier.NONE),
    Capability.kpADD:       (Keycode.KP_PLUS, Modifier.NONE),
    Capability.kpDOT:       (Keycode.KP_PERIOD, Modifier.NONE),
    Capability.kpZRO:       (Keycode.KP_0, Modifier.NONE),
    Capability.kpCMA:       (Keycode.KP_COMMA, Modifier.NONE),
    Capability.kpENT:       (Keycode.KP_ENTER, Modifier.NONE),

    Capability.kpDIV2:      (Keycode.KP_DIVIDE, Modifier.SHIFT),
    Capability.kpMUL2:      (Keycode.KP_MULTIPLY, Modifier.SHIFT),
    Capability.kpSUB2:      (Keycode.KP_MINUS, Modifier.SHIFT),
    Capability.kpADD2:      (Keycode.KP_PLUS, Modifier.SHIFT),
    Capability.kpDOT2:      (Keycode.KP_PERIOD, Modifier.SHIFT),
    Capability.kpZRO2:      (Keycode.KP_0, Modifier.SHIFT),
    Capability.kpCMA2:      (Keycode.KP_COMMA, Modifier.SHIFT),
    Capability.kpENT2:      (Keycode.KP_ENTER, Modifier.SHIFT),

    Capability.kpDIV3:      (Keycode.KP_DIVIDE, Modifier.ALT),
    Capability.kpMUL3:      (Keycode.KP_MULTIPLY, Modifier.ALT),
    Capability.kpSUB3:      (Keycode.KP_MINUS, Modifier.ALT),
    Capability.kpADD3:      (Keycode.KP_PLUS, Modifier.ALT),
    Capability.kpDOT3:      (Keycode.KP_PERIOD, Modifier.ALT),
    Capability.kpZRO3:      (Keycode.KP_0, Modifier.ALT),
    Capability.kpCMA3:      (Keycode.KP_COMMA, Modifier.ALT),
    Capability.kpENT3:      (Keycode.KP_ENTER, Modifier.ALT),

    Capability.kpDIV4:      (Keycode.KP_DIVIDE, Modifier.ALT | Modifier.SHIFT),
    Capability.kpMUL4:      (Keycode.KP_MULTIPLY, Modifier.ALT | Modifier.SHIFT),
    Capability.kpSUB4:      (Keycode.KP_MINUS, Modifier.ALT | Modifier.SHIFT),
    Capability.kpADD4:      (Keycode.KP_PLUS, Modifier.ALT | Modifier.SHIFT),
    Capability.kpDOT4:      (Keycode.KP_PERIOD, Modifier.ALT | Modifier.SHIFT),
    Capability.kpZRO4:      (Keycode.KP_0, Modifier.ALT | Modifier.SHIFT),
    Capability.kpCMA4:      (Keycode.KP_COMMA, Modifier.ALT | Modifier.SHIFT),
    Capability.kpENT4:      (Keycode.KP_ENTER, Modifier.ALT | Modifier.SHIFT),

    Capability.kpDIV5:      (Keycode.KP_DIVIDE, Modifier.CTRL),
    Capability.kpMUL5:      (Keycode.KP_MULTIPLY, Modifier.CTRL),
    Capability.kpSUB5:      (Keycode.KP_MINUS, Modifier.CTRL),
    Capability.kpADD5:      (Keycode.KP_PLUS, Modifier.CTRL),
    Capability.kpDOT5:      (Keycode.KP_PERIOD, Modifier.CTRL),
    Capability.kpZRO5:      (Keycode.KP_0, Modifier.CTRL),
    Capability.kpCMA5:      (Keycode.KP_COMMA, Modifier.CTRL),
    Capability.kpENT5:      (Keycode.KP_ENTER, Modifier.CTRL),

    Capability.kpDIV6:      (Keycode.KP_DIVIDE, Modifier.CTRL | Modifier.SHIFT),
    Capability.kpMUL6:      (Keycode.KP_MULTIPLY, Modifier.CTRL | Modifier.SHIFT),
    Capability.kpSUB6:      (Keycode.KP_MINUS, Modifier.CTRL | Modifier.SHIFT),
    Capability.kpADD6:      (Keycode.KP_PLUS, Modifier.CTRL | Modifier.SHIFT),
    Capability.kpDOT6:      (Keycode.KP_PERIOD, Modifier.CTRL | Modifier.SHIFT),
    Capability.kpZRO6:      (Keycode.KP_0, Modifier.CTRL | Modifier.SHIFT),
    Capability.kpCMA6:      (Keycode.KP_COMMA, Modifier.CTRL | Modifier.SHIFT),
    Capability.kpENT6:      (Keycode.KP_ENTER, Modifier.CTRL | Modifier.SHIFT),

    Capability.kpDIV7:      (Keycode.KP_DIVIDE, Modifier.CTRL | Modifier.ALT),
    Capability.kpMUL7:      (Keycode.KP_MULTIPLY, Modifier.CTRL | Modifier.ALT),
    Capability.kpSUB7:      (Keycode.KP_MINUS, Modifier.CTRL | Modifier.ALT),
    Capability.kpADD7:      (Keycode.KP_PLUS, Modifier.CTRL | Modifier.ALT),
    Capability.kpDOT7:      (Keycode.KP_PERIOD, Modifier.CTRL | Modifier.ALT),
    Capability.kpZRO7:      (Keycode.KP_0, Modifier.CTRL | Modifier.ALT),
    Capability.kpCMA7:      (Keycode.KP_COMMA, Modifier.CTRL | Modifier.ALT),
    Capability.kpENT7:      (Keycode.KP_ENTER, Modifier.CTRL | Modifier.ALT),

    Capability.kpDIV8:      (Keycode.KP_DIVIDE, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kpMUL8:      (Keycode.KP_MULTIPLY, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kpSUB8:      (Keycode.KP_MINUS, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kpADD8:      (Keycode.KP_PLUS, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kpDOT8:      (Keycode.KP_PERIOD, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kpZRO8:      (Keycode.KP_0, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kpCMA8:      (Keycode.KP_COMMA, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),
    Capability.kpENT8:      (Keycode.KP_ENTER, Modifier.CTRL | Modifier.ALT | Modifier.SHIFT),

}


'''
NOTE: Mappings from curses.has_key

    _curses.KEY_SR: 'kri',
    _curses.KEY_SF: 'kind',

    _curses.KEY_F0: 'kf0',

    _curses.KEY_F49: 'kf49',
    _curses.KEY_F50: 'kf50',
    _curses.KEY_F51: 'kf51',
    _curses.KEY_F52: 'kf52',
    _curses.KEY_F53: 'kf53',
    _curses.KEY_F54: 'kf54',
    _curses.KEY_F55: 'kf55',
    _curses.KEY_F56: 'kf56',
    _curses.KEY_F57: 'kf57',
    _curses.KEY_F58: 'kf58',
    _curses.KEY_F59: 'kf59',
    _curses.KEY_F60: 'kf60',
    _curses.KEY_F61: 'kf61',
    _curses.KEY_F62: 'kf62',
    _curses.KEY_F63: 'kf63',

    _curses.KEY_BEG: 'kbeg',
    _curses.KEY_CANCEL: 'kcan',
    _curses.KEY_CATAB: 'ktbc',
    _curses.KEY_CLEAR: 'kclr',
    _curses.KEY_CLOSE: 'kclo',
    _curses.KEY_COMMAND: 'kcmd',
    _curses.KEY_COPY: 'kcpy',
    _curses.KEY_CREATE: 'kcrt',
    _curses.KEY_CTAB: 'kctab',
    _curses.KEY_DL: 'kdl1',
    _curses.KEY_EIC: 'krmir',
    _curses.KEY_EOL: 'kel',
    _curses.KEY_EOS: 'ked',
    _curses.KEY_EXIT: 'kext',
    _curses.KEY_FIND: 'kfnd',
    _curses.KEY_HELP: 'khlp',
    _curses.KEY_IL: 'kil1',
    _curses.KEY_LL: 'kll',
    _curses.KEY_MARK: 'kmrk',
    _curses.KEY_MESSAGE: 'kmsg',
    _curses.KEY_MOVE: 'kmov',
    _curses.KEY_OPEN: 'kopn',
    _curses.KEY_OPTIONS: 'kopt',
    _curses.KEY_PRINT: 'kprt',
    _curses.KEY_REDO: 'krdo',
    _curses.KEY_REFERENCE: 'kref',
    _curses.KEY_REFRESH: 'krfr',
    _curses.KEY_REPLACE: 'krpl',
    _curses.KEY_RESTART: 'krst',
    _curses.KEY_RESUME: 'kres',
    _curses.KEY_SAVE: 'ksav',
    _curses.KEY_SBEG: 'kBEG',
    _curses.KEY_SCANCEL: 'kCAN',
    _curses.KEY_SCOMMAND: 'kCMD',
    _curses.KEY_SCOPY: 'kCPY',
    _curses.KEY_SCREATE: 'kCRT',
    _curses.KEY_SDL: 'kDL',
    _curses.KEY_SELECT: 'kslt',
    _curses.KEY_SEOL: 'kEOL',
    _curses.KEY_SEXIT: 'kEXT',
    _curses.KEY_SFIND: 'kFND',
    _curses.KEY_SHELP: 'kHLP',
    _curses.KEY_SMESSAGE: 'kMSG',
    _curses.KEY_SMOVE: 'kMOV',
    _curses.KEY_SOPTIONS: 'kOPT',
    _curses.KEY_SPRINT: 'kPRT',
    _curses.KEY_SREDO: 'kRDO',
    _curses.KEY_SREPLACE: 'kRPL',
    _curses.KEY_SRSUME: 'kRES',
    _curses.KEY_SSAVE: 'kSAV',
    _curses.KEY_SSUSPEND: 'kSPD',
    _curses.KEY_STAB: 'khts',
    _curses.KEY_SUNDO: 'kUND',
    _curses.KEY_SUSPEND: 'kspd',
    _curses.KEY_UNDO: 'kund',

'''

def get_key(sequence):
    keycode, modifiers = SEQUENCE_KEYCODES.get(sequence, (None, None))
    if keycode:
        return Key(keycode, modifiers, alt=sequence.is_escaped)

    keycode, modifiers = KEY_KEYCODES.get(sequence.key, (None, None))
    if keycode:
        return Key(keycode, modifiers, alt=sequence.is_escaped)

    if len(sequence) > 1:
        # TODO: Some unrecognized sequence
        return

    keycode = ord(sequence)

    # Keys with CTRL
    if keycode < 32:
        keycode = ord(chr(keycode+64).lower())
        return Key(keycode, ctrl=True, alt=sequence.is_escaped)

    if keycode < 127:
        return Key(keycode, alt=sequence.is_escaped)


def parse_sequence(sequence):
    if sequence.key in FOCUS_CHANGE:
        # TODO: yield Focus In/Out events
        return

    if sequence.key == MOUSE_REPORT:
        # TODO: get_mouse(sequence)
        return

    key = get_key(sequence)
    if key:
        yield events.KeyPress(sequence, key)
    if len(sequence) == 1 and ord(sequence) >= 127:
        yield events.TextInput(sequence, sequence)
    if key:
        yield events.KeyUp(sequence, key)


class TermInputWrapper(InputWrapper):

    def __init__(self, term):
        super().__init__()
        self.term = term

    def get_events_gen(self, timeout=None):
        """Get all pending events."""
        for sequence in self.term.get_sequences(timeout):
            log.debug('INPUT: %s - %r %s',
                      sequence.key or '???',
                      sequence,
                      sequence.is_escaped and '(escaped)' or '',
                     )
            yield from parse_sequence(sequence)

