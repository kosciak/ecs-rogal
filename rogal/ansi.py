import sys

from enum import Enum


"""Rudimentary ANSI support.

See: https://en.wikipedia.org/wiki/ANSI_escape_code

"""


class EscapeSequence(Enum):
    # CSI = '\x1b[' # Control Sequence Introducer
    CSI = '\033['   # Control Sequence Introducer


class CSI_Code(Enum):
    CUU = 'A'   # Cursor Up
    CUD = 'B'   # Cursor Down
    CUF = 'C'   # Cursor Forward
    CUB = 'D'   # Cursor Back
    CNL = 'E'   # Cursor Next Line
    CPL = 'F'   # Cursor Previous Line
    CHA = 'G'   # Cursor Horizontal Absolute
    CUP = 'H'   # Cursor Position
    ED = 'J'    # Erase Display
    EL = 'K'    # Erase Line
    SU = 'S'    # Scroll Up
    SD = 'T'    # Scroll Down
    SGR = 'm'   # Select Graphic Rendition / Set Graphic Rendition


class SGR_Attribute(Enum):
    RESET = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINED = 4
    SLOW_BLINK = 5
    RAPID_BLINK = 6
    INVERT = 7
    HIDE = 8
    STRIKE = 9
    FG_BASE = 30
    SET_FG = 38
    DEFAULT_FG = 39
    BG_BASE = 40
    SET_BG = 48
    DEFAULT_BG = 49
    OVERLINED = 53
    FG_BRIGHT_BASE = 90
    BG_BRIGHT_BASE = 100


class ColorsMode(Enum):
    COLORS_256 = 5
    COLORS_RGB = 2


class Color(Enum):
    BLACK=0,
    RED=1,
    GREEN=2,
    YELLOW=3,
    BLUE=4,
    MAGENTA=5,
    CYAN=6,
    WHITE=7,


def sequence(escape_sequence, code, *parameters):
    return '%s%s%s' % (escape_sequence, ';'.join([f'{param}' for param in parameters]), code)


def cursor_up(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.CUU.value, n)

def cursor_down(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.CUD.value, n)

def cursor_forward(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.CUF.value, n)

def cursor_back(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.CUB.value, n)

def cursor_next_line(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.CNL.value, n)

def cursor_prev_line(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.CPL.value, n)

def cursor_column(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.CHA.value, n)

def cursor_position(n=1, m=1):
    """Move cursor to row n, column m (1-indexed from top-left)."""
    return sequence(EscapeSequence.CSI.value, CSI_Code.CUP.value, n, m)


def erase_display(n=1):
    return sequence(EscapeSequence.CSI.value, CSI_Code.ED.value, n)


def sgr(*parameters):
    return sequence(EscapeSequence.CSI.value, CSI_Code.SGR.value, *parameters)


def reset():
    return sgr(SGR_Attribute.RESET.value)


def bold():
    return sgr(SGR_Attribute.BOLD.value)

def dim():
    return sgr(SGR_Attribute.DIM.value)

def italic():
    return sgr(SGR_Attribute.ITALIC.value)

def underlined():
    return sgr(SGR_Attribute.UNDERLINED.value)

def slow_blink():
    return sgr(SGR_Attribute.SLOW_BLINK.value)

def rapid_blink():
    return sgr(SGR_Attribute.RAPID_BLINK.value)

def inverted():
    return sgr(SGR_Attribute.INVERT.value)

def hide():
    return sgr(SGR_Attribute.HIDE.value)

def strike():
    return sgr(SGR_Attribute.STRIKE.value)

def overlined():
    return sgr(SGR_Attribute.OVERLINED.value)


def fg(color):
    return sgr(SGR_Attribute.FG_BASE.value+color%8)

def bg(color):
    return sgr(SGR_Attribute.BG_BASE.value+color%8)

def fg_bright(color):
    return sgr(SGR_Attribute.FG_BRIGHT_BASE.value+color%8)

def bg_bright(color):
    return sgr(SGR_Attribute.BG_BRIGHT_BASE.value+color%8)

def fg_bold(color):
    return sgr(SGR_Attribute.FG_BASE.value+color%8, SGR_Attribute.BOLD.value)

def bg_bold(color):
    return sgr(SGR_Attribute.FG_BASE.value+color%8, SGR_Attribute.BOLD.value)

def fg_256(color):
    return sgr(SGR_Attribute.SET_FG.value, ColorsMode.COLORS_256.value, color)

def bg_256(color):
    return sgr(SGR_Attribute.SET_BG.value, ColorsMode.COLORS_256.value, color)

def fg_rgb(r, g, b):
    return sgr(SGR_Attribute.SET_FG.value, ColorsMode.COLORS_RGB.value, r, g, b)

def bg_rgb(r, g, b):
    return sgr(SGR_Attribute.SET_BG.value, ColorsMode.COLORS_RGB.value, r, g, b)


def color_256(fg, bg):
    sequences = []
    if fg:
        sequences.append(fg_256(fg))
    if bg:
        sequences.append(bg_256(bg))
    return ''.join(sequences)

def color_rgb(fg, bg):
    sequences = []
    if fg:
        sequences.append(fg_rgb(*fg))
    if bg:
        sequences.append(bg_rgb(*bg))
    return ''.join(sequences)


def show_colors(fn, colors_num=256):
    elements = []
    print('SYSTEM COLORS:')
    columns = 8
    for color in range(colors_num):
        element = '%s %03d %s' % (fn(color), color, reset())
        elements.append(element)
        if len(elements) == columns:
            print(''.join(elements))
            elements = []
        if color == 15:
            print('216 COLORS:')
            columns = 6
        if color == 231:
            print('GRAYSCALE COLORS:')
            columns = 12
    if elements:
        print(''.join(elements))


def show_colors_rgb(colors, columns=8):
    elements = []
    for idx, color in enumerate(colors):
        element = '%s %03d %s' % (bg_rgb(*color.rgb), idx, reset())
        elements.append(element)
        if len(elements) == columns:
            print(''.join(elements))
            elements = []
    if elements:
        print(''.join(elements))


def show_color(color):
    print(f'{bg_rgb(*color.rgb)} {color.rgb} {reset()}')


def show_rgb_console(console):
    prev_fg = None
    prev_bg = None
    lines = []
    for row in console.tiles:
        row_txt = []
        for ch, fg, bg in row:
            if prev_fg is None or not (fg == prev_fg).all():
                row_txt.append(fg_rgb(*fg))
                prev_fg = fg
            if prev_bg is None or not (bg == prev_bg).all():
                row_txt.append(bg_rgb(*bg))
                prev_bg = bg
            row_txt.append(chr(ch))
        lines.append(''.join(row_txt))
    lines.append(reset())
    sys.stdout.write('\n'.join(lines))
    sys.stdout.flush()

