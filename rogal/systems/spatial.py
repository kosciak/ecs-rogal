import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class IndexingSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def calculate_spatial(self):
        # TODO: This will work for already created entities, what about generating new level?
        if not self.spatial._entities:
            self.spatial.calculate_entities()

    def update_flags(self):
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        locations = self.ecs.manage(components.Location)

        for entity, location in self.ecs.join(blocks_vision_changes.entities, locations):
            self.spatial.update_entity(entity, location)

        for entity, location in self.ecs.join(blocks_movement_changes.entities, locations):
            self.spatial.update_entity(entity, location)

    def run(self):
        self.calculate_spatial()
        self.update_flags()

