import collections
import logging

import numpy as np

from .bitmask import bitmask_8bit
from . import components
from . import dtypes
from .ecs import EntitiesSet
from .flags import Flag
from .geometry import Direction


log = logging.getLogger(__name__)


class SpatialIndex:

    """Spatial index - central API for level related indexes (flags and entities)."""

    def __init__(self, ecs):
        self.ecs = ecs
        self.levels = self.ecs.manage(components.Level)

        # flags.Flags bitmasks calculated from level's terrain
        self._terrain_flags = {}
        # flags.Flags bitmasks calculated from entities
        self._entities_flags = {}
        # all entites per level
        self._entities = collections.defaultdict(EntitiesSet)
        # all entities per position per level
        self._entities_positions = collections.defaultdict(lambda: collections.defaultdict(EntitiesSet))

    @staticmethod
    def init_flags(size):
        """Init flags array."""
        flags = np.zeros(size, dtype=dtypes.flags_dt)
        return flags

    @staticmethod
    def init_terrain(size):
        """Init terrain tiles array."""
        terrain = np.zeros(size, dtype=dtypes.terrain_dt)
        return terrain

    def create_level(self, level_id, depth, terrain):
        """Create Level entity and add to ECS."""
        level = components.Level(depth, terrain)
        return self.ecs.create(level, entity_id=level_id)

    def get_level(self, level_id):
        """Get Level with given ID."""
        return self.levels.get(level_id)

    # TODO: destroy_level(self, level_id):

    def terrain_type(self, level_id, terrain_type):
        """Return boolean mask of tiles with given terrain Type."""
        level = self.get_level(level_id)
        return level.terrain >> 4 == terrain_type

    def calculate_terrain_flags(self, level_id):
        """Calculated flags based on level's terrain tiles."""
        log.debug(f'SpatialIndex.calculate_terrain_flags(level_id={level_id.short_id!r})')
        blocks_vision = self.ecs.manage(components.BlocksVision)
        blocks_movement = self.ecs.manage(components.BlocksMovement)

        level = self.get_level(level_id)
        terrain_flags = self.init_flags(level.size)
        for terrain in np.unique(level.terrain):
            terrain_mask = level.terrain == terrain
            flags = blocks_vision.get(terrain, 0) | blocks_movement.get(terrain, 0)
            terrain_flags[terrain_mask] = flags

        return terrain_flags

    def terrain_flags(self, level_id):
        """Return terrain flags for given Level."""
        terrain_flags = self._terrain_flags.get(level_id)
        if terrain_flags is None:
            terrain_flags = self.calculate_terrain_flags(level_id)
            self._terrain_flags[level_id] = terrain_flags
        return terrain_flags

    def calculate_entities(self):
        """Calculate entities indexes."""
        log.debug(f'SpatialIndex.calculate_entities()')
        locations = self.ecs.manage(components.Location)
        for entity, location in locations:
            self._entities[location.level_id].add(entity)
            self._entities_positions[location.level_id][location.position].add(entity)

    def entities(self, level_id):
        """Get all entities on given Level."""
        return self._entities[level_id]

    def get_entities(self, location, position=None):
        """Get entitities on given Location."""
        return self._entities_positions[location.level_id][position or location.position]

    def calculate_entities_flags(self, level_id):
        """Calculate entities flags for given Level."""
        log.debug(f'SpatialIndex.calculate_entities_flags(level_id={level_id.short_id!r})')
        blocks_vision = self.ecs.manage(components.BlocksVision)
        blocks_movement = self.ecs.manage(components.BlocksMovement)

        level = self.get_level(level_id)
        entities_flags = self.init_flags(level.size)
        if not (blocks_vision or blocks_movement):
            return entities_flags

        locations = self.ecs.manage(components.Location)
        for entity, flag, location in self.ecs.join(self.entities(level_id), blocks_vision, locations):
            entities_flags[location.position] |= flag
        for entity, flag, location in self.ecs.join(self.entities(level_id), blocks_movement, locations):
            entities_flags[location.position] |= flag

        return entities_flags

    def entities_flags(self, level_id):
        """Return entities flags for given Level."""
        entities_flags = self._entities_flags.get(level_id)
        if entities_flags is None:
            entities_flags = self.calculate_entities_flags(level_id)
            self._entities_flags[level_id] = entities_flags
        return entities_flags

    def calculate_entities_flags_position(self, level_id, position):
        """Calculate flags for entities on given Location."""
        blocks_vision = self.ecs.manage(components.BlocksVision)
        blocks_movement = self.ecs.manage(components.BlocksMovement)
        flags = 0
        for entity in self._entities_positions[level_id][position]:
            flags |= blocks_vision.get(entity, 0) | blocks_movement.get(entity, 0)
        self.entities_flags(level_id)[position] = flags

    def transparent(self, level_id):
        """Return boolean mask of transparent tiles."""
        terrain_flags = self.terrain_flags(level_id)
        entities_flags = self.entities_flags(level_id)
        return (terrain_flags | entities_flags) & Flag.BLOCKS_VISION == 0

    def walkable(self, level_id):
        """Return boolean mask of walkable tiles."""
        terrain_flags = self.terrain_flags(level_id)
        entities_flags = self.entities_flags(level_id)
        return (terrain_flags | entities_flags) & Flag.BLOCKS_VISION == 0

    def revealable(self, level_id):
        """Return boolean mask of revealable tiles (transparent tiles and their neighbours)."""
        non_transparent_bitmask = bitmask_8bit(~self.transparent(level_id), pad_value=True)
        revealable = non_transparent_bitmask < 255
        return revealable

    def is_movement_blocked(self, location, position=None):
        """Return True if given position allows movement."""
        position = position or location.position
        terrain_flags = self.terrain_flags(location.level_id)
        entities_flags = self.entities_flags(location.level_id)
        return (terrain_flags[position] | entities_flags[position]) & Flag.BLOCKS_MOVEMENT

    def get_exits(self, location):
        """Return all available exit directions from given position."""
        # TODO: add movement_type argument and check only appopriate movement type related flag?
        exits = set()
        for direction in Direction:
            target_position = location.position.move(direction)
            if not self.is_movement_blocked(location, target_position):
                exits.add(direction)
        return exits

    def update_entity(self, entity, location, prev_position=None):
        """Update entity related indexes, and recalculate entities flags."""
        if prev_position:
            self.get_entities(location, prev_position).discard(entity)
            self.calculate_entities_flags_position(location.level_id, prev_position)
        self.get_entities(location).add(entity)
        self.calculate_entities_flags_position(location.level_id, location.position)

    def remove_entity(self, entity, location):
        """Remove entity from Location."""
        self.entities(location.level_id).discard(entity)
        self.get_entities(location).discard(entity)
        self.calculate_entities_flags_position(location.level_id, location.position)

    def add_entity(self, entity, location):
        """Add entity to Location."""
        self.entities(location.level_id).add(entity)
        self.update_entity(entity, location)

