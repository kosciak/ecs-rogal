import collections


class Tilesheet(collections.namedtuple(
    'Tilesheet', [
        'path',
        'columns',
        'rows',
        'charset',
    ])):

    __slots__ = ()

    is_tilesheet = True

