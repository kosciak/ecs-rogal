import sys

from .escape_seq import csi, ocs
from .escape_seq import CSI, XTWINOPS, TitleMode, Mode


"""Handy (X)Term sequence codes.

Some of them are not accesible using terminfo capabilities.

See: https://stackoverflow.com/questions/11023929/using-the-alternate-screen-in-a-bash-script
See: https://stackoverflow.com/questions/5966903/how-to-get-mousemove-and-mouseclick-in-bash
See: https://domoticx.com/terminal-codes-ansivt100/

"""

def save_title(mode=TitleMode.ICON_AND_WINDOW):
    return csi(CSI.XTWINOPS, XTWINOPS.SAVE_TITLE, mode)

def restore_title(mode=TitleMode.ICON_AND_WINDOW):
    return csi(CSI.XTWINOPS, XTWINOPS.RESTORE_TITLE, mode)

def set_title(title, mode=TitleMode.ICON_AND_WINDOW):
    return ocs(mode, title)


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

