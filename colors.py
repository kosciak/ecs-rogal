import collections
import colorsys
import enum
import math


"""Colors, color manipulation and conversions, color maps calculations."""


class Color(collections.namedtuple(
    'Color', [
        'values', 
        'alpha',
    ])):

    """Base class for Color implementations in different color models."""

    __slots__ = ()

    def to_rgb(self):
        raise NotImplementedError()

    def to_hsv(self):
        raise NotImplementedError()

    @property
    def hex(self):
        raise NotImplementedError()

    def set_alpha(self, alpha):
        if type(alpha) == int or alpha > 1:
            alpha = alpha/255.
        return self.__class__(self.values, alpha)

    @property
    def rgba(self):
        rgb = self.to_rgb()
        return int(rgb.red*255), int(rgb.green*255), int(rgb.blue*255), int(self.alpha*255)

    @property
    def rgb(self):
        return self.rgba[:3]

    @property
    def hsva(self):
        hsv = self.to_hsv()
        return int(hsv.hue*360), int(hsv.saturaion*100), int(hsv.value*100), int(hsv.alpha*255)

    @property
    def hsv(self):
        return self.hsva[:3]


class RGBColor(Color):

    """Color in RGB color model."""

    __slots__ = ()

    @property
    def red(self):
        return self.values[0]

    @property
    def green(self):
        return self.values[1]

    @property
    def blue(self):
        return self.values[2]

    def to_rgb(self):
        return self

    def to_hsv(self):
        values = colorsys.rgb_to_hsv(*self.values)
        return HSVColor(values, self.alpha)

    @property
    def hex(self):
        if self.alpha < 1.:
            values = self.rgba
        else:
            values = self.rgb
        hex_val = ''.join([format(val, '02x') for val in values])
        return '#' + hex_val.upper()

    def __repr__(self):
        return "<RGB red=%d, green=%d, blue=%d, alpha=%d>" % self.rgba


class HSVColor(Color):

    """Color in HSV (Hue, Saturation, Value) color model."""

    __slots__ = ()

    @property
    def hue(self):
        return self.values[0]

    @property
    def saturaion(self):
        return self.values[1]

    @property
    def value(self):
        return self.values[2]

    def to_hsv(self):
        return self

    def to_rgb(self):
        values = colorsys.hsv_to_rgb(*self.values)
        return RGBColor(values, self.alpha)

    @property
    def hex(self):
        if self.alpha < 1.:
            values = self.hsva
        else:
            values = self.hsv
        hex_val = format(values[0], '03x') 
        hex_val += ''.join([format(val, '02x') for val in values[1:]])
        return '#' + hex_val.upper()

    def __repr__(self):
        return "<HSV hue=%d, saturation=%d, value=%d, alpha=%d>" % self.hsva


def RGB(red, green, blue, alpha=255):
    """Return RGB color. 

    Values of Red, Green, Blue are in range of 0-255.
    
    """
    return RGBColor((red/255., green/255., blue/255.), alpha/255.)


def HSV(hue, saturaion, value, alpha=255):
    """Return HSV color.

    Saturation is in range of 0-360 degrees, Hue, and value in range of 0-100%.
    
    """
    return HSVColor((hue/360.%1., saturaion/100., value/100.), alpha/255.)


def HEX(color):
    """Return color from hex: #RRGGBBaa or #HHHSSVVaa"""
    if color.startswith('#'):
        color = color[1:]
    alpha = 255
    if len(color) > 7:
        alpha = int(color[-2:], 16)
    if len(color) % 2 == 0:
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
        return RGB(red, green, blue, alpha)
    else:
        hue = int(color[0:3], 16)
        saturation = int(color[3:5], 16)
        value = int(color[5:7], 16)
        return HSV(hue, saturation, value, alpha)


