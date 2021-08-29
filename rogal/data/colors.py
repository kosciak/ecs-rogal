from ..collections.attrdict import AttrDict
from ..colors import HEX, ColorPalette


def parse_colors(data):
    colors = [HEX(color) for color in data]
    return colors


def parse_color_names(data):
    color_names = AttrDict(data)
    return color_names


class ColorPaletteParser:

    def __init__(self, colors, color_names):
        self.colors = colors
        self.color_names = color_names

    def parse_color(self, color, colors, color_names):
        if color.startswith('#'):
            return HEX(color)
        return colors[color_names[color]]

    def __call__(self, data):
        colors = []
        for name in data['colors']:
            colors.extend(self.colors.get(name)[len(colors):])

        color_names = AttrDict()
        for name in data['color_names']:
            color_names.update(self.color_names.get(name) or {})

        fg = self.parse_color(data['fg'], colors, color_names)
        bg = self.parse_color(data['bg'], colors, color_names)

        return ColorPalette(
            name=data['name'],
            fg=fg,
            bg=bg,
            color_names=color_names,
            colors=colors,
        )

