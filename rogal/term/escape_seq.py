import functools

"""Rudimentary (X)Term sequence codes support.

Support is far from complete, included most basic ones, widely supported by terminals, that will come handy.
It may be better idea to use terminfo capabilities instead of manually crafting escape codes from scratch.

See: https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
See: http://www.xfree86.org/current/ctlseqs.html
See: http://manpages.ubuntu.com/manpages/impish/en/man4/console_codes.4.html
See: https://terminalguide.namepad.de/

"""


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


class CSI:
    # ANSI related
    CUU = 'A'   # Cursor Up
    CUD = 'B'   # Cursor Down
    CUF = 'C'   # Cursor Forward
    CUB = 'D'   # Cursor Back
    CNL = 'E'   # Cursor Next Line
    CPL = 'F'   # Cursor Previous Line
    CHA = 'G'   # Cursor Horizontal Absolute
    CUP = 'H'   # Cursor Position
    ED  = 'J'   # Erase Display
    EL  = 'K'   # Erase Line
    SU  = 'S'   # Scroll Up
    SD  = 'T'   # Scroll Down
    HVP = 'f'   # Horizontal Vertical Position
    SGR = 'm'   # Select Graphic Rendition / Set Graphic Rendition
    DSR = '5n'  # Device Status Report
    CPR = '6n'  # Cursor Postition Report

    # Other
    XTWINOPS    = 't'   # Window manipulation
    SM          = 'h'   # Set Mode
    RM          = 'l'   # Reset Mode
    DECSET      = 'h'   # DEC Private Mode Set
    DECRST      = 'l'   # DEC Private Mode Reset
    DECLL       = 'q'   # Set keyboard LEDs (0 - clear all, set: 1 - ScrollLock, 2 - NumLock, 3 - CapsLock)


class SGR:
    # SGR Attributes, used in ANSI codes
    RESET = 0
    BOLD = 1
    DIM = 2
    FAINT = DIM
    ITALIC = 3
    UNDERLINED = 4
    SLOW_BLINK = 5
    RAPID_BLINK = 6
    INVERT = 7
    INVERSE = INVERT
    HIDE = 8
    STRIKE = 9
    NORMAL = 22     # Reset BOLD, DIM
    RESET_BOLD = NORMAL
    RESET_DIM = NORMAL
    RESET_FAINT = NORMAL
    RESET_ITALIC = 23
    RESET_UNDERLINE = 24
    RESET_BLINK = 25
    RESET_INVERT = 27
    RESET_INVERSE = RESET_INVERT
    RESET_HIDE = 28
    FG_BASE = 30    # 30 - 37 - Set foreground to color
    SET_FG = 38     # Set foreground to 256 colors index or RGB tuple
    DEFAULT_FG = 39
    BG_BASE = 40    # 40 - 47 - Set background to color
    SET_BG = 48     # Set background to 256 colors index or RGB tuple
    DEFAULT_BG = 49
    OVERLINED = 53
    RESET_OVERLINED = 55
    FG_BRIGHT_BASE = 90
    BG_BRIGHT_BASE = 100


class ColorsMode:
    # Used by SGR.SET_FG and SGR.SET_BG
    COLORS_256 = 5
    COLORS_RGB = 2


class Color:
    BLACK   = 0,
    RED     = 1,
    GREEN   = 2,
    YELLOW  = 3,
    BLUE    = 4,
    MAGENTA = 5,
    CYAN    = 6,
    WHITE   = 7,


class XTWINOPS:
    SAVE_TITLE = 22
    RESTORE_TITLE = 23


class TitleMode:
    ICON_AND_WINDOW = 0
    ICON = 1
    WINDOW = 2


# For VT100 reference of DEC* modes
# See: https://vt100.net/docs/vt510-rm/contents.html
class Mode:
    IRM = '4'           # Insert mode

    DECCKM = '?1'       # When set, the cursor keys send an ESC O prefix, rather than ESC [

    DECOM = '?6'        # When set, cursor addressing is  relative  to  the  upper  left corner of the scrolling region

    DECAWM = '?7'       # Wraparound mode

    DECTCEM = '?25'     # Show/Hide cursor

    DECNKM = '?66'      # Application Keypad Mode

    ALTBUF = '?47'      # Alternate Screen Buffer

    ALLOW_ALTBUF = '?1046'  # Allow Alternate Screen Buffer
    ALTBUF_CE = '?1047'     # Alternate Screen Buffer, With Clear on Exit
    CSR_ALTBUF = '?1048'    # Cursor Save/Restore for use with Alternate Screen Buffer
    ALTBUF_EXT = '?1049'    # ?1047 + ?1048

    X10_MOUSE = '?9'                # Clicking only tracking
    VT200_MOUSE = '?1000'           # Down+up tracking
    VT200_HIGHLIGHT_MOUSE = '?1001' # Highlight mode
    BTN_EVENT_MOUSE = '?1002'       # Click and dragging tracking
    ANY_EVENT_MOUSE = '?1003'       # All motion tracking

    FOCUS_EVENT = '?1004'           # Focus In/Out events

    ALTERNATE_SCROLL = '?1007'      # Alternate Scroll Wheel

    EXT_MODE_MOUSE = '?1005'        # Enable UTF-8 Mouse Mode
    SGR_EXT_MODE_MOUSE = '?1006'    # Enable SGR Mouse Mode
    URXVT_EXT_MODE_MOUSE = '?1015'  # Enable urxvt Mouse Mode
    PIXEL_POSITION_MOUSE = '?1016'  # Enable SGR Mouse PixelMode

    BRACKETED_PASTE = '?2004'       # Set bracketed paste mode


@functools.lru_cache(maxsize=None)
def csi(code, *parameters):
    """Build CSI sequence."""
    return '%s%s%s' % (EscapeSequence.CSI, SEPARATOR.join([f'{param}' for param in parameters]), code)


@functools.lru_cache(maxsize=None)
def ocs(*parameters, terminator=EscapeSequence.ST):
    """Build OCS sequence."""
    return '%s%s%s' % (EscapeSequence.OCS, SEPARATOR.join([f'{param}' for param in parameters]), terminator)

