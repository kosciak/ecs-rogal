import collections
from enum import Enum, IntFlag

import numpy as np


class Line(IntFlag):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2
    WIDE = SINGLE | DOUBLE


class Box(collections.namedtuple(
    'Box', [
        'top_line',
        'right_line',
        'bottom_line',
        'left_line',
        'center_pixels',
    ])):

    __slots__ = ()

    def _line_pixels(self, line, pixel_width=1):
        pixels = []

        if line & Line.DOUBLE:
            pixels.extend([255, ]*pixel_width)
        else:
            pixels.extend([0, ]*pixel_width)

        if line & Line.SINGLE:
            pixels.extend([255, ]*pixel_width)
        else:
            pixels.extend([0, ]*pixel_width)

        if line & Line.DOUBLE:
            pixels.extend([255, ]*pixel_width)
        else:
            pixels.extend([0, ]*pixel_width)

        return pixels

    def _horizontal(self, line, pixel_width=1):
        return self._line_pixels(line, pixel_width)

    def _vertical(self, line, pixel_width=1):
        return np.reshape(
            self._line_pixels(line, pixel_width),
            (3*pixel_width, 1)
        )

    def top(self, pixel_width=1):
        return self._vertical(self.top_line, pixel_width)

    def right(self, pixel_width=1):
        return self._horizontal(self.right_line, pixel_width)

    def bottom(self, pixel_width=1):
        return self._vertical(self.bottom_line, pixel_width)

    def left(self, pixel_width=1):
        return self._horizontal(self.left_line, pixel_width)

    def center(self, pixel_width=1):
        pixels = []
        for i in range(pixel_width):
            for p in self.center_pixels[0:3]:
                pixels.extend([p and 255 or 0, ]*pixel_width)
        for i in range(pixel_width):
            for p in self.center_pixels[3:6]:
                pixels.extend([p and 255 or 0, ]*pixel_width)
        for i in range(pixel_width):
            for p in self.center_pixels[6:9]:
                pixels.extend([p and 255 or 0, ]*pixel_width)

        return  np.reshape(
            pixels,
            (3*pixel_width, 3*pixel_width)
        ).transpose()


