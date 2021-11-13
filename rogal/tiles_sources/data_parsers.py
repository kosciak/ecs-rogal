from ..geometry import Size

from ..data import data_store, parsers

from .tilesheets import Tilesheet
from .fonts import TrueTypeFont
from .block_elements import BlockElements
from .box_drawing import BoxDrawing


class TilesSourcesParser:

    def parse_tilesheet(self, data):
        return Tilesheet(
            data['tilesheet'],
            data['columns'],
            data['rows'],
            parsers.parse_charset(data['charset']),
        )

    def parse_ttf(self, data):
        size = data['size']
        if isinstance(size, (tuple, list)):
            size = Size(*size)
        return TrueTypeFont(
            data['ttf'],
            size,
            parsers.parse_charset(data['charset']),
        )

    def parse_tiles_generator(self, data):
        if data['generator'] == 'BlockElements':
            return BlockElements(
                parsers.parse_charset(data['charset']),
            )
        if data['generator'] == 'BoxDrawing':
            return BoxDrawing(
                parsers.parse_charset(data['charset']),
            )

    def __call__(self, data):
        if 'tilesheet' in data:
            return self.parse_tilesheet(data)

        if 'ttf' in data:
            return self.parse_ttf(data)

        if 'generator' in data:
            return self.parse_tiles_generator(data)


data_store.register('tiles_sources', TilesSourcesParser())

parsers.register('tiles_source', data_store.tiles_sources.parse)

