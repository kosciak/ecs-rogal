import collections
import functools
import logging
import uuid

from .utils import perf


log = logging.getLogger(__name__)


class Entity(int):

    """Entity is just and integer ID."""

    __slots__ = ()

    def __new__(cls, entity_id=None):
        if entity_id is None:
            entity_id = uuid.uuid4().int
        return super().__new__(cls, entity_id)

    @property
    def short_id(self):
        hex = '%032x' % self
        return hex[:8]

    def __str__(self):
        return self.short_id

    def __repr__(self):
        hex = '%032x' % self
        return '<Entity id="%s-%s-%s-%s-%s">' % (
            hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])


class Component:

    """Component that hold some value(s).

    params - values that are used by constructor and serialization

    """

    __slots__ = ()
    params = None

    @property
    def name(self):
        return f'{self.__class__.__name__}'

    @property
    def qualname(self):
        return f'{self.__class__.__module__}.{self.name}'

    @property
    def parameters(self):
        parameters = self.params
        if parameters is None:
            parameters = self.__slots__
        return parameters

    def __reduce__(self):
        data = []
        for param in self.parameters:
            data.append(getattr(self, param))
        return data

    def serialize(self):
        data = {}
        for param in self.parameters:
            data[param] = getattr(self, param)
        return data

    # def __lt__(self, other):
    #     # Just some arbitrary comparison for total_ordering to work
    #     return id(self) < id(other)

    #def __eq__(self, other):
    #    return id(self) == id(other)

    def __repr__(self):
        param_values = [(param, getattr(self, param)) for param in self.parameters]
        if not param_values:
            return f'<{self.name}={super().__repr__()}>'
        else:
            param_values_txt = ', '.join([f'{param}={value!r}' for param, value in param_values])
            return f'<{self.name} {param_values_txt}>'


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

    """Single value component that can be incremented/decremented, and compared to other values."""

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
    return functools.partial(_type_factory, bases=bases)


Int = component_type(IntComponent)
Bool = component_type(IntComponent)
Float = component_type(IntComponent)
String = component_type(Component, str)
EntityRef = component_type(Component, Entity)
Counter = component_type(CounterComponent)


class JoinIterator:

    __slots__ = ('managers', )

    def __init__(self, *managers):
        self.managers = managers

    def __iter__(self):
        if not all(self.managers):
            return
        entities = set.intersection(*[
            manager.entities
            for manager in self.managers
            # NOTE: No need to intersect with ALL entitites
            if not isinstance(manager, EntitiesManager)
        ])
        # TODO: Consider filtering out FlagComponent no need to have element that is always True
        for entity in entities:
            values = [
                manager.get(entity)
                for manager in self.managers
            ]
            yield values


class JoinableManager:

    __slots__ = ('entities', '_values', )

    def __init__(self):
        self.entities = EntitiesSet()
        self._values = {} # = {entity: value, }

    def __len__(self):
        return len(self._values)

    def __contains__(self, entity):
        # return entity in self._values
        return entity in self.entities

    def get(self, entity, default=None):
        return self._values.get(entity, default)

    def __iter__(self):
        # yield from self._values.keys()
        yield from self.entities

    def insert(self, entity, value):
        self.entities.add(entity)
        self._values[entity] = value

    def discard(self, entity):
        self.entities.discard(entity)
        self._values.pop(entity, None)

    def remove(self, *entities):
        for entity in entities:
            self.discard(entity)

    def clear(self):
        self.entities.clear()
        self._values.clear()


class EntitiesSet(set):

    def get(self, entity):
        return entity

    @property
    def entities(self):
        return self


class ComponentManager(JoinableManager):

    __slots__ = ('component_type', )

    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type

    def insert(self, entity, *args, component=None, **kwargs):
        if component and not type(component) == self.component_type:
            raise ValueError('Invalid component type!')
        component = component or self.component_type(*args, **kwargs)
        super().insert(entity, component)
        return component

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.component_type.__name__})>'


class EntitiesManager(EntitiesSet):

    def __init__(self):
        super().__init__()
        self._component_managers = {} # {component_type: ComponentManager(component_type), }

    def manage(self, component_type):
        if isinstance(component_type, Component):
            component_type = type(component_type)
        component_manager = self._component_managers.get(component_type)
        if component_manager is None:
            component_manager = ComponentManager(component_type)
            self._component_managers[component_type] = component_manager
        return self._component_managers[component_type]

    def create(self, *components, entity_id=None):
        entity = Entity(entity_id)
        self.add(entity)
        for component in components:
            component_manager = self.manage(component)
            component_manager.insert(entity, component=component)
        return entity

    def remove(self, *entities):
        for entity in entities:
            for component_manager in self._component_managers.values():
                component_manager.discard(entity)
            self.discard(entity)

    def all_components(self, entity):
        components = []
        for component_manager in self._component_managers.values():
            component = component_manager.get(entity)
            if component:
                components.append(component)
        return components

    def serialize(self):
        data = collections.defaultdict(dict)
        # TODO: Use: data = {component.qualname: {entity: component, }, } ?
        for entity in self:
            for component in self.all_components(entity):
                data[entity][component.qualname] = component.serialize()
        return data

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class System:

    INCLUDE_STATES = set()
    EXCLUDE_STATES = set()

    def __init__(self, ecs):
        self.ecs = ecs

    def should_run(self, state):
        if self.EXCLUDE_STATES and state in self.EXCLUDE_STATES:
            return False
        if self.INCLUDE_STATES and not state in self.INCLUDE_STATES:
            return False
        return True

    def run(self, state, *args, **kwargs):
        return

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class SystemsManager:

    def __init__(self):
        self.systems = []

    def register(self, system):
        self.systems.append(system)

    def run(self, state, *args, **kwargs):
        systems = [system for system in self if system.should_run(state)]
        # log.debug(f'systems.run({state.name}): {systems}')
        for system in systems:
            system.run(state, *args, **kwargs)

    def __iter__(self):
        yield from self.systems


class LevelsManager:

    def __init__(self):
        self.levels = {}

    def add(self, level):
        self.levels[level.id] = level

    def get(self, level_id):
        return self.levels.get(level_id)

    def __contains__(self, level_id):
        return level_id in self.levels

    def __iter__(self):
        yield from self.levels.values()


class ECS:

    def __init__(self):
        self.entities = EntitiesManager()
        self.systems = SystemsManager()
        self.levels = LevelsManager()

    def create(self, *components, entity_id=None):
        return self.entities.create(*components, entity_id=entity_id)

    def get(self, entity_id):
        return self.entities.get(entity_id)

    def manage(self, component_type):
        return self.entities.manage(component_type)

    def join(self, *managers):
        yield from JoinIterator(*managers)

    def register(self, system):
        self.systems.register(system)

    def run(self, state, *args, **kwargs):
        with perf.Perf('ecs.Systems.run()'):
            self.systems.run(state, *args, **kwargs)

    def add_level(self, level):
        self.levels.add(level)

