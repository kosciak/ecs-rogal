import collections
import functools
import logging
import uuid


log = logging.getLogger(__name__)


@functools.total_ordering
class Component:

    """Component that hold some value(s).

    params - values that are used by constructor and serialization

    """

    __slots__ = ()
    params = ()

    @property
    def name(self):
        return f'{self.__class__.__name__}'

    @property
    def qualname(self):
        return f'{self.__class__.__module__}.{self.name}'

    def __reduce__(self):
        data = []
        params = self.params or self.__slots__
        for param in params:
            data.append(getattr(self, param))
        return data

    def serialize(self):
        data = {}
        params = self.params or self.__slots__
        for param in params:
            data[param] = getattr(self, param)
        return data

    def __lt__(self, other):
        # Just some arbitrary comparison for total_ordering to work
        return id(self) < id(other)

    #def __eq__(self, other):
    #    return id(self) == id(other)

    def __repr__(self):
        param_values = []
        if self.params:
            param_values = [(param, getattr(self, param)) for param in self.params]
        elif self.__slots__:
            param_values = [(param, getattr(self, param)) for param in self.__slots__]
        if not param_values:
            return f'<{self.name}>'
        else:
            param_values_txt = ', '.join([f'{param}={value!r}' for param, value in param_values])
            return f'<{self.name} {param_values_txt}>'


class ConstantValueComponent(Component):

    """Component that holds constant value, when iterating only it's value is returned."""

    __slots__ = ()

    def serialize(self):
        return self.value


class SingleValueComponent(Component):

    """Component that holds single value."""

    __slots__ = ('value', )
    params = ('value', )

    def __init__(self, value):
        self.value = value

    def serialize(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f'<{self.__class__.__name__}={self.value!r}>'


class CounterComponent(SingleValueComponent):

    """Single value component that can be incremented/decremented, and compared to other values."""

    __slots__ = ()

    def __init__(self, value):
        super().__init__(int(value))

    def __add__(self, value):
        self.value += value
        return self

    def __sub__(self, value):
        self.value -= value
        return self

    def __eq__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value == other

    def __lt__(self, other):
        return self.value < other


class FlagComponent(ConstantValueComponent):

    """Constant value Component holding True as value."""

    _INSTANCE = None

    __slots__ = ()
    params = ('value', )

    def __new__(cls):
        if not cls._INSTANCE:
            # NOTE: Singleton
            cls._INSTANCE = super().__new__(cls)
        return cls._INSTANCE

    @property
    def value(self):
        return True

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


def Flag(name):
    """Returns FlagComponent instance of class with given name."""
    bases = (FlagComponent, )
    attrs = dict(
        __slots__=(),
        __call__=lambda self, *args, **kwargs: self,
    )
    return type(name, bases, attrs)()


def _type_factory(name, bases):
    """Returns class with given name, inheriting from bases."""
    attrs = dict(
        __slots__=(),
    )
    return type(name, bases, attrs)

def component_type(*bases):
    return functools.partial(_type_factory, bases=bases)

Constant = component_type(ConstantValueComponent, SingleValueComponent, )
Counter = component_type(CounterComponent)


class Entity(int):

    """Entity is just and integer ID."""

    __slots__ = ()

    def __new__(cls, entity_id=None):
        if entity_id is None:
            entity_id = uuid.uuid4().int
        return super().__new__(cls, entity_id)

    def __repr__(self):
        hex = '%032x' % self
        return '<Entity id="%s-%s-%s-%s-%s">' % (
            hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])


class EntitiesIterator:

    __slots__ = ('managers', )

    def __init__(self, *managers):
        self.managers = managers

    def __iter__(self):
        if not all(self.managers):
            return
        if len(self.managers) == 1 and \
           isinstance(self.managers[0], EntitiesManager):
            # NOTE: Iterate through all entities, it's the only one manager
            entities = self.managers[0].entities
        else:
            entities = set.intersection(*(
                manager.entities
                for manager in self.managers
                # NOTE: No need to intersect with ALL entitites
                if not isinstance(manager, EntitiesManager)
            ))
        yield from entities


class JoinIterator:

    __slots__ = ('managers', )

    def __init__(self, *managers):
        self.managers = managers

    def __iter__(self):
        if not all(self.managers):
            return
        entities = EntitiesIterator(*self.managers)
        # TODO: Consider filtering out FlagComponent no need to have element that is always True
        for entity in entities:
            values = [
                manager.get(entity)
                for manager in self.managers
            ]
            yield values


class JoinableManager:

    __slots__ = ('_values', )

    def __init__(self):
        self._values = {} # = {entity: value, }

    def __len__(self):
        return len(self._values)

    def __contains__(self, entity):
        return entity in self._values

    def get(self, entity):
        return self._values.get(entity)

    def __iter__(self):
        yield from self._values.values()

    def discard(self, entity):
        self._values.pop(entity, None)

    def remove(self, *entities):
        for entity in entities:
            self.discard(entity)

    def clear(self):
        self._values.clear()

    @property
    def entities(self):
        return EntitiesSet(self._values.keys())


class EntitiesSet(set):

    def get(self, entity):
        if entity in self:
            return entity

    @property
    def entities(self):
        return self


class ComponentManager(JoinableManager):

    __slots__ = ('component_type', )

    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type

    def get(self, entity, unpack_constants=True):
        value = super().get(entity)
        if unpack_constants and isinstance(value, ConstantValueComponent):
            return value.value
        return value

    def insert(self, entity, *args, component=None, **kwargs):
        if component and not type(component) == self.component_type:
            raise ValueError('Invalid component type!')
        component = component or self.component_type(*args, **kwargs)
        self._values[entity] = component

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

    def serialize(self):
        data = {}
        # TODO: Needs rewrite!!!
        return data

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class System:

    INCLUDE_STATES = set()
    EXCLUDE_STATES = set()

    def __init__(self, ecs, entities):
        self.ecs = ecs
        self.entities = entities

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
        log.debug(f'systems.run({state.name}): {systems}')
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
        self.systems.run(state, *args, **kwargs)

    def add_level(self, level):
        self.levels.add(level)

