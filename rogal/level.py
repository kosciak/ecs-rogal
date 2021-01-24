import collections
import uuid

import numpy as np

from . import dtypes
from .ecs import EntitiesSet
from .flags import Flag, get_flags
from .bitmask import bitmask_8bit
from .geometry import Rectangular, Direction, Position


class Level(Rectangular):

    position = Position.ZERO

    def __init__(self, level_id, size, depth):
        self.id = level_id

        self.size = size
        self.depth = depth

        self.terrain = np.zeros(self.size, dtype=dtypes.terrain_id_dt)

        # base_* indexes - calculated from terrain
        self.base_flags = np.zeros(self.size, dtype=dtypes.flags_dt)
        self.base_movement_cost = np.zeros(self.size, dtype=dtypes.movement_cost_dt)

        # NOTE: entities and indexes depend on MapIndexingSystem
        self.entities = collections.defaultdict(EntitiesSet)

        # calculated from base_* indexes and entities
        self.flags = np.zeros(self.size, dtype=dtypes.flags_dt)
        self.movement_cost = np.zeros(self.size, dtype=dtypes.movement_cost_dt)

    @staticmethod
    def create(size, depth):
        level_id = uuid.uuid4()
        return Level(level_id, size, depth)

    def calculate_base(self, ecs):
        """Calculate base_* indexes if needed."""
        if not np.any(self.base_flags):
            for terrain in np.unique(self.terrain):
                terrain_mask = self.terrain == terrain
                terrain_flags = get_flags(ecs, terrain)
                self.base_flags[terrain_mask] = terrain_flags

    def clear(self):
        """Clear indexes."""
        self.entities.clear()
        self.flags[:] = self.base_flags

    @property
    def transparent(self):
        """Return boolean mask of transparent tiles."""
        return self.flags & Flag.BLOCKS_VISION == 0

    @property
    def revealable(self):
        """Return boolean mask of revealable tiles (transparent tiles and their neighbours)."""
        non_transparent_bitmask = bitmask_8bit(~self.transparent, pad_value=True)
        revealable = non_transparent_bitmask < 255
        return revealable

    def get_entities(self, *positions):
        """Return entities on given position."""
        entities = EntitiesSet()
        for position in positions:
            entities.update(self.entities[position])
        return entities

    def is_movement_allowed(self, position):
        """Return True if given position allows movement."""
        return not self.flags[position] & Flag.BLOCKS_MOVEMENT

    def get_exits(self, position):
        """Return all available exit directions from given position."""
        # TODO: add movement_type argument and check only appopriate movement type related flag
        exits = set()
        for direction in Direction:
            target_position = position.move(direction)
            if self.is_movement_allowed(target_position):
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

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id} depth={self.depth} size={self.size}>'

