import re
import logging

from .capabilities import STR_CAPABILITIES, Capability


log = logging.getLogger(__name__)


"""Input sequences parsing. Parse keys, mouse events, focus in/out events, cursor report, etc

See: https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-PC-Style-Function-Keys
See: https://fossies.org/linux/rxvt/doc/rxvtRef.html#KeyCodes

"""


# Unfortunately not all key related capabilities that are supported by terminals are available in terminfo,
# that's why here is a list of default values for each capability.
DEFAULT_KEY_SEQUENCES = {
    # PC-style Normal mode
    b'\x08':   Capability.key_backspace,

    b'\x1b[A': Capability.key_up,
    b'\x1b[B': Capability.key_down,
    b'\x1b[C': Capability.key_right,
    b'\x1b[D': Capability.key_left,

    b'\x1b[H': Capability.key_home,
    b'\x1b[F': Capability.key_end,

    b'\x1b[E': Capability.key_b2,

    # PC-style Application mode
    b'\x1bOA': Capability.key_up,
    b'\x1bOB': Capability.key_down,
    b'\x1bOC': Capability.key_right,
    b'\x1bOD': Capability.key_left,

    b'\x1bOH': Capability.key_home,
    b'\x1bOF': Capability.key_end,

    # VT220-style PF1 - PF4 keys above keypad
    b'\x1bOP': Capability.key_f1,
    b'\x1bOQ': Capability.key_f2,
    b'\x1bOR': Capability.key_f3,
    b'\x1bOS': Capability.key_f4,

    # VT220-style Normal mode keypad keys
    b'\x1b[3~': Capability.key_dc,
    b'\x1b[2~': Capability.key_ic,

    b'\x1b[1~': Capability.key_home,    # ? key_find in xterm
    b'\x1b[4~': Capability.key_end,     # ? key_select in xterm

    b'\x1b[6~': Capability.key_npage,
    b'\x1b[5~': Capability.key_ppage,

    # VT220-style Application mode keypad keys
    b'\x1bOp': Capability.kp0,
    b'\x1bOq': Capability.kp1,
    b'\x1bOr': Capability.kp2,
    b'\x1bOs': Capability.kp3,
    b'\x1bOt': Capability.kp4,
    b'\x1bOu': Capability.kp5,
    b'\x1bOv': Capability.kp6,
    b'\x1bOw': Capability.kp7,
    b'\x1bOx': Capability.kp8,
    b'\x1bOy': Capability.kp9,

    b'\x1bOo': Capability.kpDIV,
    b'\x1bOj': Capability.kpMUL,
    b'\x1bOm': Capability.kpSUB,
    b'\x1bOk': Capability.kpADD,
    b'\x1bOl': Capability.kpCMA,
    b'\x1bOn': Capability.kpDOT,
    b'\x1bOM': Capability.kpENT,

    b'\x1bO2o': Capability.kpDIV2,
    b'\x1bO2j': Capability.kpMUL2,
    b'\x1bO2m': Capability.kpSUB2,
    b'\x1bO2k': Capability.kpADD2,
    b'\x1bO2l': Capability.kpCMA2,
    b'\x1bO2n': Capability.kpDOT2,
    b'\x1bO2M': Capability.kpENT2,

    b'\x1bO3o': Capability.kpDIV3,
    b'\x1bO3j': Capability.kpMUL3,
    b'\x1bO3m': Capability.kpSUB3,
    b'\x1bO3k': Capability.kpADD3,
    b'\x1bO3l': Capability.kpCMA3,
    b'\x1bO3n': Capability.kpDOT3,
    b'\x1bO3M': Capability.kpENT3,

    b'\x1bO4o': Capability.kpDIV4,
    b'\x1bO4j': Capability.kpMUL4,
    b'\x1bO4m': Capability.kpSUB4,
    b'\x1bO4k': Capability.kpADD4,
    b'\x1bO4l': Capability.kpCMA4,
    b'\x1bO4n': Capability.kpDOT4,
    b'\x1bO4M': Capability.kpENT4,

    b'\x1bO5o': Capability.kpDIV5,
    b'\x1bO5j': Capability.kpMUL5,
    b'\x1bO5m': Capability.kpSUB5,
    b'\x1bO5k': Capability.kpADD5,
    b'\x1bO5l': Capability.kpCMA5,
    b'\x1bO5n': Capability.kpDOT5,
    b'\x1bO5M': Capability.kpENT5,

    b'\x1bO6o': Capability.kpDIV6,
    b'\x1bO6j': Capability.kpMUL6,
    b'\x1bO6m': Capability.kpSUB6,
    b'\x1bO6k': Capability.kpADD6,
    b'\x1bO6l': Capability.kpCMA6,
    b'\x1bO6n': Capability.kpDOT6,
    b'\x1bO6M': Capability.kpENT6,

    b'\x1bO7o': Capability.kpDIV7,
    b'\x1bO7j': Capability.kpMUL7,
    b'\x1bO7m': Capability.kpSUB7,
    b'\x1bO7k': Capability.kpADD7,
    b'\x1bO7l': Capability.kpCMA7,
    b'\x1bO7n': Capability.kpDOT7,
    b'\x1bO7M': Capability.kpENT7,

    b'\x1bO8o': Capability.kpDIV8,
    b'\x1bO8j': Capability.kpMUL8,
    b'\x1bO8m': Capability.kpSUB8,
    b'\x1bO8k': Capability.kpADD8,
    b'\x1bO8l': Capability.kpCMA8,
    b'\x1bO8n': Capability.kpDOT8,
    b'\x1bO8M': Capability.kpENT8,

    # xterm
    b'\x1b[1;2A': Capability.kUP,
    b'\x1b[1;2B': Capability.kDN,
    b'\x1b[1;2C': Capability.kRIT,
    b'\x1b[1;2D': Capability.kLFT,

    # rxvt
    b'\x1b[a': Capability.kUP,
    b'\x1b[b': Capability.kDN,
    b'\x1b[c': Capability.kRIT,
    b'\x1b[d': Capability.kLFT,

    b'\x1bOa': Capability.kUP5,
    b'\x1bOb': Capability.kDN5,
    b'\x1bOc': Capability.kRIT5,
    b'\x1bOd': Capability.kLFT5,

    b'\x1b[3^': Capability.kDC5,
    b'\x1b[2^': Capability.kIC5,

    b'\x1b[3@': Capability.kDC6,
    b'\x1b[2@': Capability.kIC6,

    b'\x1b[7~': Capability.key_home,
    b'\x1b[8~': Capability.key_end,

    b'\x1b[7^': Capability.kHOM5,
    b'\x1b[8^': Capability.kEND5,

    b'\x1b[7@': Capability.kHOM6,
    b'\x1b[8@': Capability.kEND6,

    b'\x1b[6^': Capability.kNXT5,
    b'\x1b[5^': Capability.kPRV5,

    b'\x1b[6@': Capability.kNXT6,
    b'\x1b[5@': Capability.kPRV6,
}


