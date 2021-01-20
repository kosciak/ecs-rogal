import logging
import os.path

from . import components
from .data_loaders import DATA_DIR, YAMLDataLoader
from . import terrain


log = logging.getLogger(__name__)


"""Entities loading and spawning."""

# TODO: 
#   - Split data/entities.yaml into data/terrain.yaml, data/actors.yaml 
#   - Use qualified names when loading "terrain.STONE_WALL", "actors.PLAYER", etc


class Entities(YAMLDataLoader):

    _data = None

    def __init__(self, ecs, tileset):
        self.fn = os.path.join(
            DATA_DIR,
            'entities.yaml'
        )
        self.ecs = ecs
        self.tileset = tileset
        self.on_init()

    @property
    def data(self):
        if self._data is None:
            self._data = self.load_data(self.fn)
        return self._data

    # def parse_<value_name>(self, value): return parsed_value

    def parse_renderable_tile(self, value):
        return self.tileset.get(value)

    def parse_onoperate_insert(self, value):
        return [self.get_component(n, v) for n, v in value.items()]

    def parse_onoperate_remove(self, value):
        return [self.get_component_type(v) for v in value]

    def parse_values(self, component_name, values):
        parsed = {}
        for name, value in values.items():
            parser_fn = getattr(self, f'parse_{component_name.lower()}_{name}', None)
            if parser_fn:
                value = parser_fn(value)
            parsed[name] = value
        return parsed

    def get_component_type(self, name):
        return getattr(components, name)

    def get_component(self, name, values):
        component_type = self.get_component_type(name)
        if values is None:
            component = component_type()
        elif isinstance(values, dict):
            values = self.parse_values(name, values)
            component = component_type(**values)
        elif isinstance(values, list):
            component = component_type(*values)
        else:
            component = component_type(values)
        return component

    def get_data(self, path):
        names = path.split('.')
        data = self.data
        for name in names:
            data = data.get(name)
        return data

    def get_names(self, path):
        path = path.rstrip('.*')
        data = self.get_data(path)
        if data:
            names = [f'{path}.{name}' for name in data.keys()]
        else:
            names = []
        return names

    def get_template(self, name):
        template = []
        entity_data = self.get_data(name)
        for name, values in entity_data.items():
            component = self.get_component(name, values)
            template.append(component)
        return template

    def parse_entity_id(self, template):
        for component in template:
            if type(component) == components.Terrain:
                return terrain.get_terrain_id(component)

    def on_init(self):
        on_load_create = self.get_data('on_load.create')
        for name in self.get_names(on_load_create):
            self.create(name)

    def create(self, name, entity_id=None):
        template = self.get_template(name)
        entity_id = self.parse_entity_id(template)
        return self.ecs.create(*template, entity_id=entity_id)

    def spawn(self, name, level_id, position, entity_id=None):
        entity = self.create(name, entity_id=entity_id)
        locations = self.ecs.manage(components.Location)
        locations.insert(entity, level_id, position)

