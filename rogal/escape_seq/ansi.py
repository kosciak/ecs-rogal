import sys

from .core import EscapeSequence, csi


"""Rudimentary ANSI support.

See: https://en.wikipedia.org/wiki/ANSI_escape_code

"""


class CSI:
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


class SGR_Attribute:
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


class ColorsMode:
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



def cursor_up(n=1):
    return csi(CSI.CUU, n)

def cursor_down(n=1):
    return csi(CSI.CUD, n)

def cursor_forward(n=1):
    return csi(CSI.CUF, n)

def cursor_back(n=1):
    return csi(CSI.CUB, n)

def cursor_next_line(n=1):
    return csi(CSI.CNL, n)

def cursor_prev_line(n=1):
    return csi(CSI.CPL, n)

def cursor_column(n=1):
    return csi(CSI.CHA, n)

def cursor_position(n=1, m=1):
    """Move cursor to row n, column m (1-indexed from top-left)."""
    return csi(CSI.CUP, n, m)


def erase_display(n=1):
    return csi(CSI.ED, n)


def sgr(*parameters):
    return csi(CSI.SGR, *parameters)


def reset():
    return sgr(SGR_Attribute.RESET)


def bold():
    return sgr(SGR_Attribute.BOLD)

def dim():
    return sgr(SGR_Attribute.DIM)

def italic():
    return sgr(SGR_Attribute.ITALIC)

def underlined():
    return sgr(SGR_Attribute.UNDERLINED)

def slow_blink():
    return sgr(SGR_Attribute.SLOW_BLINK)

def rapid_blink():
    return sgr(SGR_Attribute.RAPID_BLINK)

def inverted():
    return sgr(SGR_Attribute.INVERT)

def hide():
    return sgr(SGR_Attribute.HIDE)

def strike():
    return sgr(SGR_Attribute.STRIKE)

def overlined():
    return sgr(SGR_Attribute.OVERLINED)


def fg(color):
    return sgr(SGR_Attribute.FG_BASE+color%8)

def bg(color):
    return sgr(SGR_Attribute.BG_BASE+color%8)

def fg_bright(color):
    return sgr(SGR_Attribute.FG_BRIGHT_BASE+color%8)

def bg_bright(color):
    return sgr(SGR_Attribute.BG_BRIGHT_BASE+color%8)

def fg_bold(color):
    return sgr(SGR_Attribute.FG_BASE+color%8, SGR_Attribute.BOLD)

def bg_bold(color):
    return sgr(SGR_Attribute.FG_BASE+color%8, SGR_Attribute.BOLD)

def fg_256(color):
    return sgr(SGR_Attribute.SET_FG, ColorsMode.COLORS_256, color)

def bg_256(color):
    return sgr(SGR_Attribute.SET_BG, ColorsMode.COLORS_256, color)

def fg_rgb(r, g, b):
    return sgr(SGR_Attribute.SET_FG, ColorsMode.COLORS_RGB, r, g, b)

def bg_rgb(r, g, b):
    return sgr(SGR_Attribute.SET_BG, ColorsMode.COLORS_RGB, r, g, b)


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

    columns = console.width
    line = []
    column = 0
    for ch, fg, bg in console.tiles_gen(encode_ch=chr):
        column += 1
        if prev_fg is None or not (fg == prev_fg).all():
            line.append(fg_rgb(*fg))
            prev_fg = fg
        if prev_bg is None or not (bg == prev_bg).all():
            line.append(bg_rgb(*bg))
            prev_bg = bg
        line.append(ch)
        if column >= columns:
            lines.append(''.join(line))
            line = []
            column = 0

    sys.stdout.write(cursor_next_line(1).join(lines))
    sys.stdout.write(reset())
    sys.stdout.flush()

