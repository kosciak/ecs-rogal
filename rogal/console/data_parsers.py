from ..data import data_store, parsers

from .core import Align, Padding
from .core import Glyph, Colors
from .charsets import Charset, UnicodeBlock


def parse_glyph(data):
    return Glyph(data)


def parse_glyphs_sequence(data):
    if data is None:
        return None
    return [parsers.parse_glyph(glyph) for glyph in data]


def parse_frames_sequence(data):
    if data is None:
        return None
    frames = [str(frame) for frame in parsers.parse_glyphs_sequence(data)]
    return frames


def parse_charset(data):
    if 'code_points' in data:
        return Charset(data['code_points'])
    elif 'glyphs' in data:
        return parsers.parse_glyphs_sequence(data['glyphs'])
    elif 'from' in data and 'to' in data:
        return UnicodeBlock(
            data['from'],
            data['to']
        )


def parse_align(data):
    if data is None:
        return None
    return getattr(Align, data.upper())


def parse_padding(data):
    if data is None:
        return None
    if isinstance(data, str):
        data = [int(value.strip() or 0) for value in data.split(',')]
    if isinstance(data, int):
        return Padding(data)
    if isinstance(data, (list, tuple)):
        return Padding(*data)
    if isinstance(data, dict):
        padding = dict(
            top=0, right=0, bottom=0, left=0,
        )
        padding.update(data)
        return Padding(**padding)


def parse_colors(data):
    if data is None:
        return None
    if isinstance(data, dict):
        fg = data.get('fg')
        bg = data.get('bg')
    if isinstance(data, (list, tuple)):
        fg = data[0]
        bg = None
        if len(data) > 1:
            bg = data[1]
    return Colors(fg, bg)


data_store.register('glyphs', parse_glyph)
data_store.register('charsets', parse_charset)

parsers.register('glyph', data_store.glyphs.parse)
parsers.register('charset', data_store.charsets.parse)
parsers.register('glyphs_sequence', parse_glyphs_sequence)
parsers.register('frames_sequence', parse_frames_sequence)
parsers.register('align', parse_align)
parsers.register('padding', parse_padding)
parsers.register('colors', parse_colors)

