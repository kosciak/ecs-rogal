import logging
import os.path

import yaml

from . import components
from .renderable import RenderOrder
from .terrain import Terrain
from .tiles import TermTiles as tiles


log = logging.getLogger(__name__)


"""Entities loading and spawning."""

# TODO: 
#   - Split data/entities.yaml into data/terrain.yaml, data/actors.yaml 
#   - Use qualified names when loading "terrain.STONE_WALL", "actors.PLAYER", etc

DATA_DIR = 'data'

TERRAIN = {
    Terrain.VOID.id: 'VOID',
    Terrain.STONE_WALL.id: 'STONE_WALL',
    Terrain.STONE_FLOOR.id: 'STONE_FLOOR',
    Terrain.SHALLOW_WATER.id: 'SHALLOW_WATER',
}


class EntityLoader:

    _data = None

    def __init__(self, ecs):
        self.fn = os.path.join(
            DATA_DIR,
            'entities.yaml'
        )
        self.ecs = ecs

    @property
    def data(self):
        if self._data is None:
            self._data = self.load_data(self.fn)
        return self._data

    def load_data(self, fn):
        log.debug(f'Loading data: {fn}')
        with open(self.fn, 'r') as f:
            data = yaml.safe_load(f)
            return data

    # def parse_<value_name>(self, value): return parsed_value

    def parse_tile(self, value):
        return getattr(tiles, value)

    def parse_render_order(self, value):
        return getattr(RenderOrder, value)

    def parse_insert(self, value):
        return [self.get_component(n, v) for n, v in value.items()]

    def parse_remove(self, value):
        return [self.get_component_type(v) for v in value]

    def parse_values(self, values):
        parsed = {}
        for name, value in values.items():
            parser_fn = getattr(self, f'parse_{name}')
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
            values = self.parse_values(values)
            component = component_type(**values)
        elif isinstance(values, list):
            component = component_type(*values)
        else:
            component = component_type(values)
        return component

    def get_components(self, name):
        template = []
        entity_data = self.data.get(name)
        for name, values in entity_data.items():
            component = self.get_component(name, values)
            template.append(component)
        return template

    def create(self, name, entity_id=None):
        template = self.get_components(name)
        return self.ecs.create(*template, entity_id=entity_id)

    def spawn(self, name, level_id, position, entity_id=None):
        entity = self.create(name, entity_id=entity_id)
        locations = self.ecs.manage(components.Location)
        locations.insert(entity, level_id, position)

