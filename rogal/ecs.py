import collections
import uuid


# TODO: ComponentMeta extracting lower_case name to be used as entity.name_of_component?

class Component:

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


class SingleValueComponent(Component):

    __slots__ = ('value', )

    def __init__(self, value):
        self.value = value

    def serialize(self):
        return self.value

    def __repr__(self):
        return f'<{self.__class__.__name__}={self.value!r}>'


class FlagComponent(Component):

    __slots__ = ('_value', )

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def serialize(self):
        return self.value

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


def SingleValue(name):
    """Returns SingleValueComponent class with given name."""
    bases = (SingleValueComponent, )
    attrs = dict(
        __slots__=(),
        params=('value', ),
    )
    return type(name, bases, attrs)


def Flag(name):
    """Returns FlagComponent instance of class with given name."""
    bases = (FlagComponent, )
    attrs = dict(
        __slots__=(),
        __call__=lambda self, *args, **kwargs: self,
    )
    return type(name, bases, attrs)(value=True)


class Entity:

    __slots__ = ('id', '_components', )

    def __init__(self, entity_id, *components):
        self.id = entity_id
        self._components = {}
        self.attach(*components)

    def __repr__(self):
        return f'<Entity id={self.id}, {list(self._components.values())}>'

    def attach(self, *components):
        for component in components:
            component_type = type(component)
            self._components[component_type] = component

    def remove(self, *component_types):
        for component_type in component_types:
            if isinstance(component_type, Component):
                component_type = type(component_type)
            if not component_type in self._components:
                return
            self._components.pop(component_type, None)

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
        component = self._components.get(component_type)
        if isinstance(component, (SingleValueComponent, FlagComponent)):
            return component.value
        else:
            return component

    @property
    def components(self):
        return self._components.values()

    def serialize(self):
        data = {}
        for component in self.components:
            data[component.name] = component.serialize()
        return data


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


class ComponentIterator:

    __slots__ = ('component_manager', )

    def __init__(self, component_manager):
        self.component_manager = component_manager

    def __iter__(self):
        # TODO: Check if removing entity while iterating won't break things!
        for entity in self.component_manager.entities:
            yield component_manager.get(entity)


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

    @property
    def entities(self):
        return {}

    def get(self, entity):
        raise NotImplementedError()

    # TODO: Do I really need it at Manager level? Maybe ecs.join(*managers) should be enough?
    def join(self, *managers):
        yield from JoinIterator(self, *managers)


class EntitiesSet(set, JoinableManager):

    @property
    def entities(self):
        return self

    def get(self, entity):
        if entity in self:
            return entity


class ComponentManager(JoinableManager):

    __slots__ = ('_entities', 'component_type', )

    def __init__(self, component_type):
        self._entities = set()
        self.component_type = component_type

    def __len__(self):
        return len(self._entities)

    def __contains__(self, entity):
        return entity in self.entities

    def get(self, entity):
        return entity.get(self.component_type)

    def insert(self, entity, *args, component=None, **kwargs):
        if component and not type(component) == self.component_type:
            raise ValueError('Invalid component type!')
        component = component or self.component_type(*args, **kwargs)
        entity.attach(component)
        self.entities.add(entity)

    def remove(self, *entities):
        for entity in entities:
            entity.remove(self.component_type)
        self.entities -= set(entities)

    def clear(self):
        for entity in self.entities:
            entity.remove(self.component_type)
        self.entities.clear()

    @property
    def entities(self):
        return self._entities

    def iter(self):
        yield from ComponentIterator(self)

    def __iter__(self):
        yield from self.iter()

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.component_type.__name__})>'


class EntitiesManager(JoinableManager):

    def __init__(self):
        self._entities = {} # {entity.id: entity, }
        self._component_managers = {} # {component_type: ComponentManager(component_type), }

    def manage(self, component_type):
        if isinstance(component_type, Component):
            component_type = type(component_type)
        component_manager = self._component_managers.get(component_type)
        if component_manager is None:
            component_manager = ComponentManager(component_type)
            self._component_managers[component_type] = component_manager
        return self._component_managers[component_type]

    def get_id(self, entity_id):
        if isinstance(entity_id, Entity):
            return entity_id.id
        if isinstance(entity_id, uuid.UUID):
            return entity_id
        if entity_id is not None:
            return uuid.UUID(int=entity_id)
        return uuid.uuid4()

    def create(self, *components, entity_id=None):
        entity_id = self.get_id(entity_id)
        entity = Entity(entity_id)
        self._entities[entity.id] = entity
        for component in components:
            component_manager = self.manage(component)
            component_manager.insert(entity, component=component)
        return entity

    def get(self, entity_id):
        entity_id = self.get_id(entity_id)
        return self._entities.get(entity_id)

    def remove(self, *entities):
        for entity in entities:
            for component_type in entity.components.keys():
                component_manager = self.manage(component_type)
                component_manager.remove(entity, component_type)
            self._entities.pop(entity.id, None)

    @property
    def entities(self):
        return self._entities.values()

    def __iter__(self):
        yield from self._entities.values()

    def serialize(self):
        data = {}
        for entity in self:
            data[str(entity.id)] = entity.serialize()
        return data

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class ECS:

    def __init__(self):
        self.entities = EntitiesManager()
        # TODO: self.systems = SystemsManager()
        self.systems = []

    def create(self, *components, entity_id=None):
        return self.entities.create(*components, entity_id=entity_id)

    def manage(self, component_type):
        return self.entities.manage(component_type)

    def join(self, *managers):
        yield from JoinIterator(*managers)

    def register(self, system):
        self.systems.append(system)

    def systems_run(self, *args, **kwargs):
        print('Running systems...')
        for system_run in self.systems:
            system_run(self, *args, **kwargs)

