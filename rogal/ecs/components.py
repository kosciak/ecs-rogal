import functools

from .core import Component, Entity, EntitiesSet


"""Common Component types."""


class Singleton:
    __slots__ = ()

    _INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if not cls._INSTANCE:
            cls._INSTANCE = super().__new__(cls, *args, **kwargs)
        return cls._INSTANCE


class IntComponent(Component, int):
    __slots__ = ()

    def __new__(cls, value):
        return super().__new__(cls, int(value))


class BoolComponent(IntComponent):
    __slots__ = ()

    def __new__(cls, value):
        return super().__new__(cls, bool(value))

    def __repr__(self):
        return f'<{self.name}={bool(self)}>'


class FloatComponent(Component, float):
    __slots__ = ()

    def __new__(cls, value):
        return super().__new__(cls, float(value))


@functools.total_ordering
class CounterComponent(Component):

    """Single value component that can be incremented/decremented, and compared to other values.

    Just change value without the need of reinserting changed value to manager (as with IntComponent)

    """

    __slots__ = ('value', )

    def __init__(self, value):
        self.value = int(value)

    def __int__(self):
        return self.value

    def __iadd__(self, value):
        self.value += value
        return self

    def __isub__(self, value):
        self.value -= value
        return self

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

    def __repr__(self):
        return f'<{self.name}={self.value!r}>'


def Flag(name):
    """Returns BoolComponent instance of class with given name."""
    bases = (Singleton, BoolComponent, )
    attrs = dict(
        __slots__=(),
        __call__=lambda self, *args, **kwargs: self,
    )
    return type(name, bases, attrs)(True)


def IntFlag(name, value):
    """Returns IntComponent instance of class with given name."""
    bases = (Singleton, IntComponent, )
    attrs = dict(
        __slots__=(),
        __call__=lambda self, *args, **kwargs: self,
    )
    return type(name, bases, attrs)(value)


def _type_factory(name, bases):
    """Returns class with given name, inheriting from bases."""
    attrs = dict(
        __slots__=(),
    )
    return type(name, bases, attrs)

def component_type(*bases):
    """Component type factory."""
    return functools.partial(_type_factory, bases=bases)


Int = component_type(IntComponent)
Bool = component_type(IntComponent)
Float = component_type(IntComponent)
String = component_type(Component, str)
List = component_type(Component, list)
Set = component_type(Component, set)

EntityReference = component_type(Component, Entity)
EntitiesRefs = component_type(Component, EntitiesSet)

Counter = component_type(CounterComponent)

