
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
        """Return ColorMap as gradient between two HSV colors, with given number of steps."""
        colors = []
        for color in color_min.to_hsv().gradient(color_max, steps=steps):
            colors.append(color.to_rgb())
        return ColorMap(colors)

    @staticmethod
    def from_rgb_gradient(color_min, color_max, steps=256):
        """Return ColorMap as gradient between two RGB colors, with given number of steps."""
        colors = []
        for color in color_min.to_rgb().gradient(color_max, steps=steps):
            colors.append(color.to_rgb())
        return ColorMap(colors)


class ColorNames:

    @classmethod
    def get(cls, name):
        return getattr(cls, name)


class ColorPalette:

    def __init__(self, name, fg, bg, colors, color_names=None):
        self.name = name
        self.fg = fg
        self.bg = bg
        #self.cursor_fg = None
        #self.cursor_bg = None
        self.colors = colors
        self.color_names = color_names

    def __len__(self):
        return len(self.colors)

    def get(self, key):
        if isinstance(key, str) and self.color_names:
            key = self.color_names.get(key)
        if key is None:
            return None
        return self.colors[key]

    def __getattr__(self, key):
        return self.get(key)

    def __getitem__(self, key):
        return self.get(key)

    def invert(self, name=None):
        return ColorPalette(name or self.name, self.bg, self.fg, self.colors)

    def __repr__(self):
        return f'<ColorPalette name="{self.name}">'


