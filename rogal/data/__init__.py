from .core import Data
from .loaders import DataLoader

from ..tiles.data_parsers import parse_glyph, GlyphsSequenceParser, CharsetsParser
from ..tiles_sources.data_parsers import TilesSourcesParser
from ..colors.data_parsers import parse_color_list, parse_color_names, ColorPaletteParser


Glyphs = Data(parse_glyph)

Charsets = Data(CharsetsParser(Glyphs))

Bitmasks = Data(GlyphsSequenceParser(Glyphs))

Decorations = Data(GlyphsSequenceParser(Glyphs))

TilesSources = Data(TilesSourcesParser(Charsets))

ColorLists = Data(parse_color_list)

ColorNames = Data(parse_color_names)

ColorPalettes = Data(ColorPaletteParser(ColorLists, ColorNames))


DATA = {
    'Charsets': Charsets,
    'Glyphs': Glyphs,
    'Bitmasks': Bitmasks,
    'Decorations': Decorations,
    'TilesSources': TilesSources,
    'ColorLists': ColorLists,
    'ColorNames': ColorNames,
    'ColorPalettes': ColorPalettes,
}


def register_data(**kwargs):
    if 'data' in kwargs:
        data = kwargs.pop('data')
        loader = DataLoader(data)
        kwargs.update(loader.load())

    for name, loader in kwargs.items():
        name = name.title().replace('_', '')
        data = DATA.get(name)
        if isinstance(loader, (list, tuple)):
            for l in loader:
                data.register(l)
        else:
            data.register(loader)


__all__ = ['register_data', ]
__all__.extend(DATA.keys())

