import collections
import uuid

import numpy as np

from . import dtypes
from .ecs import EntitiesSet
from .bitmask import bitmask_8bit
from .geometry import Rectangular, Direction, Position


class Level(Rectangular):

    position = Position.ZERO

    def __init__(self, level_id, size, depth):
        self.id = level_id

        self.size = size
        self.depth = depth

        self.terrain = np.zeros(self.size, dtype=dtypes.terrain_id_dt)

        # NOTE: entities and indexes depend on IndexingSystem
        self.entities = EntitiesSet()
        self.entities_per_position = collections.defaultdict(EntitiesSet)

    @staticmethod
    def create(size, depth):
        level_id = uuid.uuid4()
        return Level(level_id, size, depth)

    def get_entities(self, *positions):
        """Return entities on given position."""
        entities = EntitiesSet()
        # for position in positions:
        #     entities.update(self.entities_per_position[position])
        positions = set(positions)
        for position in self.entities_per_position.keys():
            if position in positions:
                entities.update(self.entities_per_position[position])
        return entities

    def serialize(self):
        terrain = []
        for row in self.terrain.T:
            terrain.append(','.join([f'{terrain_id:02x}' for terrain_id in row]))
        data = {
            str(self.id): dict(
                depth=self.depth,
                #name=self.name,
                terrain=terrain,
            )}
        return data

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id} depth={self.depth} size={self.size}>'

