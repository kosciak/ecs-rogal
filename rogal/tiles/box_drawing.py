import collections
from enum import IntFlag

import numpy as np

from .tiles_source import TilesSource


class Line(IntFlag):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2
    WIDE = SINGLE | DOUBLE


Box = collections.namedtuple(
    'Box', [
        'top',
        'right',
        'bottom',
        'left',
        'center', # 3x3 pixels in center, tried generating from Lines, but it was a mess...
    ])

# See: https://en.wikipedia.org/wiki/Box_Drawing_(Unicode_block)
BOXES = {
    # Single line
    0x2500: Box(
        Line.NONE, Line.SINGLE, Line.NONE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 1,
         0, 0, 0]
    ),
    0x2502: Box(
        Line.SINGLE, Line.NONE, Line.SINGLE, Line.NONE,
        [0, 1, 0,
         0, 1, 0,
         0, 1, 0]
    ),
    0x250c: Box(
        Line.NONE, Line.SINGLE, Line.SINGLE, Line.NONE,
        [0, 0, 0,
         0, 1, 1,
         0, 1, 0]
    ),
    0x2510: Box(
        Line.NONE, Line.NONE, Line.SINGLE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 0,
         0, 1, 0]
    ),
    0x2514: Box(
        Line.SINGLE, Line.SINGLE, Line.NONE, Line.NONE,
        [0, 1, 0,
         0, 1, 1,
         0, 0, 0]
    ),
    0x2518: Box(
        Line.SINGLE, Line.NONE, Line.NONE, Line.SINGLE,
        [0, 1, 0,
         1, 1, 0,
         0, 0, 0]
    ),
    0x251c: Box(
        Line.SINGLE, Line.SINGLE, Line.SINGLE, Line.NONE,
        [0, 1, 0,
         0, 1, 1,
         0, 1, 0]
    ),
    0x2524: Box(
        Line.SINGLE, Line.NONE, Line.SINGLE, Line.SINGLE,
        [0, 1, 0,
         1, 1, 0,
         0, 1, 0]
    ),
    0x252c: Box(
        Line.NONE, Line.SINGLE, Line.SINGLE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 1,
         0, 1, 0]
    ),
    0x2534: Box(
        Line.SINGLE, Line.SINGLE, Line.NONE, Line.SINGLE,
        [0, 1, 0,
         1, 1, 1,
         0, 0, 0]
    ),
    0x253c: Box(
        Line.SINGLE, Line.SINGLE, Line.SINGLE, Line.SINGLE,
        [0, 1, 0,
         1, 1, 1,
         0, 1, 0]
    ),

    # Wide line
    0x2501: Box(
        Line.NONE, Line.WIDE, Line.NONE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2503: Box(
        Line.WIDE, Line.NONE, Line.WIDE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x250f: Box(
        Line.NONE, Line.WIDE, Line.WIDE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2513: Box(
        Line.NONE, Line.NONE, Line.WIDE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2517: Box(
        Line.WIDE, Line.WIDE, Line.NONE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x251b: Box(
        Line.WIDE, Line.NONE, Line.NONE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2523: Box(
        Line.WIDE, Line.WIDE, Line.WIDE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x252b: Box(
        Line.WIDE, Line.NONE, Line.WIDE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2533: Box(
        Line.NONE, Line.WIDE, Line.WIDE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x253b: Box(
        Line.WIDE, Line.WIDE, Line.NONE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x254b: Box(
        Line.WIDE, Line.WIDE, Line.WIDE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),

    # Double line
    0x2550: Box(
        Line.NONE, Line.DOUBLE, Line.NONE, Line.DOUBLE,
        [1, 1, 1,
         0, 0, 0,
         1, 1, 1]
    ),
    0x2551: Box(
        Line.DOUBLE, Line.NONE, Line.DOUBLE, Line.NONE,
        [1, 0, 1,
         1, 0, 1,
         1, 0, 1]
    ),
    0x2554: Box(
        Line.NONE, Line.DOUBLE, Line.DOUBLE, Line.NONE,
        [1, 1, 1,
         1, 0, 0,
         1, 0, 1]
    ),
    0x2557: Box(
        Line.NONE, Line.NONE, Line.DOUBLE, Line.DOUBLE,
        [1, 1, 1,
         0, 0, 1,
         1, 0, 1]
    ),
    0x255a: Box(
        Line.DOUBLE, Line.DOUBLE, Line.NONE, Line.NONE,
        [1, 0, 1,
         1, 0, 0,
         1, 1, 1]
    ),
    0x255d: Box(
        Line.DOUBLE, Line.NONE, Line.NONE, Line.DOUBLE,
        [1, 0, 1,
         0, 0, 1,
         1, 1, 1]
    ),
    0x2560: Box(
        Line.DOUBLE, Line.DOUBLE, Line.DOUBLE, Line.NONE,
        [1, 0, 1,
         1, 0, 0,
         1, 0, 1]
    ),
    0x2563: Box(
        Line.DOUBLE, Line.NONE, Line.DOUBLE, Line.DOUBLE,
        [1, 0, 1,
         0, 0, 1,
         1, 0, 1]
    ),
    0x2566: Box(
        Line.NONE, Line.DOUBLE, Line.DOUBLE, Line.DOUBLE,
        [1, 1, 1,
         0, 0, 0,
         1, 0, 1]
    ),
    0x2569: Box(
        Line.DOUBLE, Line.DOUBLE, Line.NONE, Line.DOUBLE,
        [1, 0, 1,
         0, 0, 0,
         1, 1, 1]
    ),
    0x256c: Box(
        Line.DOUBLE, Line.DOUBLE, Line.DOUBLE, Line.DOUBLE,
        [1, 0, 1,
         0, 0, 0,
         1, 0, 1]
    ),

    # Single line horizontal / double line vertical
    0x2553: Box(
        Line.NONE, Line.SINGLE, Line.DOUBLE, Line.NONE,
        [0, 0, 0,
         1, 1, 1,
         1, 0, 1]
    ),
    0x2556: Box(
        Line.NONE, Line.NONE, Line.DOUBLE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 1,
         1, 0, 1]
    ),
    0x2559: Box(
        Line.DOUBLE, Line.SINGLE, Line.NONE, Line.NONE,
        [1, 0, 1,
         1, 1, 1,
         0, 0, 0]
    ),
    0x255c: Box(
        Line.DOUBLE, Line.NONE, Line.NONE, Line.SINGLE,
        [1, 0, 1,
         1, 1, 1,
         0, 0, 0]
    ),
    0x255f: Box(
        Line.DOUBLE, Line.SINGLE, Line.DOUBLE, Line.NONE,
        [1, 0, 1,
         1, 0, 1,
         1, 0, 1]
    ),
    0x2562: Box(
        Line.DOUBLE, Line.NONE, Line.DOUBLE, Line.SINGLE,
        [1, 0, 1,
         1, 0, 1,
         1, 0, 1]
    ),
    0x2565: Box(
        Line.NONE, Line.SINGLE, Line.DOUBLE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 1,
         1, 0, 1]
    ),
    0x2568: Box(
        Line.DOUBLE, Line.SINGLE, Line.NONE, Line.SINGLE,
        [1, 0, 1,
         1, 1, 1,
         0, 0, 0]
    ),
    0x256b: Box(
        Line.DOUBLE, Line.SINGLE, Line.DOUBLE, Line.SINGLE,
        [1, 0, 1,
         1, 1, 1,
         1, 0, 1]
    ),

    # Double line horizontal / single line vertical
    0x2552: Box(
        Line.NONE, Line.DOUBLE, Line.SINGLE, Line.NONE,
        [0, 1, 1,
         0, 1, 0,
         0, 1, 1]
    ),
    0x2555: Box(
        Line.NONE, Line.NONE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 0,
         0, 1, 0,
         1, 1, 0]
    ),
    0x2558: Box(
        Line.SINGLE, Line.DOUBLE, Line.NONE, Line.NONE,
        [0, 1, 1,
         0, 1, 0,
         0, 1, 1]
    ),
    0x255b: Box(
        Line.SINGLE, Line.NONE, Line.NONE, Line.DOUBLE,
        [1, 1, 0,
         0, 1, 0,
         1, 1, 0]
    ),
    0x255e: Box(
        Line.SINGLE, Line.DOUBLE, Line.SINGLE, Line.NONE,
        [0, 1, 1,
         0, 1, 0,
         0, 1, 1]
    ),
    0x2561: Box(
        Line.SINGLE, Line.NONE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 0,
         0, 1, 0,
         1, 1, 0]
    ),
    0x2564: Box(
        Line.NONE, Line.DOUBLE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 1,
         0, 0, 0,
         1, 1, 1]
    ),
    0x2567: Box(
        Line.SINGLE, Line.DOUBLE, Line.NONE, Line.DOUBLE,
        [1, 1, 1,
         0, 0, 0,
         1, 1, 1]
    ),
    0x256a: Box(
        Line.SINGLE, Line.DOUBLE, Line.SINGLE, Line.DOUBLE,
        [1, 1, 1,
         0, 1, 0,
         1, 1, 1]
    ),

    # Single line horizontal / wide line vertical
    0x250e: Box(
        Line.NONE, Line.SINGLE, Line.WIDE, Line.NONE,
        [0, 0, 0,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2512: Box(
        Line.NONE, Line.NONE, Line.WIDE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2516: Box(
        Line.WIDE, Line.SINGLE, Line.NONE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         0, 0, 0]
    ),
    0x251a: Box(
        Line.WIDE, Line.NONE, Line.NONE, Line.SINGLE,
        [1, 1, 1,
         1, 1, 1,
         0, 0, 0]
    ),
    0x2520: Box(
        Line.WIDE, Line.SINGLE, Line.WIDE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2528: Box(
        Line.WIDE, Line.NONE, Line.WIDE, Line.SINGLE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2530: Box(
        Line.NONE, Line.SINGLE, Line.WIDE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2538: Box(
        Line.WIDE, Line.SINGLE, Line.NONE, Line.SINGLE,
        [1, 1, 1,
         1, 1, 1,
         0, 0, 0]
    ),
    0x2542: Box(
        Line.WIDE, Line.SINGLE, Line.WIDE, Line.SINGLE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),

    # Wide line horizontal / single line vertical
    0x250d: Box(
        Line.NONE, Line.WIDE, Line.SINGLE, Line.NONE,
        [0, 1, 1,
         0, 1, 1,
         0, 1, 1]
    ),
    0x2511: Box(
        Line.NONE, Line.NONE, Line.SINGLE, Line.WIDE,
        [1, 1, 0,
         0, 1, 1,
         1, 1, 0]
    ),
    0x2515: Box(
        Line.SINGLE, Line.WIDE, Line.NONE, Line.NONE,
        [0, 1, 1,
         0, 1, 1,
         0, 1, 1]
    ),
    0x2519: Box(
        Line.SINGLE, Line.NONE, Line.NONE, Line.WIDE,
        [1, 1, 0,
         1, 1, 0,
         1, 1, 0]
    ),
    0x251d: Box(
        Line.SINGLE, Line.WIDE, Line.SINGLE, Line.NONE,
        [0, 1, 1,
         0, 1, 1,
         0, 1, 1]
    ),
    0x2525: Box(
        Line.SINGLE, Line.NONE, Line.SINGLE, Line.WIDE,
        [1, 1, 0,
         1, 1, 0,
         1, 1, 0]
    ),
    0x252f: Box(
        Line.NONE, Line.WIDE, Line.SINGLE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2537: Box(
        Line.SINGLE, Line.WIDE, Line.NONE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x253f: Box(
        Line.SINGLE, Line.WIDE, Line.SINGLE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),

    # Single ends
    0x2574: Box(
        Line.NONE, Line.NONE, Line.NONE, Line.SINGLE,
        [0, 0, 0,
         1, 1, 0,
         0, 0, 0]
    ),
    0x2575: Box(
        Line.SINGLE, Line.NONE, Line.NONE, Line.NONE,
        [0, 1, 0,
         0, 1, 0,
         0, 0, 0]
    ),
    0x2576: Box(
        Line.NONE, Line.SINGLE, Line.NONE, Line.NONE,
        [0, 0, 0,
         0, 1, 1,
         0, 0, 0]
    ),
    0x2577: Box(
        Line.NONE, Line.NONE, Line.SINGLE, Line.NONE,
        [0, 0, 0,
         0, 1, 0,
         0, 1, 0]
    ),

    # Wide ends
    0x2578: Box(
        Line.NONE, Line.NONE, Line.NONE, Line.WIDE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x2579: Box(
        Line.WIDE, Line.NONE, Line.NONE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x257a: Box(
        Line.NONE, Line.WIDE, Line.NONE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),
    0x257b: Box(
        Line.NONE, Line.NONE, Line.WIDE, Line.NONE,
        [1, 1, 1,
         1, 1, 1,
         1, 1, 1]
    ),

    # TODO: Rest of the Unicode block, or at least single / wide, wide / single

}


class BoxDrawing(TilesSource):

    def __init__(self, charset=None):
        if not charset:
            charset = BOXES.keys()
        super().__init__(charset)

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

    def horizontal(self, line, pixel_width=1):
        return self._line_pixels(line, pixel_width)

    def vertical(self, line, pixel_width=1):
        return np.reshape(
            self._line_pixels(line, pixel_width),
            (3*pixel_width, 1)
        )

    def center(self, box, pixel_width=1):
        pixels = []

        for i in range(pixel_width):
            for e in box.center[0:3]:
                pixels.extend([e and 255 or 0, ]*pixel_width)
        for i in range(pixel_width):
            for e in box.center[3:6]:
                pixels.extend([e and 255 or 0, ]*pixel_width)
        for i in range(pixel_width):
            for e in box.center[6:9]:
                pixels.extend([e and 255 or 0, ]*pixel_width)

        return  np.reshape(
            pixels,
            (3*pixel_width, 3*pixel_width)
        ).transpose()

    def get_tile(self, code_point, tile_size):
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
        first = line_width//2
        second = line_width - line_width//2

        tile[:half_x, half_y-first:half_y+second] = self.horizontal(box.left, pixel_width)
        tile[half_x:, half_y-first:half_y+second] = self.horizontal(box.right, pixel_width)

        tile[half_x-first:half_x+second, :half_y] = self.vertical(box.top, pixel_width)
        tile[half_x-first:half_x+second, half_y:] = self.vertical(box.bottom, pixel_width)

        tile[half_x-first:half_x+second, half_y-first:half_y+second] = self.center(box, pixel_width)

        return tile.transpose()

