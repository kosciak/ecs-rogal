
class Pool:

    __slots__ = ('_value', 'max_value', )

    def __init__(self, value, max_value=None):
        self._value = 0
        value = int(value)
        max_value = max_value and int(max_value)
        self.max_value = max_value or value
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = max(0, min(value, self.max_value))

    def __iadd__(self, value):
        self._value += int(value)
        return self

    def __isub__(self, value):
        self._value -= int(value)
        return self

    def __int__(self):
        return self.value


class Attribute:

    __slots__ = ('base', 'modifier')

    def __init__(self, base, modifier=None):
        self.base = base
        self.modifier = modifier or 0

    @property
    def total(self):
        return self.base + self.modifier

    def __int__(self):
        return self.total

