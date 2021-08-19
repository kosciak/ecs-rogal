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


# DEJA_VU_SANS_MONO_11_TTF = TrueTypeFont(
#     '/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf',
#     # '/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono-Bold.ttf',
#     # '/usr/share/fonts/google-droid-sans-mono-fonts/DroidSansMono.ttf',
#     # '/usr/share/fonts/gdouros-symbola/Symbola.ttf',
#     # '/home/kosciak/.local/share/fonts/comic-sans-ms_[pl.allfont.net].ttf',
#     11,
#     Charsets.CP437,
# )