# See: https://en.wikipedia.org/wiki/Box_Drawing_(Unicode_block)
BOXES = {
    # Single line
    0x2500: Box(
        Line.NONE, Line.SINGLE, Line.NONE, Line.SINGLE,
        [0, 0, 0, 1, 1, 1, 0, 0, 0]
    ),
    0x2502: Box(
        Line.SINGLE, Line.NONE, Line.SINGLE, Line.NONE,
        [0, 1, 0, 0, 1, 0, 0, 1, 0]
    ),
    0x250c: Box(
        Line.NONE, Line.SINGLE, Line.SINGLE, Line.NONE,
        [0, 0, 0, 0, 1, 1, 0, 1, 0]
    ),
    0x2510: Box(
        Line.NONE, Line.NONE, Line.SINGLE, Line.SINGLE,
        [0, 0, 0, 1, 1, 0, 0, 1, 0]
    ),
    0x2514: Box(
        Line.SINGLE, Line.SINGLE, Line.NONE, Line.NONE,
        [0, 1, 0, 0, 1, 1, 0, 0, 0]
    ),
    0x2518: Box(
        Line.SINGLE, Line.NONE, Line.NONE, Line.SINGLE,
        [0, 1, 0, 1, 1, 0, 0, 0, 0]
    ),
    0x251c: Box(
        Line.SINGLE, Line.SINGLE, Line.SINGLE, Line.NONE,
        [0, 1, 0, 0, 1, 1, 0, 1, 0]
    ),
    0x2524: Box(
        Line.SINGLE, Line.NONE, Line.SINGLE, Line.SINGLE,
        [0, 1, 0, 1, 1, 0, 0, 1, 0]
    ),
    0x252c: Box(
        Line.NONE, Line.SINGLE, Line.SINGLE, Line.SINGLE,
        [0, 0, 0, 1, 1, 1, 0, 1, 0]
    ),
    0x2534: Box(
        Line.SINGLE, Line.SINGLE, Line.NONE, Line.SINGLE,
        [0, 1, 0, 1, 1, 1, 0, 0, 0]
    ),
    0x253c: Box(
        Line.SINGLE, Line.SINGLE, Line.SINGLE, Line.SINGLE,
        [0, 1, 0, 1, 1, 1, 0, 1, 0]
    ),

    # Wide line
    0x2501: Box(
        Line.NONE, Line.WIDE, Line.NONE, Line.WIDE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x2503: Box(
        Line.WIDE, Line.NONE, Line.WIDE, Line.NONE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x250f: Box(
        Line.NONE, Line.WIDE, Line.WIDE, Line.NONE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x2513: Box(
        Line.NONE, Line.NONE, Line.WIDE, Line.WIDE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x2517: Box(
        Line.WIDE, Line.WIDE, Line.NONE, Line.NONE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x251b: Box(
        Line.WIDE, Line.NONE, Line.NONE, Line.WIDE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x2523: Box(
        Line.WIDE, Line.WIDE, Line.WIDE, Line.NONE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x252b: Box(
        Line.WIDE, Line.NONE, Line.WIDE, Line.WIDE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x2533: Box(
        Line.NONE, Line.WIDE, Line.WIDE, Line.WIDE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x253b: Box(
        Line.WIDE, Line.WIDE, Line.NONE, Line.WIDE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),
    0x254b: Box(
        Line.WIDE, Line.WIDE, Line.WIDE, Line.WIDE,
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ),

    # Double line
    0x2550: Box(
        Line.NONE, Line.DOUBLE, Line.NONE, Line.DOUBLE,
        [1, 1, 1, 0, 0, 0, 1, 1, 1]
    ),
    0x2551: Box(
        Line.DOUBLE, Line.NONE, Line.DOUBLE, Line.NONE,
        [1, 0, 1, 1, 0, 1, 1, 0, 1]
    ),
    0x2554: Box(
        Line.NONE, Line.DOUBLE, Line.DOUBLE, Line.NONE,
        [1, 1, 1, 1, 0, 0, 1, 0, 1]
    ),
    0x2557: Box(
        Line.NONE, Line.NONE, Line.DOUBLE, Line.DOUBLE,
        [1, 1, 1, 0, 0, 1, 1, 0, 1]
    ),
    0x255a: Box(
        Line.DOUBLE, Line.DOUBLE, Line.NONE, Line.NONE,
        [1, 0, 1, 1, 0, 0, 1, 1, 1]
    ),
    0x255d: Box(
        Line.DOUBLE, Line.NONE, Line.NONE, Line.DOUBLE,
        [1, 0, 1, 0, 0, 1, 1, 1, 1]
    ),
    0x2560: Box(
        Line.DOUBLE, Line.DOUBLE, Line.DOUBLE, Line.NONE,
        [1, 0, 1, 1, 0, 0, 1, 0, 1]
    ),
    0x2563: Box(
        Line.DOUBLE, Line.NONE, Line.DOUBLE, Line.DOUBLE,
        [1, 0, 1, 0, 0, 1, 1, 0, 1]
    ),
    0x2566: Box(
        Line.NONE, Line.DOUBLE, Line.DOUBLE, Line.DOUBLE,
        [1, 1, 1, 0, 0, 0, 1, 0, 1]
    ),
    0x2569: Box(
        Line.DOUBLE, Line.DOUBLE, Line.NONE, Line.DOUBLE,
        [1, 0, 1, 0, 0, 0, 1, 1, 1]
    ),
    0x256c: Box(
        Line.DOUBLE, Line.DOUBLE, Line.DOUBLE, Line.DOUBLE,
        [1, 0, 1, 0, 0, 0, 1, 0, 1]
    ),

    # Single line horizontal / double line vertical
    0x2553: Box(
        Line.NONE, Line.SINGLE, Line.DOUBLE, Line.NONE,
        [0, 0, 0, 1, 1, 1, 1, 0, 1]
    ),
    0x2556: Box(
        Line.NONE, Line.NONE, Line.DOUBLE, Line.SINGLE,
        [0, 0, 0, 1, 1, 1, 1, 0, 1]
    ),
    0x2559: Box(
        Line.DOUBLE, Line.SINGLE, Line.NONE, Line.NONE,
        [1, 0, 1, 1, 1, 1, 0, 0, 0]
    ),
    0x255c: Box(
        Line.DOUBLE, Line.NONE, Line.NONE, Line.SINGLE,
        [1, 0, 1, 1, 1, 1, 0, 0, 0]
    ),
    0x255f: Box(
        Line.DOUBLE, Line.SINGLE, Line.DOUBLE, Line.NONE,
        [1, 0, 1, 1, 0, 1, 1, 0, 1]
    ),
    0x2562: Box(
        Line.DOUBLE, Line.NONE, Line.DOUBLE, Line.SINGLE,
        [1, 0, 1, 1, 0, 1, 1, 0, 1]
    ),
    0x2565: Box(
        Line.NONE, Line.SINGLE, Line.DOUBLE, Line.SINGLE,
        [0, 0, 0, 1, 1, 1, 1, 0, 1]
    ),
    0x2568: Box(
        Line.DOUBLE, Line.SINGLE, Line.NONE, Line.SINGLE,
        [1, 0, 1, 1, 1, 1, 0, 0, 0]
    ),
    0x256b: Box(
        Line.DOUBLE, Line.SINGLE, Line.DOUBLE, Line.SINGLE,
        [1, 0, 1, 1, 1, 1, 1, 0, 1]
    ),

    # Double line horizontal / single line vertical
    0x2552: Box(
        Line.NONE, Line.DOUBLE, Line.SINGLE, Line.NONE,
        [0, 1, 1, 0, 1, 0, 0, 1, 1]
    ),
    0x2555: Box(
        Line.NONE, Line.NONE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 0, 0, 1, 0, 1, 1, 0]
    ),
    0x2558: Box(
        Line.SINGLE, Line.DOUBLE, Line.NONE, Line.NONE,
        [0, 1, 1, 0, 1, 0, 0, 1, 1]
    ),
    0x255b: Box(
        Line.SINGLE, Line.NONE, Line.NONE, Line.DOUBLE,
        [1, 1, 0, 0, 1, 0, 1, 1, 0]
    ),
    0x255e: Box(
        Line.SINGLE, Line.DOUBLE, Line.SINGLE, Line.NONE,
        [0, 1, 1, 0, 1, 0, 0, 1, 1]
    ),
    0x2561: Box(
        Line.SINGLE, Line.NONE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 0, 0, 1, 0, 1, 1, 0]
    ),
    0x2564: Box(
        Line.NONE, Line.DOUBLE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 1, 0, 0, 0, 1, 1, 1]
    ),
    0x2567: Box(
        Line.SINGLE, Line.DOUBLE, Line.NONE, Line.DOUBLE,
        [1, 1, 1, 0, 0, 0, 1, 1, 1]
    ),
    0x256a: Box(
        Line.SINGLE, Line.DOUBLE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 1, 0, 1, 0, 1, 1, 1]
    ),

}


class DynamicTiles:

    def get_box_tile(self, code_point, tile_size):
        box = BOXES.get(code_point)
        if not box:
            return None

        tile = np.zeros(tile_size, dtype=np.uint8, order="F")

        half_x = tile_size.width//2
        half_y = tile_size.height//2

        pixel_width = 1
        if tile.shape[1] > 18:
            pixel_width += 1
        line_width = 3 * pixel_width
        first_half = line_width//2
        second_half = line_width - line_width//2

        tile[:half_x, half_y-first_half:half_y+second_half] = box.left(pixel_width)
        tile[half_x:, half_y-first_half:half_y+second_half] = box.right(pixel_width)

        tile[half_x-first_half:half_x+second_half, :half_y] = box.top(pixel_width)
        tile[half_x-first_half:half_x+second_half, half_y:] = box.bottom(pixel_width)

        tile[half_x-first_half:half_x+second_half, half_y-first_half:half_y+second_half] = box.center(pixel_width)

        return tile.transpose()


    def get_tile(self, code_point, tile_size):
        return self.get_box_tile(code_point, tile_size)
