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


class Entity:

    """Entity with set of Components.

    Entity contains only one Component of given type.

    """

    __slots__ = ('id', '_component_types', )

    def __init__(self, entity_id):
        self.id = entity_id
        self._component_types = {}

    def __repr__(self):
        return f'<Entity id={self.id}, {list(self.components)}>'

    def attach(self, manager):
        self._component_types[manager.component_type] = manager

    def remove(self, *component_types):
        for component_type in component_types:
            if isinstance(component_type, Component):
                component_type = type(component_type)
            self._component_types.pop(component_type, None)

    def __contains__(self, component_type):
        if isinstance(component_type, Component):
            component_type = type(component_type)
        return component_type in self._components

    def has(self, *component_types):
        for component_type in component_types:
            if not component_type in self:
                return False
        return True

    def get(self, component_type):
        if isinstance(component_type, Component):
            component_type = type(component_type)
        manager = self._component_types.get(component_type)
        return manager.get(self.id)

    @property
    def components(self):
        for manager in self._component_types.values():
            yield manager.get(self.id, unpack_constants=False)

    def serialize(self):
        data = {}
        for component in self.components:
            data[component.name] = component.serialize()
        return data


class EntityIDsIterator:

    __slots__ = ('managers', )

    def __init__(self, *managers):
        self.managers = managers

    def __iter__(self):
        if not all(self.managers):
            return
        if len(self.managers) == 1 and \
           isinstance(self.managers[0], EntitiesManager):
            # NOTE: Iterate through all entities, it's the only one manager
            entity_ids = self.managers[0].entity_ids
        else:
            entity_ids = set.intersection(*(
                manager.entity_ids
                for manager in self.managers
                # NOTE: No need to intersect with ALL entitites
                if not isinstance(manager, EntitiesManager)
            ))
        yield from entity_ids


class JoinIterator:

    __slots__ = ('managers', )

    def __init__(self, *managers):
        self.managers = managers

    def __iter__(self):
        if not all(self.managers):
            return
        entity_ids = EntityIDsIterator(*self.managers)
        # TODO: Consider filtering out FlagComponent no need to have element that is always True
        for entity_id in entity_ids:
            values = [
                manager.get(entity_id)
                for manager in self.managers
            ]
            yield values


class JoinableManager:

    __slots__ = ('_values', )

    def __init__(self):
        self._values = {} # = {entity_id: value, }

    def get_id(self, entity_id):
        if isinstance(entity_id, uuid.UUID):
            return entity_id
        if isinstance(entity_id, Entity):
            return entity_id.id
        if entity_id is not None:
            return uuid.UUID(int=entity_id)

    def __len__(self):
        return len(self._values)

    def __contains__(self, entity):
        entity_id = self.get_id(entity)
        return entity_id in self._values

    def get(self, entity):
        entity_id = self.get_id(entity)
        return self._values.get(entity_id)

    def __iter__(self):
        yield from self._values.values()

    def clear(self):
        self._values.clear()

    @property
    def entity_ids(self):
        return set(self._values.keys())

    # TODO: Do I really need it at Manager level? Maybe ecs.join(*managers) should be enough?
    def join(self, *managers):
        yield from JoinIterator(self, *managers)


# TODO: Rename? It's not set after all...
class EntitiesSet(JoinableManager):

    def add(self, entity):
        entity_id = self.get_id(entity)
        self._values[entity_id] = entity

    def discard(self, entity):
        entity_id = self.get_id(entity)
        self._values.pop(entity_id, None)


class ComponentManager(JoinableManager):

    __slots__ = ('entities', 'component_type', )

    def __init__(self, component_type):
        super().__init__()
        self.entities = EntitiesSet()
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
        entity.attach(self)
        self._values[entity.id] = component
        self.entities.add(entity)

    def remove(self, *entities):
        for entity in entities:
            entity.remove(self.component_type)
            self._values.pop(entity.id, None)
            self.entities.discard(entity)

    def clear(self):
        for entity in self.entities:
            entity.remove(self.component_type)
        self.entities.clear()
        super().clear()

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.component_type.__name__})>'


class EntitiesManager(JoinableManager):

    def __init__(self):
        super().__init__()
        self._component_managers = {} # {component_type: ComponentManager(component_type), }

    def get_id(self, entity_id):
        if entity_id is None:
            return uuid.uuid4()
        else:
            return super().get_id(entity_id)

    def manage(self, component_type):
        if isinstance(component_type, Component):
            component_type = type(component_type)
        component_manager = self._component_managers.get(component_type)
        if component_manager is None:
            component_manager = ComponentManager(component_type)
            self._component_managers[component_type] = component_manager
        return self._component_managers[component_type]

    def create(self, *components, entity_id=None):
        entity_id = self.get_id(entity_id)
        entity = Entity(entity_id)
        self._values[entity.id] = entity
        for component in components:
            component_manager = self.manage(component)
            component_manager.insert(entity, component=component)
        return entity

    def remove(self, *entities):
        for entity in entities:
            for component_manager in list(entity._component_types.values()):
                component_manager.remove(entity)
            self._values.pop(entity.id, None)

    def serialize(self):
        data = {}
        for entity in self:
            data[str(entity.id)] = entity.serialize()
        return data

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
        self.systems.register(system(self))

    def run(self, state, *args, **kwargs):
        self.systems.run(state, *args, **kwargs)

    def add_level(self, level):
        self.levels.add(level)

