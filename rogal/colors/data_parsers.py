from ..collections.attrdict import AttrDict

from .core import RGB, HSV, HEX
from .palette import ColorPalette


def parse_color(data):
    if data.startswith('#'):
        return HEX(data)
    for key in ['rgb', 'RGB']:
        if key in data:
            return RGB(data[key])
    for key in ['hsv', 'HSV']:
        if key in data:
            return RGB(data[key])


def parse_colors_list(data):
    colors = [parse_color(color) for color in data]
    return colors


def parse_color_names(data):
    color_names = AttrDict(data)
    return color_names


class ColorPaletteParser:

    def __init__(self, colors_lists, color_names):
        self.colors_lists = colors_lists
        self.color_names = color_names

    def parse_color(self, data, colors, color_names):
        color = parse_color(data)
        if not color:
            color = colors[color_names[data]]
        return color

    def __call__(self, data):
        colors = []
        for name in data['colors']:
            colors.extend(self.colors_lists.get(name)[len(colors):])

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

