from ..tiles_sources.tilesheets import Tilesheet
from ..tiles_sources.fonts import TrueTypeFont


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
            return TrueTypeFont(
                data['ttf'],
                data['size'],
                self.charsets.get(data['charset']),
            )

