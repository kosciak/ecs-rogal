import numpy as np


# Same as tcod.console.Console._DTYPE_RGB
rgb_console_dt = np.dtype({
    'names':    ['ch', 'fg', 'bg'],
    'formats':  ['<i4', ('u1', (3,)), ('u1', (3,))],
    'offsets':  [0, 4, 8],
    'itemsize': 12
})


rgb_dt = np.dtype('3B')
rgba_dt = np.dtype('4B')


tile_rgb_dt = np.dtype([
    ('ch',          '<i4'),
    ('fg',          rgb_dt),
    ('bg',          rgb_dt),
])


terrain_dt = np.dtype('u1')


flags_dt = np.dtype('u4')


movement_cost_dt = np.dtype([
    ('walk',        'u2'),
    ('fly',         'u2'),
    ('swim',        'u2'),
])

