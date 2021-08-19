from .core import Data
from .charsets import parse_charset
from .symbols import parse_symbol, SymbolsListParser
from .tilesheets import TilesheetParser


Charsets = Data(parse_charset)

Symbols = Data(parse_symbol)

Bitmasks = Data(SymbolsListParser(Symbols))

Decorations = Data(SymbolsListParser(Symbols))

Tilesheets = Data(TilesheetParser(Charsets))


DATA = {
    'Charsets': Charsets,
    'Symbols': Symbols,
    'Bitmasks': Bitmasks,
    'Decorations': Decorations,
    'Tilesheets': Tilesheets,
}


def register_data(**kwargs):
    for name, loader in kwargs.items():
        data = DATA.get(name.title())
        data.register(loader)


__all__ = ['register_data', ]
__all__.extend(DATA.keys())

