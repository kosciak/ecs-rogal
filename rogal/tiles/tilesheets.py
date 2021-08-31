import collections
import os.path


ASSETS_DIR = 'assets'
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')


class TrueTypeFont(collections.namedtuple(
    'TrueTypeFont', [
        'path',
        'size',
        'charset',
    ])):

    __slots__ = ()


class Tilesheet(collections.namedtuple(
    'Tilesheet', [
        'path',
        'columns',
        'rows',
        'charset',
    ])):

    __slots__ = ()

