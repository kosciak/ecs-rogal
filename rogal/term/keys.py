import re

from .capabilities import STR_CAPABILITIES, Capability


"""Support for keyboard related capabilities.

Unfortunately not all key related capabilities that are supported by terminals are available in terminfo,
that's why here is a list of default values for each capability.

See: https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-PC-Style-Function-Keys
See: https://fossies.org/linux/rxvt/doc/rxvtRef.html#KeyCodes

"""


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


KEY_SEQ_PATTERNS = [
    re.compile('\x1b\[[a-zA-Z]', re.ASCII),
    re.compile('\x1bO[a-zA-Z]', re.ASCII),
    re.compile('\x1b\?[a-zA-Z]', re.ASCII),
    re.compile('\x1b\[[0-9]{1,2}[\^~@$]', re.ASCII),
    re.compile('\x1b\[[0-9]{1,2};[0-9]{1,2}[\^~@$]', re.ASCII),
    re.compile('\x1b\[[0-9]{1,2};[0-9]{1,2}[A-Z]', re.ASCII),
    # TODO: kmouse, focus in/out, mouse events parsing?
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
        key_sequences.update(DEFAULT_KEY_SEQUENCES)
        for cap_name in STR_CAPABILITIES:
            if cap_name.startswith('k') and not cap_name.startswith('key_'):
                sequence = self._terminfo.get_str(cap_name)
                if sequence:
                    key_sequences[sequence.decode(self._encoding)] = cap_name
        return key_sequences

    def match(self, sequence):
        match = None
        for pattern in KEY_SEQ_PATTERNS:
            match = pattern.match(sequence)
            if match:
                break
        return match

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
                break

            match = self.match(input_sequence)
            if match:
                sequence = input_sequence[0:match.end()]
                input_sequence = input_sequence[match.end():]
            else:
                sequence = input_sequence[:1]
                input_sequence = input_sequence[1:]
                if sequence == '\x1b':
                    if is_escaped:
                        yield KeySequence(sequence)
                    else:
                        is_escaped = True
                    sequence = None
            if sequence:
                yield KeySequence(
                    sequence,
                    key=self.key_sequences.get(sequence),
                    is_escaped=is_escaped
                )
                sequence = None
                is_escaped = False
        if is_escaped:
            sequence = '\x1b'
            yield KeySequence(sequence)

