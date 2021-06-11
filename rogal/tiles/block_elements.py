import collections

import numpy as np


Split = collections.namedtuple(
    'Split', [
        'is_horizontal',
        'start', 'end'
    ])


Quadrant = collections.namedtuple(
    'Quadrant', [
        'upper_left', 'upper_right',
        'lower_left', 'lower_right',
    ])


# See: https://en.wikipedia.org/wiki/Block_Elements

SPLITS = {
    0x2580: Split(False, 0.0, 0.5),
    0x2581: Split(False, 0.875, 1.0),
    0x2582: Split(False, 0.75, 1.0),
    0x2583: Split(False, 0.625, 1.0),
    0x2584: Split(False, 0.5, 1.0),
    0x2585: Split(False, 0.375, 1.0),
    0x2586: Split(False, 0.25, 1.0),
    0x2587: Split(False, 0.125, 1.0),
    0x2588: Split(True, 0.0, 1.0),
    0x2589: Split(True, 0.0, 0.875),
    0x258a: Split(True, 0.0, 0.75),
    0x258b: Split(True, 0.0, 0.625),
    0x258c: Split(True, 0.0, 0.5),
    0x258d: Split(True, 0.0, 0.375),
    0x258e: Split(True, 0.0, 0.25),
    0x258f: Split(True, 0.0, 0.125),
    0x2590: Split(True, 0.5, 1.0),
    0x2594: Split(False, 0.0, 0.5),
    0x2595: Split(True, 0.875, 1.0),
}


SOLID_SHADES = {
    0x2591: 0.25,
    0x2592: 0.5,
    0x2593: 0.75,
}


QUADRANTS = {
    0x2596: Quadrant(False, False, True, False),
    0x2597: Quadrant(False, False, False, True),
    0x2598: Quadrant(True, False, False, False),
    0x2599: Quadrant(True, False, True, True),
    0x259a: Quadrant(True, False, False, True),
    0x259b: Quadrant(True, True, True, False),
    0x259c: Quadrant(True, True, False, True),
    0x259d: Quadrant(False, True, False, False),
    0x259e: Quadrant(False, True, True, False),
    0x259f: Quadrant(False, True, True, True),
}


class BlockElements:

    def get_split_tile(self, code_point, tile_size):
        split = SPLITS.get(code_point)
        if not split:
            return None

        tile = np.zeros(tile_size, dtype=np.uint8, order="F")

        if split.is_horizontal:
            start = int(tile.shape[0]*split.start)
            end = int(tile.shape[0]*split.end)
            tile[start:end] = 255
        else:
            start = int(tile.shape[1]*split.start)
            end = int(tile.shape[1]*split.end)
            tile[:, start:end] = 255

        return tile.transpose()

    def get_shade_tile(self, code_point, tile_size):
        shade_value = SOLID_SHADES.get(code_point)
        if not shade_value:
            return None

        tile = np.zeros(tile_size, dtype=np.uint8, order="F")

        tile[:] = int(256*shade_value)

        return tile.transpose()

    def get_quadrant_tile(self, code_point, tile_size):
        quadrant = QUADRANTS.get(code_point)
        if not quadrant:
            return None

        tile = np.zeros(tile_size, dtype=np.uint8, order="F")

        half_x = tile_size.width//2
        half_y = tile_size.height//2

        tile[:half_x, :half_y] = quadrant.upper_left and 255 or 0
        tile[half_x:, :half_y] = quadrant.upper_right and 255 or 0
        tile[:half_x, half_y:] = quadrant.lower_left and 255 or 0
        tile[half_x:, half_y:] = quadrant.lower_right and 255 or 0

        return tile.transpose()

    def has_code_point(self, code_point):
        if code_point in SPLITS:
            return True
        if code_point in SOLID_SHADES:
            return True
        if code_point in QUADRANTS:
            return True
        return False

    def get_tile(self, code_point, tile_size):
        if code_point in SPLITS:
            return self.get_split_tile(code_point, tile_size)

        if code_point in SOLID_SHADES:
            return self.get_shade_tile(code_point, tile_size)

        if code_point in QUADRANTS:
            return self.get_quadrant_tile(code_point, tile_size)

        return None

