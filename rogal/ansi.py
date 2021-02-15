from enum import Enum


"""Rudimentary ANSI support."""


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
    UNDERLINED = 4
    INVERT = 7
    FG_BASE = 30
    SET_FG = 38
    DEFAULT_FG = 39
    BG_BASE = 40
    SET_BG = 48
    DEFAULT_BG = 49
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


def sgr(*parameters):
    return sequence(EscapeSequence.CSI.value, CSI_Code.SGR.value, *parameters)


def reset():
    return sgr(SGR_Attribute.RESET.value)


def bold():
    return sgr(SGR_Attribute.BOLD.value)

def dim():
    return sgr(SGR_Attribute.DIM.value)

def underlined():
    return sgr(SGR_Attribute.UNDERLINED.value)

def inverted():
    return sgr(SGR_Attribute.INVERT.value)


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


def show_console(console):
    lines = []
    for row in console.tiles_rgb:
        row_txt = []
        for ch, fg, bg in row:
            row_txt.append(fg_rgb(*fg)+bg_rgb(*bg)+chr(ch)+reset())
        lines.append(''.join(row_txt))
    print('\n'.join(lines))

