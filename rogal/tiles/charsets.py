from .core import Glyph


class Charset(tuple):

    def __new__(cls, code_points):
        return super().__new__(
            cls,
            (Glyph(code_point) for code_point in code_points)
        )

    def __contain__(self, code_point):
        if isinstance(code_point, str):
            code_point = ord(code_point)
        return code_point in self


class UnicodeBlock(Charset):

    __slots__ = ()

    def __new__(cls, start, end):
        return super().__new__(cls, range(start, end+1))


def show_charset(*charsets, columns=16):
    characters = []
    for charset in charsets:
        for code_point in charset:
            char = chr(code_point or 32)
            characters.append(char)
            if len(characters) == columns:
                print(' '.join(characters))
                characters = []

    if characters:
        print(' '.join(characters))


# TODO: Move to data/unicode_blocks.yaml ?
# Unicode blocks - just some interesting blocks that might come handy
UNICODE_BASIC_LATIN =       UnicodeBlock(0x0000, 0x007f)

UNICODE_CURRENCY_SYMBOLS =  UnicodeBlock(0x20a0, 0x20cf)

UNICODE_ARROWS =            UnicodeBlock(0x2190, 0x21ff)

UNICODE_BOX_DRAWING =       UnicodeBlock(0x2500, 0x257f)
UNICODE_BLOCK_ELEMENTS =    UnicodeBlock(0x2580, 0x259f)
UNICODE_GEOMETRIC_SHAPES =  UnicodeBlock(0x25a0, 0x25ff)
UNICODE_MISC_SYMBOLS =      UnicodeBlock(0x2600, 0x26ff)
UNICODE_DINGBATS =          UnicodeBlock(0x2700, 0x27bf)

UNICODE_BRAILLE_PATTERNS =  UnicodeBlock(0x2800, 0x28ff)

