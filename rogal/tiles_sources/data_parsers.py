from ..geometry import Size

from ..data import data_store, parsers

from .tilesheets import Tilesheet
from .fonts import TrueTypeFont
from .block_elements import BlockElements
from .box_drawing import BoxDrawing


def parse_tilesheet(data):
    return Tilesheet(
        data['tilesheet'],
        data['columns'],
        data['rows'],
        parsers.parse_charset(data['charset']),
    )

def parse_ttf(data):
    size = data['size']
    if isinstance(size, (tuple, list)):
        size = Size(*size)
    return TrueTypeFont(
        data['ttf'],
        size,
        parsers.parse_charset(data['charset']),
    )

def parse_tiles_generator(data):
    if data['generator'] == 'BlockElements':
        return BlockElements(
            parsers.parse_charset(data['charset']),
        )
    if data['generator'] == 'BoxDrawing':
        return BoxDrawing(
            parsers.parse_charset(data['charset']),
        )

def parse_tiles_source(data):
    if 'tilesheet' in data:
        return parsers.parse_tilesheet(data)

    if 'ttf' in data:
        return parsers.parse_ttf(data)

    if 'generator' in data:
        return parsers.parse_tiles_generator(data)


data_store.register('tiles_sources', parse_tiles_source)

parsers.register('tilesheet', parse_tilesheet)
parsers.register('ttf', parse_ttf)
parsers.register('tiles_generator', parse_tiles_generator)
parsers.register('tiles_source', data_store.tiles_sources.parse)

