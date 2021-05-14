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


def get_key_sequences(terminfo):
    key_sequences = {}
    key_sequences.update(DEFAULT_KEY_SEQUENCES)
    for cap_name in STR_CAPABILITIES:
        if cap_name.startswith('k') and not cap_name.startswith('key_'):
           sequence = terminfo.get_str(cap_name)
           if sequence:
                key_sequences[sequence] = cap_name
    return key_sequences

