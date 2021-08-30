from ..data_loaders import DataLoader

from .core import Data
from .charsets import parse_charset
from .symbols import parse_symbol, SymbolsListParser
from .tilesheets import TilesheetParser
from .colors import parse_colors, parse_color_names, ColorPaletteParser


Charsets = Data(parse_charset)

Symbols = Data(parse_symbol)

Bitmasks = Data(SymbolsListParser(Symbols))

Decorations = Data(SymbolsListParser(Symbols))

Tilesheets = Data(TilesheetParser(Charsets))

Colors = Data(parse_colors)

ColorNames = Data(parse_color_names)

ColorPalettes = Data(ColorPaletteParser(Colors, ColorNames))


DATA = {
    'Charsets': Charsets,
    'Symbols': Symbols,
    'Bitmasks': Bitmasks,
    'Decorations': Decorations,
    'Tilesheets': Tilesheets,
    'Colors': Colors,
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