FOCUS_SEQUENCES = {
    b'\x1b[I': Capability.focus_in,
    b'\x1b[O': Capability.focus_out,
}


PASTE_SEQUENCES = {
    b'\x1b[200~': Capability.paste_begin,
    b'\x1b[201~': Capability.paste_finish,
}


KEY_SEQUENCE_PATTERNS = [
    re.compile('\x1b\[[a-zA-Z]', re.ASCII),
    re.compile('\x1bO[a-zA-Z]', re.ASCII),
    re.compile('\x1bO[0-9][a-zA-Z]', re.ASCII),
    re.compile('\x1b\?[a-zA-Z]', re.ASCII),
    re.compile('\x1b\[[0-9]{1,3}[\^~@$]', re.ASCII),
    re.compile('\x1b\[[0-9]{1,2};[0-9]{1,2}[\^~@$]', re.ASCII),
    re.compile('\x1b\[[0-9]{1,2};[0-9]{1,2}[A-Z]', re.ASCII),
    # TODO: kmouse, focus in/out, mouse events parsing?
]


MOUSE_REPORT_PATTERNS = [
    # re.compile('\x1b[\[>]M(?P<btn>)(?P<column>)(?P<row>)(?P<state>)')
    re.compile('\x1b[\[>]M(?P<btn>.)(?P<column>.{1,2})(?P<row>.{1,2})(?P<state>)'), # default or EXT_MODE_MOUSE
    re.compile('\x1b\[<(?P<btn>[0-9]{1,3});(?P<column>[0-9]{1,4});(?P<row>[0-9]{1,4})(?P<state>[mM])', re.ASCII), # SGR_EXT_MODE_MOUSE
    re.compile('\x1b\[(?P<btn>[0-9]{1,3});(?P<column>[0-9]{1,4});(?P<row>[0-9]{1,4})(?P<state>M)', re.ASCII),   # URXVT_EXT_MODE_MOUSE
]


