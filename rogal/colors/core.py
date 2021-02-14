import collections
import colorsys
import math


"""Colors, color manipulation and conversions, color maps calculations."""


class Color:

    """Base class for Color implementations in different color models."""

    __slots__ = ()

    @classmethod
    def from_values(cls, values, alpha=1.):
        raise NotImplementedError()

    @property
    def values(self):
        raise NotImplementedError()

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
        if alpha < 1.:
            alpha = alpha*255
        return self.__class__(self.values, alpha)

    @property
    def rgba(self):
        return (*self.rgb, self.alpha)

    @property
    def hsva(self):
        return (*self.hsv, self.alpha)

    def interpolate(self, other, level=0.5):
        # Linear color interpolation
        # TODO: For HSV see: https://www.alanzucconi.com/2016/01/06/colour-interpolation/2/
        values = self.values
        other_values = other.values
        interpolated_values = [(other_values[i]-values[i])*level + values[i]
                               for i in range(len(values))]
        alpha = (other.alpha-self.alpha)*level + self.alpha
        return self.__class__.from_values(interpolated_values, alpha)

    def gradient(self, other, steps):
        values = self.values
        other_values = other.values
        values_diff = [other_values[i] - values[i] for i in range(len(values))]
        alpha_diff = other.alpha - self.alpha
        # TODO: Consider: for value in np.linspace(0, 1, steps)
        for step in range(steps):
            level = step / (steps - 1)
            gradient_values = [values_diff[i]*level + values[i]
                               for i in range(len(values))]
            alpha = (other.alpha-self.alpha)*level + self.alpha
            yield self.__class__.from_values(gradient_values, alpha)


class RGBColor(Color, collections.namedtuple(
    'RGBColor', [
        'rgb',
        'alpha',
    ])):

    """Color in RGB color model."""

    __slots__ = ()

    @classmethod
    def from_values(cls, values, alpha=255):
        if alpha < 1.:
            alpha = alpha*255
        return cls((int(values[0]*255), int(values[1]*255), int(values[2]*255)), alpha)

    @property
    def values(self):
        return (self.rgb[0]/255., self.rgb[1]/255., self.rgb[2]/255.)

    @property
    def red(self):
        return self.rgb[0]
    r = red

    @property
    def green(self):
        return self.rgb[1]
    g = green

    @property
    def blue(self):
        return self.rgb[2]
    b = blue

    def to_rgb(self):
        return self

    def to_hsv(self):
        values = colorsys.rgb_to_hsv(*self.values)
        return HSVColor.from_values(values, self.alpha)

    @property
    def hsv(self):
        hsv_color = self.to_hsv()
        return hsv_color.hsv

    def interpolate(self, other, level=0.5):
        other = other.to_rgb()
        return super().interpolate(other, level)

    def gradient(self, other, steps):
        other = other.to_rgb()
        return super().gradient(other, steps)

    def greyscale(self):
        # Convert to greyscale using linear luminosity method
        # See: https://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale
        linear = int(self.red*0.2126 + self.green*0.7152 + self.blue*0.0722)
        return RGBColor((linear, linear, linear), self.alpha)

    def saturate(self, level=1.0):
        return self.to_hsv().saturate(level).to_rgb()

    def desaturate(self, level=1.0):
        return self.to_hsv().desaturate(level).to_rgb()

    @property
    def hex(self):
        if self.alpha < 255:
            values = self.rgba
        else:
            values = self.rgb
        hex_val = ''.join([format(val, '02x') for val in values])
        return '#' + hex_val.upper()

    def __repr__(self):
        return "<RGB red=%d, green=%d, blue=%d, alpha=%d>" % self.rgba


class HSVColor(Color, collections.namedtuple(
    'HSVColor', [
        'hsv',
        'alpha',
    ])):

    """Color in HSV (Hue, Saturation, Value) color model."""

    __slots__ = ()

    @classmethod
    def from_values(cls, values, alpha=255):
        if alpha < 1.:
            alpha = alpha*255
        return cls((int(values[0]*360), int(values[1]*100), int(values[2]*100)), alpha)

    @property
    def values(self):
        return (self.hsv[0]/360.%1., self.hsv[1]/100., self.hsv[2]/100.)

    @property
    def hue(self):
        return self.hsv[0]
    h = hue

    @property
    def saturation(self):
        return self.hsv[1]
    s = saturation

    @property
    def value(self):
        return self.hsv[2]
    v = value

    def to_hsv(self):
        return self

    def to_rgb(self):
        values = colorsys.hsv_to_rgb(*self.values)
        return RGBColor.from_values(values, self.alpha)

    @property
    def rgb(self):
        rgb_color = self.to_rgb()
        return rgb_color.rgb

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
        saturation = min([100, self.saturation * level])
        return HSVColor((self.hue, int(saturation), self.value), self.alpha)

    def desaturate(self, level=1.0):
        level = abs(level - 1.0)
        saturation = max([0, self.saturation * level])
        return HSVColor((self.hue, int(saturation), self.value), self.alpha)

    @property
    def hex(self):
        if self.alpha < 255:
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
    return RGBColor((red, green, blue), alpha)


def HSV(hue, saturation, value, alpha=255):
    """Return HSV color.

    Saturation is in range of 0-360 degrees, Hue, and value in range of 0-100%.
    Value of Alpha is in range of 0-255.

    """
    return HSVColor((hue, saturation, value), alpha)


def HEX(color, alpha=255):
    """Return color from hex: #RRGGBBaa or #HHHSSVVaa"""
    if color.startswith('#'):
        color = color[1:]
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

