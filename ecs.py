import collections
import uuid


class Component:

    __slots__ = ()
    _attrs_ = ()

    def __repr__(self):
        attr_values = []
        if self._attrs_:
            attr_values = [(attr, getattr(self, attr)) for attr in self._attrs_]
        elif self.__slots__:
            attr_values = [(attr, getattr(self, attr)) for attr in self.__slots__]
        if not attr_values:
            return f'<{self.__class__.__name__}>'
        else:
            attr_values_txt = ', '.join([f'{attr}={value}' for attr, value in attr_values])
            return f'<{self.__class__.__name__} {attr_values_txt}>'


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
            if isinstance(component_type, Component):
                component_type = type(component_type)
            if not component_type in self:
                return False
        return True
    
    def get(self, component_type):
        if isinstance(component_type, Component):
            component_type = type(component_type)
        return self._components.get(component_type)

    @property
    def components(self):
        return self._components.values()


class SingleComponentIterator:

    __slots__ = ('component_manager', )

    def __init__(self, component_manager):
        self.component_manager = component_manager

    def __iter__(self):
        # TODO: Check if removing entity while iterating won't break things!
        for entity in self.component_manager.entities:
            yield entity, entity.get(self.component_manager.component_type)


class MultiComponentsIterator:

    __slots__ = ('component_managers', )

    def __init__(self, *component_managers):
        self.component_managers = component_managers

    def __iter__(self):
        entities = set.intersection(*[
            component_manager.entities
            for component_manager in self.component_managers
        ])
        for entity in entities:
            components = [
                entity.get(component_manager.component_type)
                for component_manager in self.component_managers
            ]
            yield (entity, *components)


class ComponentManager:

    __slots__ = ('_entities', 'component_type', )

    def __init__(self, component_type):
        self._entities = set()
        self.component_type = component_type

    def __len__(self):
        return len(self._entities)

    def __contains__(self, entity):
        return entity in self.entities

    def insert(self, entity, component):
        if not type(component) == self.component_type:
            raise ValueError('Invalid component type!')
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
        yield from SingleComponentIterator(self)

    def __iter__(self):
        yield from self.iter()

    def join(self, *component_managers):
        component_managers = [self, *component_managers]
        yield from MultiComponentsIterator(*component_managers)


class EntitiesManager:

    def __init__(self):
        self._entities = {} # {entity.id: entity, }
        self._component_managers = {} # {component_type: ComponentManager(component_type), }

    def create(self, *components, entity_id=None):
        entity_id = entity_id or uuid.uuid4()
        entity = Entity(entity_id, *components)
        self._entities[entity.id] = entity
        for component in entity.components:
            component_type = type(component)
            component_manager = self._component_managers.get(component_type)
            if not component_manager:
                component_manager = ComponentManager(component_type)
                self._component_managers[component_type] = component_manager
            component_manager.insert(entity, component)
        return entity

    def get(self, entity_id):
        return self._entities.get(entity_id)

    def remove(self, *entities):
        for entity in entities:
            for component_type in entity.components.keys():
                manager = self._component_managers[component_type]
                manager.remove(entity, component_type)
            self._entities.pop(entity.id, None)

    def manage(self, component_type):
        if isinstance(component_type, Component):
            component_type = type(component_type)
        return self._component_managers[component_type]

    def filter(self, *component_types):
        component_managers = [
            self._component_managers[component_type] 
            for component_type in component_types
        ]
        if len(component_managers) == 1:
            yield from SingleComponentIterator(component_managers[0])
        else:
            yield from MultiComponentsIterator(*component_managers)