# Some predefined colors:
RED = HSV(0, 100, 100)
YELLOW = HSV(60, 100, 100)
GREEN = HSV(120, 100, 100)
CYAN = HSV(180, 100, 100)
BLUE = HSV(240, 100, 100)
MAGENTA = HSV(300, 100, 100)

BLACK = HSV(0, 0, 0)
WHITE = HSV(0, 0, 100)


class ColorMap:

    """ColorMap consisting of list of Colors."""

    def __init__(self, colors):
        self.colors = colors

    @property
    def steps(self):
        return len(self.colors)

    def get(self, value):
        """Return Color associated with given value.

        value = (0., 1.]

        """
        n = value / (1./self.steps)
        if value and math.floor(n) == n:
            n -= 1
        return self.colors[int(n)]

    @staticmethod
    def from_gradient(color_min, color_max, steps=256):
        """Return ColorMap as gradient between two colors, with given number of steps."""
        colors = []
        hsva_min = color_min.to_hsv()
        hsva_max = color_max.to_hsv()
        values_range = [hsva_max.values[i] - hsva_min.values[i] for i in range(3)]
        alpha_range = hsva_max.alpha - hsva_min.alpha
        for value in range(0, steps):
            values = [value/float(steps-1)*values_range[i]+hsva_min.values[i] for i in range(3)]
            alpha = value/float(steps-1)*alpha_range+ hsva_min.alpha
            values[0] %= 1.
            rgba = HSVColor(values, alpha).to_rgb()
            colors.append(rgba)
        return ColorMap(colors)


class ColorPalleteIndex(enum.IntEnum):
    BLACK=0,
    RED=1,
    GREEN=2,
    YELLOW=3,
    BLUE=4,
    MAGENTA=5, 
    CYAN=6,
    WHITE=7,

    BLACK_BOLD=8,
    RED_BOLD=9,
    GREEN_BOLD=10,
    YELLOW_BOLD=11,
    BLUE_BOLD=12,
    MAGENTA_BOLD=13, 
    CYAN_BOLD=14,
    WHITE_BOLD=15,


class ColorPalette:

    def __init__(self, fg, bg, colors):
        self.fg = fg
        self.bg = bg
        #self.cursor_fg = None
        #self.cursor_bg = None
        self.colors = colors

    def __len__(self):
        return len(self.colors)

    def __getitem__(self, key):
        return self.colors[key]

    def __getattr__(self, name):
        name = name.upper()
        if name in {'FG', 'FOREGROUND'}:
            return self.fg
        if name in {'BG', 'BACKGROUND'}:
            return self.bg
        index = getattr(ColorPalleteIndexes, name)
        return self.colors[index]


TANGO_DARK = ColorPalette(
  fg=HEX("#babdb6"),
  bg=HEX("#000000"),
  colors=[
    HEX("#2e3436"),
    HEX("#cc0000"),
    HEX("#4e9a06"),
    HEX("#c4a000"),
    HEX("#3465a4"),
    HEX("#75507b"),
    HEX("#06989a"),
    HEX("#d3d7cf"),
    HEX("#555753"),
    HEX("#ef2929"),
    HEX("#8ae234"),
    HEX("#fce94f"),
    HEX("#729fcf"),
    HEX("#ad7fa8"),
    HEX("#34e2e2"),
    HEX("#eeeeec"),
  ])


TANGO_LIGHT = ColorPalette(
  fg=HEX("#000000"),
  bg=HEX("#babdb6"),
  colors=[
    HEX("#2e3436"),
    HEX("#cc0000"),
    HEX("#4e9a06"),
    HEX("#c4a000"),
    HEX("#3465a4"),
    HEX("#75507b"),
    HEX("#06989a"),
    HEX("#d3d7cf"),
    HEX("#555753"),
    HEX("#ef2929"),
    HEX("#8ae234"),
    HEX("#fce94f"),
    HEX("#729fcf"),
    HEX("#ad7fa8"),
    HEX("#34e2e2"),
    HEX("#eeeeec"),
  ])
