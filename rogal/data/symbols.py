from ..tiles.core import Glyph


def parse_symbol(code_point):
    return Glyph(code_point)


class SymbolsListParser:

    def __init__(self, symbols):
        self.symbols = symbols

    def __call__(self, data):
        return [self.symbols.get(symbol) or Glyph(symbol) for symbol in data]

