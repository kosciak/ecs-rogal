from .core import Glyph


class Charset(tuple):

    """Sequence of Glyphs."""

    __slots__ = ()

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

