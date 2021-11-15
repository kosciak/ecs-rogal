from ..collections.attrdict import AttrDict

from ..data import data_store, parsers

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


def parse_color_list(data):
    colors = [parse_color(color) for color in data]
    return colors


def parse_color_names(data):
    color_names = AttrDict(data)
    return color_names


def _parse_named_color(data, colors, color_names):
    color = parse_color(data)
    if not color:
        color = colors[color_names[data]]
    return color


def parse_color_palette(data):
    colors = []
    for name in data['colors']:
        colors.extend(parsers.parse_color_list(name)[len(colors):])

    color_names = AttrDict()
    for name in data['color_names']:
        color_names.update(parsers.parse_color_names(name) or {})

    fg = _parse_named_color(data['fg'], colors, color_names)
    bg = _parse_named_color(data['bg'], colors, color_names)

    return ColorPalette(
        name=data['name'],
        fg=fg,
        bg=bg,
        color_names=color_names,
        colors=colors,
    )


data_store.register('color_lists', parse_color_list)
data_store.register('color_names', parse_color_names)
data_store.register('color_palettes', parse_color_palette)

parsers.register('color', parse_color)
parsers.register('color_list', data_store.color_lists.parse)
parsers.register('color_names', data_store.color_names.parse)
parsers.register('color_palette', data_store.color_palettes.parse)

