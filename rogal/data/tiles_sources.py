from ..geometry import Size

from ..tiles_sources.tilesheets import Tilesheet
from ..tiles_sources.fonts import TrueTypeFont
from ..tiles_sources.block_elements import BlockElements
from ..tiles_sources.box_drawing import BoxDrawing


class TilesSourcesParser:

    def __init__(self, charsets):
        self.charsets = charsets

    def __call__(self, data):
        if 'tilesheet' in data:
            return Tilesheet(
                data['tilesheet'],
                data['columns'],
                data['rows'],
                self.charsets.get(data['charset']),
            )
        if 'ttf' in data:
            size = data['size']
            if isinstance(size, (tuple, list)):
                size = Size(*size)
            return TrueTypeFont(
                data['ttf'],
                size,
                self.charsets.parse(data['charset']),
            )
        if data.get('generator') == 'BlockElements':
            return BlockElements(
                self.charsets.parse(data['charset']),
            )
        if data.get('generator') == 'BoxDrawing':
            return BoxDrawing(
                self.charsets.parse(data['charset']),
            )

