import numpy as np


# Same as tcod.console.Console._DTYPE_RGB
CONSOLE_RGB_DT = np.dtype({
    'names':    ['ch', 'fg', 'bg'],
    'formats':  ['<i4', ('u1', (3,)), ('u1', (3,))],
    'offsets':  [0, 4, 8],
    'itemsize': 12
})


RGB_DT = np.dtype('3B')
RGBA_DT = np.dtype('4B')


TILE_RGB_DT = np.dtype([
    ('ch',      '<i4'),
    ('fg',      RGB_DT),
    ('bg',      RGB_DT),
])


TERRAIN_DT = np.dtype('u1')


FLAGS_DT = np.dtype('u4')


MOVEMENT_COST_DT = np.dtype([
    ('walk',    'u2'),
    ('fly',     'u2'),
    ('swim',    'u2'),
])

