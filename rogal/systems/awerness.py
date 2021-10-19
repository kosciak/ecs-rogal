import collections
import logging

import tcod.map

from .. import components
from ..ecs import System, EntitiesSet
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


class InvalidateViewshedsSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def on_blocks_vision_changed(self):
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        if not blocks_vision_changes:
            return
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)

        # Invalidate Viewshed of all entities with target in viewshed
        positions_per_level = collections.defaultdict(set)
        for entity, location in self.ecs.join(blocks_vision_changes.entities, locations):
            positions_per_level[location.level_id].add(location.position)

        if not positions_per_level:
            return

        viewsheds = self.ecs.manage(components.Viewshed)
        for viewshed, location in self.ecs.join(viewsheds, locations):
            if viewshed.positions & positions_per_level[location.level_id]:
                viewshed.invalidate()

    def on_has_moved(self):
        # Invalidate Viewshed after moving
        has_moved = self.ecs.manage(components.HasMoved)
        if not has_moved:
            return
        viewsheds = self.ecs.manage(components.Viewshed)

        for entity, viewshed in self.ecs.join(has_moved.entities, viewsheds):
            viewshed.invalidate()

    def run(self):
        self.on_blocks_vision_changed()
        self.on_has_moved()


class RevealLevelSystem(System):

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
        # RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def run(self):
        wants_to_reveal = self.ecs.manage(components.WantsToRevealLevel)
        if not wants_to_reveal:
            return
        level_memories = self.ecs.manage(components.LevelMemory)
        locations = self.ecs.manage(components.Location)

        for entity, memory, location in self.ecs.join(wants_to_reveal.entities, level_memories, locations):
            memory.update(location.level_id, self.spatial.revealable(location.level_id))
            msg_log.warning('Level revealed!')

        wants_to_reveal.clear()


class VisibilitySystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def update_viewsheds(self):
        players = self.ecs.manage(components.Player)
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)
        level_memories = self.ecs.manage(components.LevelMemory)

        #  Update Viesheds that needs update
        for entity, location, viewshed in self.ecs.join(self.ecs.entities, locations, viewsheds):
            if not viewshed.needs_update:
                # No need to recalculate
                continue

            # TODO: Move to separate module?
            fov = tcod.map.compute_fov(
                transparency=self.spatial.transparent(location.level_id),
                pov=location.position,
                radius=viewshed.view_range,
                light_walls=True,
                # algorithm=tcod.FOV_BASIC,
                # algorithm=tcod.FOV_SHADOW,
                # algorithm=tcod.FOV_DIAMOND,
                algorithm=tcod.FOV_RESTRICTIVE,
                # algorithm=tcod.FOV_PERMISSIVE(1),
                # algorithm=tcod.FOV_PERMISSIVE(8),
                # algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST,
            )

            viewshed.update(fov)

            memory = level_memories.get(entity)
            if memory:
                memory.update(location.level_id, fov)

    def spotted_alert(self):
        # NOTE: It's SLOOOOOOOOOOOW!!! Use only for player for now, needs rewrite anyway
        players = self.ecs.manage(components.Player)
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)

        # for entity, location, viewshed in self.ecs.join(self.ecs.entities, locations, viewsheds):
        for entity, location, viewshed in self.ecs.join(players.entities, locations, viewsheds):

            # This! This is the part that is very costly
            visible_entities = EntitiesSet()
            visible_entities.update(*[entities for entities in
                                      [self.spatial.get_entities(location, position)
                                       for position in viewshed.positions]])
            spotted_entities = EntitiesSet(visible_entities - viewshed.entities)
            viewshed.entities = visible_entities

            if spotted_entities and entity in players:
                names = self.ecs.manage(components.Name)
                monsters = self.ecs.manage(components.Monster)
                spotted_targets = []
                for target, is_monster, name in self.ecs.join(spotted_entities, monsters, names):
                    spotted_targets.append(name)
                if spotted_targets:
                    names = ', '.join(spotted_targets)
                    msg_log.info(f'You see: {names}')

    def run(self):
        self.update_viewsheds()
        with perf.Perf(self.spotted_alert):
            self.spotted_alert()

