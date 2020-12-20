import collections
import uuid

import numpy as np

from geometry import Direction, Position, Rectangle
import dtypes
from flags import Flag

    
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

        self.entities = collections.defaultdict(set)

    @staticmethod
    def create(size, depth):
        map_id = uuid.uuid4()
        return GameMap(map_id, size, depth)

    def get_exits(self, position):
        # TODO: add movement_type argument and check only appopriate movement type related flag
        exits = set()
        for direction in Direction:
            move_position = position.move(direction)
            if not self.flags[move_position] & Flag.BLOCKS_MOVEMENT:
                exits.add(direction)
        return exits


def generate(size):
    from terrain import Terrain

    level = GameMap.create(size, 0)
    level.terrain[:] = Terrain.STONE_WALL.id
    level.terrain[1:-1, 1:-1] = Terrain.STONE_FLOOR.id
    level.terrain[-3:-1, 1:-1] = Terrain.SHALLOW_WATER.id
    level.terrain[1: -1, level.height//2] = Terrain.STONE_WALL.id
    level.terrain[level.center] = Terrain.STONE_FLOOR.id
    level.terrain[level.width//4, level.height//2] = Terrain.STONE_FLOOR.id
    level.terrain[level.width//4*3, level.height//2] = Terrain.STONE_FLOOR.id

    return level