CURSOR_REPORT_PATTERNS = [
    re.compile('\x1b\[(?P<row>[0-9]{1,4});(?P<column>[0-9]{1,4})R', re.ASCII),
]


class Sequence(str):

    def __new__(cls, sequence, *, key=None, is_escaped=False):
        new = super().__new__(cls, sequence)
        new.key = key # Capability name
        new.is_escaped = is_escaped
        return new


class SequenceParser:

    """Parse input sequence characters and yield Sequence.

    Unlike decoder this parser assumes that whole available input sequence is passed in.

    """

    def __init__(self, terminfo, encoding):
        self._terminfo = terminfo
        self._encoding = encoding or 'utf-8'
        self._key_sequences = None

    @property
    def key_sequences(self):
        if self._key_sequences is None:
           self._key_sequences = self.get_key_sequences()
        return self._key_sequences

    def get_key_sequences(self):
        key_sequences = {}

        # First defaults
        for sequence_mappings in [DEFAULT_KEY_SEQUENCES, FOCUS_SEQUENCES, PASTE_SEQUENCES]:
            for sequence, cap_name in sequence_mappings.items():
                key_sequences[sequence.decode(self._encoding)] = cap_name

        # Now check what is available in terminfo, and overwrite defaults if sequence in use is different
        for cap_name in STR_CAPABILITIES:
            if cap_name.startswith('k') and not cap_name.startswith('key_'):
                sequence = self._terminfo.get_str(cap_name)
                if sequence:
                    key_sequences[sequence.decode(self._encoding)] = cap_name

        return key_sequences

    def _match_patterns(self, characters, patterns):
        for pattern in patterns:
            match = pattern.match(characters)
            if match:
                sequence = Sequence(characters[:match.end()])
                return match, sequence
        return None, None

    def match_key(self, characters):
        match, sequence = self._match_patterns(characters, KEY_SEQUENCE_PATTERNS)
        if match:
            sequence.key = self.key_sequences.get(sequence)
            characters = characters[match.end():]
        return sequence, characters

    def match_mouse_report(self, characters):
        match, sequence = self._match_patterns(characters, MOUSE_REPORT_PATTERNS)
        if match:
            sequence.key = Capability.mouse_report
            characters = characters[match.end():]
            # TODO: Parse match.groups
            # sequence.x = int(match.group('row')) -1
            # sequence.y = int(match.group('column')) -1
        return sequence, characters

    def match_cursor_report(self, characters):
        match, sequence = self._match_patterns(characters, CURSOR_REPORT_PATTERNS)
        if match:
            sequence.key = Capability.cursor_report
            characters = characters[match.end():]
            # TODO: Parse match.groups
            sequence.x = int(match.group('row'))
            sequence.y = int(match.group('column'))
            if '%i' in self._terminfo.get_str(Capability.cursor_report):
                sequence.x -= 1
                sequence.y -= 1
        return sequence, characters

    def match_key_sequence(self, characters):
        key = self.key_sequences.get(characters)
        if key:
            return Sequence(characters, key=key), ''
        return None, characters

    def parse(self, characters):
        is_escaped = False
        while characters:
            # Direct hit, no need for further parsing
            sequence, characters = self.match_key_sequence(characters)
            # Try pattern matching
            if not sequence:
                sequence, characters = self.match_cursor_report(characters)
            if not sequence:
                sequence, characters = self.match_key(characters)
            if not sequence:
                sequence, characters = self.match_mouse_report(characters)
            if not sequence:
                # Just move one character forward
                sequence = Sequence(characters[:1])
                characters = characters[1:]

            if sequence == '\x1b':
                if is_escaped:
                    # Already got '\x1b', yield it
                    yield sequence
                else:
                    # Mark next sequence as is_escaped
                    is_escaped = True
                continue

            sequence.is_escaped = is_escaped
            yield sequence
            is_escaped = False

        if is_escaped:
            yield Sequence('\x1b')

