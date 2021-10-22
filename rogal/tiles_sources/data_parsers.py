from ..geometry import Size

from .tilesheets import Tilesheet
from .fonts import TrueTypeFont
from .block_elements import BlockElements
from .box_drawing import BoxDrawing


class TilesSourcesParser:

    def __init__(self, charsets):
        self.charsets = charsets

    def parse_tilesheet(self, data):
        return Tilesheet(
            data['tilesheet'],
            data['columns'],
            data['rows'],
            self.charsets.get(data['charset']),
        )

    def parse_ttf(self, data):
        size = data['size']
        if isinstance(size, (tuple, list)):
            size = Size(*size)
        return TrueTypeFont(
            data['ttf'],
            size,
            self.charsets.parse(data['charset']),
        )

    def parse_tiles_generator(self, data):
        if data['generator'] == 'BlockElements':
            return BlockElements(
                self.charsets.parse(data['charset']),
            )
        if data['generator'] == 'BoxDrawing':
            return BoxDrawing(
                self.charsets.parse(data['charset']),
            )

    def __call__(self, data):
        if 'tilesheet' in data:
            return self.parse_tilesheet(data)

        if 'ttf' in data:
            return self.parse_ttf(data)

        if 'generator' in data:
            return self.parse_tiles_generator(data)

