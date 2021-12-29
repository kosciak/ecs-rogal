import functools


FOREGROUND_NAMES = {'FG', 'FOREGROUND', }
BACKGROUND_NAMES = {'BG', 'BACKGROUND', }


class ColorsManager:

    """Manage Color palettes and color names aliases."""

    def __init__(self, palette, aliases=None):
        self._palette = palette
        self.aliases = aliases or {} # {alias name: palette's name}

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, palette):
        self._palette = palette
        self.get.cache_clear()

    @functools.lru_cache(maxsize=None)
    def get(self, color):
        """Return color by palette's name, or by color alias name."""
        if color is None:
            return None

        # NOTE: color.upper() to make color aliases keys case insensitive
        if type(color) == str:
            color = color.upper()
        color = self.aliases.get(color, color)

        if color in FOREGROUND_NAMES:
            return self.palette.fg

        if color in BACKGROUND_NAMES:
            return self.palette.bg

        return self.palette.get(color)

