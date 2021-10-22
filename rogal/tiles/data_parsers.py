from .core import Glyph
from .charsets import Charset, UnicodeBlock


def parse_glyph(data):
    return Glyph(data)


class GlyphsParser:

    def __init__(self, glyphs):
        self.glyphs = glyphs

    def parse_glyphs_sequence(self, data):
        return [self.glyphs.parse(glyph) for glyph in data]


class GlyphsSequenceParser(GlyphsParser):

    def __call__(self, data):
        return self.parse_glyphs_sequence(data)


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

