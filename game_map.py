import uuid

import numpy as np

from geometry import WithSizeMixin

import dtypes

    
class GameMap(WithSizeMixin):

    def __init__(self, map_id, size, depth):
        self.id = map_id

        self.size = size
        self.depth = depth

        self.terrain_tiles = np.zeros(self.size, dtype=dtypes.terrain_tile_dt)
        self.terrain_ids = self.terrain_tiles.view(dtype=dtypes.terrain_id_dt)

        self.base_flags = np.zeros(self.size, dtype=dtypes.flags_dt)
        self.base_movement_cost = np.zeros(self.size, dtype=dtypes.movement_cost_dt)

        self.flags = np.zeros(self.size, dtype=dtypes.flags_dt)
        self.movement_cost = np.zeros(self.size, dtype=dtypes.movement_cost_dt)

        self.visible = np.zeros(self.size, dtype=np.bool)
        self.revealed = np.zeros(self.size, dtype=np.bool)

    @staticmethod
    def create(size, depth):
        map_id = uuid.uuid4()
        return GameMap(map_id, size, depth)


