import collections


class Colors(collections.namedtuple(
    'Colors', [
        'fg',
        'bg',
    ])):

    def __new__(cls, fg=None, bg=None):
        if not (fg or bg):
            return None
        return super().__new__(cls, fg, bg)

    def invert(self):
        return Colors(self.bg, self.fg)


class Character:

    __slots__ = ('code_point', )

    __INSTANCES = {}

    def __new__(cls, code_point):
        if isinstance(code_point, Character):
            return code_point
        if isinstance(code_point, str):
            code_point = ord(code_point)
        instance = cls.__INSTANCES.get(code_point)
        if not instance:
            instance = super().__new__(cls)
            instance.code_point = code_point
            cls.__INSTANCES[code_point] = instance
        return instance

    @property
    def char(self):
        return chr(self.code_point)

    def __str__(self):
        return self.char

    def __repr__(self):
        return f'<Character {self.code_point} = "{self.char}">'


class Tile(collections.namedtuple(
    'Tile', [
        'character',
        'colors',
    ])):

    @property
    def char(self):
        return self.character.char

    @property
    def code_point(self):
        return self.character.code_point

    @property
    def fg(self):
        return self.colors.fg

    @property
    def bg(self):
        return self.colors.bg

    @staticmethod
    def create(char, fg, bg=None):
        return Tile(Character(char), Colors(fg, bg))

