import uuid

import numpy as np

from geometry import WithSizeMixin

import dtypes

    
class GameMap(WithSizeMixin):

    def __init__(self, map_id, size, depth):
        self.id = map_id

        self.size = size
        self.depth = depth

        self.terrain = np.zeros(self.size, dtype=dtypes.terrain_id_dt)

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


def generate(size):
    from terrain import Terrain

    level = GameMap.create(size, 0)
    level.terrain[:] = Terrain.STONE_WALL.id
    level.terrain[1:-1, 1:-1] = Terrain.STONE_FLOOR.id

    return level


def render(level, panel):
    from terrain import Terrain
    from renderable import Tile
    from geometry import Position

    tiles = {
        Terrain.STONE_WALL.id:     Tile.create('#', fg=3),
        Terrain.STONE_FLOOR.id:    Tile.create('.', fg=7),
    }

    for tile_id in np.unique(level.terrain):
        mask = level.terrain == tile_id
        tile = tiles.get(tile_id)
        center = panel.center
        position = Position(center.x-level.width/2, center.y-level.height/2)
        panel.mask(tile, mask, position)

