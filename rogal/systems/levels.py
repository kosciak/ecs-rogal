import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class LevelsSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs, level_generator):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial
        self.level_generator = level_generator

    def run(self):
        wants_to_change_level = self.ecs.manage(components.WantsToChangeLevel)
        levels = self.ecs.manage(components.Level)
        locations = self.ecs.manage(components.Location)
        has_moved = self.ecs.manage(components.HasMoved)

        for entity, level_id in wants_to_change_level:
            level_id = level_id or int(self.level_generator.init_level())
            populated = level_id in levels
            level_id, starting_position = self.level_generator.generate(
                level_id=level_id, populated=populated)
            prev_location = locations.get(entity)
            if prev_location:
                self.spatial.remove_entity(entity, prev_location)
            location = locations.insert(entity, level_id, starting_position)
            self.spatial.add_entity(entity, location)
            has_moved.insert(entity)

        wants_to_change_level.clear()

