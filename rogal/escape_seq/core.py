
SEPARATOR = ';' # NOTE: Some terminals also allows ':'

class ControlChar:
    NUL = '\0'
    SOH = '\x01'
    STX = '\x02'
    ETX = '\x03'
    EOT = '\x04'
    ENQ = '\x05'
    ACK = '\x06'
    BEL = '\a'
    BS  = '\b'
    HT  = '\t'
    LF  = '\n'
    VT  = '\v'
    FF  = '\f'
    CR  = '\r'
    SO  = '\x0e'
    SI  = '\x0f'
    DLE = '\x10'
    DC1 = '\x11'
    DC2 = '\x12'
    DC3 = '\x13'
    DC4 = '\x14'
    NAK = '\x15'
    SYN = '\x16'
    ETB = '\x17'
    CAN = '\x18'
    EM  = '\x19'
    SUB = '\x1a'
    ESC = '\x1b'
    FS  = '\x1c'
    GS  = '\x1d'
    RS  = '\x1e'
    US  = '\x1f'
    SP  = ' '
    DEL = '\x7f'


class EscapeSequence:
    IND = f'{ControlChar.ESC}D'     # Index
    NEL = f'{ControlChar.ESC}E'     # Next Line
    HTS = f'{ControlChar.ESC}H'     # Tab Set
    RI  = f'{ControlChar.ESC}M'     # Reverse Index
    SS2 = f'{ControlChar.ESC}N'     # Single Shift Two
    SS3 = f'{ControlChar.ESC}O'     # Single Shift Three
    DCS = f'{ControlChar.ESC}P'     # Device Control String
    SPA = f'{ControlChar.ESC}V'     # Start of Guarded Area
    EPA = f'{ControlChar.ESC}W'     # End of Guarded Area
    SOS = f'{ControlChar.ESC}X'     # Start of String
    CSI = f'{ControlChar.ESC}['     # Control Sequence Introducer
    ST  = f'{ControlChar.ESC}\\'    # String Terminator
    OCS = f'{ControlChar.ESC}]'     # Operating System Command
    PM  = f'{ControlChar.ESC}^'     # Privacy Message
    APC = f'{ControlChar.ESC}_'     # Application Program Command

    DECSC = f'{ControlChar.ESC}7'   # Save Cursor
    DECRC = f'{ControlChar.ESC}8'   # Restore Cursor

    DECKPNM = f'{ControlChar.ESC}>' # Reset Application Keypad Mode
    DECKPAM = f'{ControlChar.ESC}=' # Set Application Keypad Mode


def csi(code, *parameters):
    return '%s%s%s' % (EscapeSequence.CSI, SEPARATOR.join([f'{param}' for param in parameters]), code)


def ocs(*parameters, terminator=EscapeSequence.ST):
    return '%s%s%s' % (EscapeSequence.OCS, SEPARATOR.join([f'{param}' for param in parameters]), terminator)

