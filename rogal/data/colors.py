from ..collections.attrdict import AttrDict
from ..colors import HEX


def parse_colors(data):
    colors = [HEX(color) for color in data]
    return colors


def parse_color_names(data):
    color_names = AttrDict(data)
    return color_names

