from ..data import data_store, parsers

from .core import Align, Padding
from .core import Glyph, Colors
from .charsets import Charset, UnicodeBlock


def parse_glyph(data):
    return Glyph(data)


class GlyphsParser:

    def parse_glyphs_sequence(self, data):
        return [parsers.parse_glyph(glyph) for glyph in data]


class GlyphsSequenceParser(GlyphsParser):

    def __call__(self, data):
        return self.parse_glyphs_sequence(data)


class FramesSequenceParser(GlyphsParser):

    def __call__(self, data):
        frames = [str(frame) for frame in self.parse_glyphs_sequence(data)]
        return frames



class CharsetsParser(GlyphsParser):

    def __call__(self, data):
        if 'code_points' in data:
            return Charset(data['code_points'])
        elif 'glyphs' in data:
            return self.parse_glyphs_sequence(data['glyphs'])
        elif 'from' in data and 'to' in data:
            return UnicodeBlock(
                data['from'],
                data['to']
            )


def parse_align(data):
    return getattr(Align, data.upper())


def parse_padding(data):
    if isinstance(data, str):
        data = [int(value.strip() or 0) for value in data.split(',')]
    if isinstance(data, int):
        return Padding(data)
    if isinstance(data, (list, tuple)):
        return Padding(*data)
    if isinstance(data, dict):
        return Padding(**data)


def parse_colors(data):
    fg = data.get('fg')
    bg = data.get('bg')
    return Colors(fg, bg)


data_store.register('glyphs', parse_glyph)
data_store.register('charsets', CharsetsParser())

parsers.register('glyph', data_store.glyphs.parse)
parsers.register('charset', data_store.charsets.parse)
parsers.register('glyphs_sequence', GlyphsSequenceParser())
parsers.register('frames_sequence', FramesSequenceParser())

