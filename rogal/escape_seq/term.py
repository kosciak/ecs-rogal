import sys

from .core import ControlChar, EscapeSequence, csi, ocs


"""Rudimentary (X)Term sequence codes support.

See: /usr/share/doc/xterm/ctlseqs.txt
See: https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
See: http://www.xfree86.org/current/ctlseqs.html
See: https://terminalguide.namepad.de/

See: https://invisible-island.net/ncurses/terminfo.ti.html
See: http://manpages.ubuntu.com/manpages/xenial/man5/terminfo.5.html

Also:
https://stackoverflow.com/questions/11023929/using-the-alternate-screen-in-a-bash-script
https://stackoverflow.com/questions/5966903/how-to-get-mousemove-and-mouseclick-in-bash
?? https://domoticx.com/terminal-codes-ansivt100/

"""

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
    DSR = '6n'  # Device Status Report

    # Other
    XTWINOPS    = 't'   # Window manipulation
    SM          = 'h'   # Set Mode
    RM          = 'l'   # Reset Mode
    DECSET      = 'h'   # DEC Private Mode Set
    DECRST      = 'l'   # DEC Private Mode Reset


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


class Mode:
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

    FOCUS_EVENT_MOUSE = '?1004'     # Focus In/Out events

    ALTERNATE_SCROLL = '?1007'      # Alternate Scroll Wheel

    EXT_MODE_MOUSE = '?1005'        # Enable UTF-8 Mouse Mode
    SGR_EXT_MODE_MOUSE = '?1006'    # Enable SGR Mouse Mode
    URXVT_EXT_MODE_MOUSE = '?1015'  # Enable urxvt Mouse Mode
    PIXEL_POSITION_MOUSE = '?1016'  # Enable SGR Mouse PixelMode



def save_title(mode=TitleMode.ICON_AND_WINDOW):
    return csi(CSI.XTWINOPS, XTWINOPS.SAVE_TITLE, mode)

def restore_title(mode=TitleMode.ICON_AND_WINDOW):
    return csi(CSI.XTWINOPS, XTWINOPS.RESTORE_TITLE, mode)


def set_private_mode(mode):
    return csi(CSI.DECSET, mode)

def reset_private_mode(mode):
    return csi(CSI.DECRST, mode)


def show_cursor():
    return set_private_mode(Mode.DECTCEM)

def hide_cursor():
    return reset_private_mode(Mode.DECTCEM)


def set_alternate_buffer():
    return set_private_mode(Mode.ALTBUF_EXT)

def reset_alternate_buffer():
    return reset_private_mode(Mode.ALTBUF_EXT)


def set_application_keypad_mode():
    return set_private_mode(Mode.DECNKM)

def reset_application_keypad_mode():
    return reset_private_mode(Mode.DECNKM)


def set_title(title, mode=TitleMode.ICON_AND_WINDOW):
    return ocs(mode, title)

