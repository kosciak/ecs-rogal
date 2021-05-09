import sys

from .core import ControlChar, EscapeSequence, csi


"""Rudimentary (X)Term sequence codes support.

See: /usr/share/doc/xterm/ctlseqs.txt
See: https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
See: http://www.xfree86.org/current/ctlseqs.html
See: https://terminalguide.namepad.de/

See: https://invisible-island.net/ncurses/terminfo.ti.html

Also:
https://stackoverflow.com/questions/11023929/using-the-alternate-screen-in-a-bash-script
https://stackoverflow.com/questions/5966903/how-to-get-mousemove-and-mouseclick-in-bash
?? https://domoticx.com/terminal-codes-ansivt100/

"""

class CSI:
    XTWINOPS    = 't'   # Window manipulation
    SM          = 'h'   # Set Mode
    RM          = 'l'   # Reset Mode
    DECSET      = 'h'   # DEC Private Mode Set
    DECRST      = 'l'   # DEC Private Mode Reset


class XTWINOPS:
    SAVE_TITLE = 22
    RESTORE_TITLE = 23


class TitleMode:
    ICON_AND_WINDOW = 0
    ICON = 1
    WINDOW = 2


class Mode:
    DECTCEM = '?25'    # Show/Hide cursor
    # TODO: Alternate buffer; mouse reporting


def osc(*parameters, terminator=EscapeSequence.ST):
    return '%s%s%s' % (EscapeSequence.OCS, ';'.join([f'{param}' for param in parameters]), terminator)


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


def set_title(title, mode=TitleMode.ICON_AND_WINDOW):
    return osc(mode, title)

