import collections
from enum import Enum

import tcod

from colors import RGB


TCOD_COLORS = []

class TCODColor(Enum):
    pass


def init_colors():
    prefixed_colors = collections.defaultdict(dict)
    for name in tcod.constants.__all__:
        if name.isupper():
            continue
        tcod_color = getattr(tcod.constants, name)
        if not isinstance(tcod_color, tcod.color.Color):
            continue
        prefix, sep, base_name = name.rpartition('_')
        prefixed_colors[prefix][base_name] = RGB(*tcod_color)

    idx = 0
    for prefix in prefixed_colors.keys():
        for base_name, color in prefixed_colors[prefix].items():
            if prefix:
                color_name = '%s_%s' % (prefix, base_name)
            else:
                color_name = base_name
            TCOD_COLORS.append(color)
            #print(color_name, color)
            setattr(TCODColor, color_name.upper(), idx)
            idx += 1

init_colors()
