import logging

from ..utils import perf

from ..ecs import System
from ..ecs.run_state import RunState

from ..components import (
    BlocksVisionChanged,
    BlocksMovementChanged,
    Location,
)


log = logging.getLogger(__name__)


class SpatialIndexingSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def run(self):
        blocks_vision_changes = self.ecs.manage(BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(BlocksMovementChanged)
        locations = self.ecs.manage(Location)

        for entity, location in self.ecs.join(blocks_vision_changes.entities, locations):
            self.spatial.update_entity(entity, location)

        for entity, location in self.ecs.join(blocks_movement_changes.entities, locations):
            self.spatial.update_entity(entity, location)

