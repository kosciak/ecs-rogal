import numpy as np


rgb_dt = np.dtype('3B')
rgba_dt = np.dtype('4B')


tile_rgb_dt = np.dtype([
    ('ch',          '<i4'),
    ('fg',          rgb_dt),
    ('bg',          rgb_dt),
])


terrain_tile_dt = np.dtype([
    ('type',        'B'),
    ('material',    'B'),
])

terrain_id_dt = np.dtype(('u2', {'type': ('u1', 0), 'material': ('u1', 1)}))


flags_dt = np.dtype('u4')


movement_cost_dt = np.dtype([
    ('walk',        'u2'),
    ('fly',         'u2'),
    ('swim',        'u2'),
])

