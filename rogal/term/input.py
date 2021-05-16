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

    b'\x1bOM': Capability.key_enter,

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


KEY_SEQUENCE_PATTERNS = [
    re.compile('\x1b\[[a-zA-Z]', re.ASCII),
    re.compile('\x1bO[a-zA-Z]', re.ASCII),
    re.compile('\x1b\?[a-zA-Z]', re.ASCII),
    re.compile('\x1b\[[0-9]{1,2}[\^~@$]', re.ASCII),
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


class KeySequence(str):

    def __new__(cls, sequence, *, key=None, is_escaped=False):
        new = super().__new__(cls, sequence)
        new.key = key # Capability name
        new.is_escaped = is_escaped
        return new


class SequenceParser:

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
        for sequence_mappings in [DEFAULT_KEY_SEQUENCES, FOCUS_SEQUENCES]:
            for sequence, cap_name in sequence_mappings.items():
                key_sequences[sequence.decode(self._encoding)] = cap_name

        # Now check what is available in terminfo, and overwrite defaults if sequence in use is different
        for cap_name in STR_CAPABILITIES:
            if cap_name.startswith('k') and not cap_name.startswith('key_'):
                sequence = self._terminfo.get_str(cap_name)
                if sequence:
                    key_sequences[sequence.decode(self._encoding)] = cap_name

        return key_sequences

    def match(self, sequence, patterns, key=None):
        match = None
        for pattern in patterns:
            match = pattern.match(sequence)
            if match:
                sequence = sequence[:match.end()]
                key = key or self.key_sequences.get(sequence)
                break
        if not match:
           key = None
        return match, key

    def match_key(self, sequence):
        return self.match(sequence, KEY_SEQUENCE_PATTERNS)

    def match_mouse_report(self, sequence):
        return self.match(sequence, MOUSE_REPORT_PATTERNS, Capability.mouse_report)

    def match_cursor_report(self, sequence):
        return self.match(sequence, CURSOR_REPORT_PATTERNS, Capability.cursor_report)

    def parse(self, input_sequence):
        sequence = None
        is_escaped = False
        while input_sequence:
            key = self.key_sequences.get(input_sequence)
            if key:
                # Direct hit, no need for further parsing
                yield KeySequence(
                    input_sequence,
                    key=key,
                    is_escaped=is_escaped
                )
                is_escaped = False
                break

            # Try pattern matching
            match, key = self.match_cursor_report(input_sequence)
            if not match:
                match, key = self.match_key(input_sequence)
            if not match:
                match, key = self.match_mouse_report(input_sequence)

            if match:
                sequence = input_sequence[:match.end()]
                input_sequence = input_sequence[match.end():]
            else:
                # Move one character forward
                sequence = input_sequence[:1]
                input_sequence = input_sequence[1:]
                if sequence == '\x1b':
                    if is_escaped:
                        # Already got '\x1b', yield it
                        yield KeySequence(sequence)
                        is_escaped = False
                    else:
                        # Mark next sequence as is_escaped
                        is_escaped = True
                    sequence = None

            if sequence:
                yield KeySequence(
                    sequence,
                    key=key or self.key_sequences.get(sequence),
                    is_escaped=is_escaped
                )
                sequence = None
                is_escaped = False

        if is_escaped:
            sequence = '\x1b'
            yield KeySequence(sequence)
