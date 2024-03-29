import collections
import functools
import logging
import uuid

from ..collections.attrdict import AttrDict
from ..utils import perf

from .run_state import RunState


log = logging.getLogger(__name__)


class Entity(int):

    """Entity is just and integer ID.

    All data related to given Entity is stored in ComponentManagers.

    """

    __slots__ = ()

    def __new__(cls, entity_id=None):
        if entity_id is None:
            entity_id = uuid.uuid4().int
        if isinstance(entity_id, bytes):
            entity_id = int.from_bytes(entity_id, 'big')
        return super().__new__(cls, entity_id)

    @property
    def bytes(self):
        return self.to_bytes(16, 'big')

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

    """Component that holds some data.

    Components should provide only setters and getters.
    All logic should be handled in Systems!

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

    def __repr__(self):
        param_values = [(param, getattr(self, param)) for param in self.parameters]
        if not param_values:
            return f'<{self.name}={super().__repr__()}>'
        else:
            param_values_txt = ', '.join([f'{param}={value!r}' for param, value in param_values])
            return f'<{self.name} {param_values_txt}>'


class EntitiesSet(set):

    """Entities container, compatibile with JoinManager interface."""

    __slots__ = ()

    def get(self, entity):
        # NOTE: It's assumed that get() is called inside JoinIterator that already knows if entity is present
        return entity

    @property
    def entities(self):
        return self


class ComponentManager(dict):

    __slots__ = ('component_type', )

    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type

    @property
    def entities(self):
        return EntitiesSet(self.keys())

    def __iter__(self):
        """Yield (entity, component) pairs.

        If you only want entities - iterate over manager.entities instead

        """
        # NOTE: Iterating over values dict directly boosted performance significantly!
        yield from self.items()

    def insert(self, entity, *args, component=None, **kwargs):
        if component is not None and not isinstance(component, self.component_type):
            raise ValueError('Invalid component type!')
        if component is None:
            component = self.component_type(*args, **kwargs)
        self[entity] = component
        return component

    def discard(self, entity):
        # self.entities.discard(entity)
        self.pop(entity, None)

    def remove(self, *entities):
        for entity in entities:
            self.discard(entity)

    def __rand__(self, other):
        return other & self.keys()

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.component_type.__name__})>'


class JoinIterator:

    """Iterate through values of combined ComponentManagers and EntitiesSets

    Only entities / components that are present in all provided managers are returned.

    """

    __slots__ = ('ignore', 'managers', )

    def __init__(self, ignore, *managers):
        self.ignore = ignore
        self.managers = managers

    def __iter__(self):
        if not all(self.managers):
            return
        # entities = set.intersection(*[
        #     manager.entities
        #     for manager in self.managers
        #     # NOTE: No need to intersect with ALL entitites
        #     if not manager is self.ignore
        # ])

        entities = None
        for manager in sorted(self.managers, key=lambda m: len(m)):
            if manager is self.ignore:
                continue
            if entities is None:
                entities = EntitiesSet(manager.entities)
                continue
            entities &= manager

        # TODO: Consider filtering out FlagComponent no need to have element that is always True
        for entity in entities:
            values = [
                manager.get(entity)
                for manager in self.managers
            ]
            yield values


class System:

    INCLUDE_STATES = set()
    EXCLUDE_STATES = set()

    def __init__(self, ecs):
        self.ecs = ecs

    @functools.lru_cache
    def should_run(self, state):
        """Return True if system should run with given RunState."""
        if self.EXCLUDE_STATES and state in self.EXCLUDE_STATES:
            return False
        if self.INCLUDE_STATES and not state in self.INCLUDE_STATES:
            return False
        return True

    def run(self):
        return

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class SystemsManager:

    def __init__(self):
        self.systems = []
        self.run_state = RunState.PRE_RUN # TODO: RENDER or WAIT_FOR_INPUT
        self.next_run_state = None

    def register(self, *systems):
        for system in systems:
            self.systems.append(system)

    def run(self):
        # Run all systems that should run with given run_state
        systems = []
        for system in self.systems:
            if not system.should_run(self.run_state):
                continue
            with perf.Perf(system.run):
                system.run()
            systems.append(system)
        log.debug(f'systems.run({self.run_state.name}): {systems}')

        # Change run_state AFTER running all systems
        if self.next_run_state:
            self.run_state = self.next_run_state
            self.next_run_state = None

    def __iter__(self):
        yield from self.systems


class ResourcesManager(AttrDict):

    def register(self, **kwargs):
        self.update(**kwargs)


class ECS:

    """Entity Component System - data storage and processing.

    Entity - simple ID for object
    Component - data associated with given object, pure data
    System - implements all logic of interaction between entities and their components

    Resources - resources not associated with any entity

    """

    def __init__(self):
        self.entities = EntitiesSet()
        self._components = {} # {component_type: ComponentManager(component_type), }
        self._systems = SystemsManager()
        self.resources = ResourcesManager()

    @property
    def run_state(self):
        return self._systems.run_state

    @run_state.setter
    def run_state(self, run_state):
        self._systems.next_run_state = run_state

    def set_run_state(self, run_state):
        log.warning('set_run_state() -> %s', run_state)
        self.run_state = run_state

    @property
    def next_state(self):
        return self._systems.next_run_state

    def create(self, *components, entity_id=None):
        """Create Entity with given components."""
        entity = Entity(entity_id)
        self.entities.add(entity)
        for component in components:
            if component is None:
                continue
            component_manager = self.manage(component)
            component_manager.insert(entity, component=component)
        return entity

    def manage(self, component_type):
        """Return ComponentManager for given Component."""
        if isinstance(component_type, Component):
            component_type = type(component_type)
        component_manager = self._components.get(component_type)
        if component_manager is None:
            component_manager = ComponentManager(component_type)
            self._components[component_type] = component_manager
        return component_manager

    def get_components(self, entity):
        """Return list of all components for given Entity."""
        components = []
        for component_manager in self._components.values():
            component = component_manager.get(entity)
            if component:
                components.append(component)
        return components

    def remove(self, *entities):
        """Remove Entity."""
        for entity in entities:
            for component_manager in self._components.values():
                component_manager.discard(entity)
            self.entities.discard(entity)

    def join(self, *managers):
        """Return iterator over values of multiple managers.

        If you only want to iterate for entity, component pairs iterate over manager itself!

        """
        yield from JoinIterator(self.entities, *managers)

    def register(self, *systems):
        """Register System."""
        self._systems.register(*systems)

    def run_once(self, *args, **kwargs):
        """Run Systems for given RunState."""
        with perf.Perf(self._systems.run):
            self._systems.run(*args, **kwargs)

    def run(self):
        # Should be named join() as in Thread.join() 
        # but join() is already used for joining managers as in database query
        while True:
            self.run_once()

