import collections
import uuid

import numpy as np

from . import dtypes
from .ecs import EntitiesSet
from .flags import Flag
from .geometry import Direction, Position, Rectangle

    
class GameMap(Rectangle):

    def __init__(self, map_id, size, depth):
        super().__init__(Position.ZERO, size)

        self.id = map_id

        self.depth = depth

        self.terrain = np.zeros(self.size, dtype=dtypes.terrain_id_dt)

        self.base_flags = np.zeros(self.size, dtype=dtypes.flags_dt)
        self.base_movement_cost = np.zeros(self.size, dtype=dtypes.movement_cost_dt)

        self.flags = np.zeros(self.size, dtype=dtypes.flags_dt)
        self.movement_cost = np.zeros(self.size, dtype=dtypes.movement_cost_dt)

        self.visible = np.zeros(self.size, dtype=np.bool)
        self.revealed = np.zeros(self.size, dtype=np.bool)

        self.entities = collections.defaultdict(EntitiesSet)

    @staticmethod
    def create(size, depth):
        map_id = uuid.uuid4()
        return GameMap(map_id, size, depth)

    def get_entities(self, position):
        return self.entities.get(position)

    def is_blocked(self, position):
        return self.flags[position] & Flag.BLOCKS_MOVEMENT

    def get_exits(self, position):
        # TODO: add movement_type argument and check only appopriate movement type related flag
        exits = set()
        for direction in Direction:
            target_position = position.move(direction)
            if not self.is_blocked(target_position):
                exits.add(direction)
        return exits

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

