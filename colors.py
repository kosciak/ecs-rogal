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

    @property
    def a(self):
        return self.alpha

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
    def rgb(self):
        rgb = self.to_rgb()
        return int(rgb.red*255), int(rgb.green*255), int(rgb.blue*255)

    @property
    def rgba(self):
        return (*self.rgb, int(self.alpha*255))

    @property
    def hsv(self):
        hsv = self.to_hsv()
        return int(hsv.hue*360), int(hsv.saturation*100), int(hsv.value*100)

    @property
    def hsva(self):
        return (*self.hsv, int(self.alpha*255))

    def interpolate(self, other, level=0.5):
        # Linear color interpolation
        values = [(other.values[i]-self.values[i])*level + self.values[i] 
                  for i in range(len(self.values))]
        alpha = (other.alpha-self.alpha)*level + self.alpha
        return self.__class__(values, alpha)

    def gradient(self, other, steps):
        values_diff = [other.values[i] - self.values[i] for i in range(len(self.values))]
        alpha_diff = other.alpha - self.alpha
        for step in range(steps):
            level = step / (steps - 1)
            values = [values_diff[i]*level + self.values[i] 
                      for i in range(len(self.values))]
            alpha = (other.alpha-self.alpha)*level + self.alpha
            yield self.__class__(values, alpha)


class RGBColor(Color):

    """Color in RGB color model."""

    __slots__ = ()

    @property
    def red(self):
        return self.values[0]
    r = red

    @property
    def green(self):
        return self.values[1]
    g = green

    @property
    def blue(self):
        return self.values[2]
    b = blue

    def to_rgb(self):
        return self

    def to_hsv(self):
        values = colorsys.rgb_to_hsv(*self.values)
        return HSVColor(values, self.alpha)

    def interpolate(self, other, level=0.5):
        other = other.to_rgb()
        return super().interpolate(other, level)

    def gradient(self, other, steps):
        other = other.to_rgb()
        return super().gradient(other, steps)

    def greyscale(self):
        # Convert to greyscale using linear luminosity method
        # See: https://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale
        linear = self.red*0.2126 + self.green*0.7152 + self.blue*0.0722
        return RGBColor((linear, linear, linear), self.alpha)

    def saturate(self, level=3.0):
        return self.to_hsv().saturate(level).to_rgb()

    def desaturate(self, level=1.0):
        return self.to_hsv().desaturate(level).to_rgb()

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
    h = hue

    @property
    def saturation(self):
        return self.values[1]
    s = saturation

    @property
    def value(self):
        return self.values[2]
    v = value

    def to_hsv(self):
        return self

    def to_rgb(self):
        values = colorsys.hsv_to_rgb(*self.values)
        return RGBColor(values, self.alpha)

    def interpolate(self, other, level=0.5):
        other = other.to_hsv()
        return super().interpolate(other, level)

    def gradient(self, other, steps):
        other = other.to_hsv()
        return super().gradient(other, steps)

    def greyscale(self):
        return self.to_rgb().greyscale().to_hsv()

    def saturate(self, level=1.0):
        level += 1.0
        saturation = min([1.0, self.saturation * level])
        return HSVColor((self.hue, saturation, self.value), self.alpha)

    def desaturate(self, level=1.0):
        level = abs(level - 1.0)
        saturation = max([0.0, self.saturation * level])
        return HSVColor((self.hue, saturation, self.value), self.alpha)

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
    Value of Alpha is in range of 0-255.
    
    """
    return RGBColor((red/255., green/255., blue/255.), alpha/255.)


def HSV(hue, saturation, value, alpha=255):
    """Return HSV color.

    Saturation is in range of 0-360 degrees, Hue, and value in range of 0-100%.
    Value of Alpha is in range of 0-255.
    
    """
    return HSVColor((hue/360.%1., saturation/100., value/100.), alpha/255.)


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
    def from_hsv_gradient(color_min, color_max, steps=256):
        """Return ColorMap as gradient between two colors, with given number of steps."""
        colors = []
        for color in color_min.to_hsv().gradient(color_max, steps=steps):
            colors.append(color.to_rgb())
        return ColorMap(colors)

    @staticmethod
    def from_rgb_gradient(color_min, color_max, steps=256):
        """Return ColorMap as gradient between two colors, with given number of steps."""
        colors = []
        for color in color_min.to_rgb().gradient(color_max, steps=steps):
            colors.append(color.to_rgb())
        return ColorMap(colors)


class ColorPalette:

    def __init__(self, fg, bg, colors):
        self.fg = fg
        self.bg = bg
        #self.cursor_fg = None
        #self.cursor_bg = None
        # TODO: add default_colors list?
        #self.colors = DEFAULT_X11_COLORS[:]
        #self.colors[0:len(colors)] = colors
        self.colors = colors

    def __len__(self):
        return len(self.colors)

    def get(self, key):
        return self.colors[key]

    def __getitem__(self, key):
        return self.colors[key]


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
