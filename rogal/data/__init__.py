from .core import Data
from .charsets import parse_charset, parse_unicode_block
from .symbols import parse_symbol, SymbolsListParser
from .tilesheets import TilesheetParser


Charsets = Data(parse_charset)

UnicodeBlocks = Data(parse_unicode_block)

Symbols = Data(parse_symbol)

Bitmasks = Data(SymbolsListParser(Symbols))

Decorations = Data(SymbolsListParser(Symbols))

Tilesheets = Data(TilesheetParser(Charsets))


DATA = {
    'Charsets': Charsets,
    'UnicodeBlocks': UnicodeBlocks,
    'Symbols': Symbols,
    'Bitmasks': Bitmasks,
    'Decorations': Decorations,
    'Tilesheets': Tilesheets,
}


def register_data(**kwargs):
    for name, loader in kwargs.items():
        name = name.title().replace('_', '')
        data = DATA.get(name)
        data.register(loader)


__all__ = ['register_data', ]
__all__.extend(DATA.keys())

