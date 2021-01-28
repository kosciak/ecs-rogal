import collections
import logging
import time

import numpy as np

import tcod

from . import components
from .ecs import System
from .ecs import EntitiesSet
from .run_state import RunState

from .utils import perf


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


"""Systems running ecs."""


class ActionsQueueSystem(System):

    INCLUDE_STATES = {
        RunState.TICKING,
    }

    def update_acts_now(self, *args, **kwargs):
        acts_now = self.ecs.manage(components.ActsNow)
        waiting_queue = self.ecs.manage(components.WaitsForAction)

        # Clear previous ActsNow flags
        acts_now.clear()

        for entity, waits in self.ecs.join(self.ecs.entities, waiting_queue):
            # Decrease wait time
            waits -= 1
            if waits <= 0:
                # No more waiting, time for some action!
                acts_now.insert(entity)

    def run(self, state, *args, **kwargs):
        with perf.Perf('systems.ActionsQueueSystem.run()'):
            self.update_acts_now(*args, **kwargs)


class MovementSystem(System):

    INCLUDE_STATES = {
        RunState.ACTION_PERFORMED,
    }

    def __init__(self, ecs, spatial):
        super().__init__(ecs)
        self.spatial = spatial

    def apply_move(self, *args, **kwargs):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        locations = self.ecs.manage(components.Location)
        movement_directions = self.ecs.manage(components.WantsToMove)
        has_moved = self.ecs.manage(components.HasMoved)

        for entity, location, direction in self.ecs.join(self.ecs.entities, locations, movement_directions):
            if entity in players:
                msg_log.info(f'{names.get(entity)} MOVE: {direction}')

            # Update position
            from_position = location.position
            location.position = location.position.move(direction)
            self.spatial.update_entity(entity, location, from_position)
            has_moved.insert(entity)

        # Clear processed movement intents
        movement_directions.clear()

    def run(self, state, *args, **kwargs):
        with perf.Perf('systems.MovementSystem.run()'):
            self.apply_move(*args, **kwargs)


class MeleeCombatSystem(System):

    INCLUDE_STATES = {
        RunState.ACTION_PERFORMED,
    }

    def __init__(self, ecs, spawner):
        super().__init__(ecs)
        self.spawner = spawner

    def run(self, state, *args, **kwargs):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        melee_targets = self.ecs.manage(components.WantsToMelee)
        locations = self.ecs.manage(components.Location)

        for entity, target in self.ecs.join(self.ecs.entities, melee_targets):
            if entity in players or target in players:
                msg_log.info(f'{names.get(entity)} ATTACK: {names.get(target)}')
            # TODO: Do some damage!
            location = locations.get(target)
            self.spawner.create_and_spawn('particles.HIT_PARTICLE', location.level_id, location.position)

        # Clear processed targets
        melee_targets.clear()


class OperateSystem(System):

    INCLUDE_STATES = {
        RunState.ACTION_PERFORMED,
    }

    def run(self, state, *args, **kwargs):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        operate_targets = self.ecs.manage(components.WantsToOperate)
        operations = self.ecs.manage(components.OnOperate)
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)

        for entity, target in self.ecs.join(self.ecs.entities, operate_targets):
            target = self.ecs.get(target)
            if entity in players:
                msg_log.info(f'{names.get(entity)} OPERATE: {names.get(target)}')
            operation = operations.get(target)
            for component in operation.insert:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                if component == components.BlocksMovement:
                    blocks_movement_changes.insert(target)
                manager = self.ecs.manage(component)
                manager.insert(target, component=component)
            for component in operation.remove:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                if component == components.BlocksMovement:
                    blocks_movement_changes.insert(target)
                manager = self.ecs.manage(component)
                manager.remove(target)

        # Clear processed targets
        operate_targets.clear()


class VisibilitySystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.ACTION_PERFORMED,
    }

    def __init__(self, ecs, spatial):
        super().__init__(ecs)
        self.spatial = spatial

    # TODO: rename this method!
    def invalidate_blocks_vision_changed_viewsheds(self, *args, **kwargs):
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
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

    def invalidate_has_moved_viewsheds(self, *args, **kwargs):
        # Invalidate Viewshed after moving
        has_moved = self.ecs.manage(components.HasMoved)
        viewsheds = self.ecs.manage(components.Viewshed)

        for viewshed, moved in self.ecs.join(viewsheds, has_moved):
            viewshed.invalidate()

    def update_viewsheds(self, *args, **kwargs):
        players = self.ecs.manage(components.Player)
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)
        level_memories = self.ecs.manage(components.LevelMemory)

        #  Update Viesheds that needs update
        for entity, location, viewshed in self.ecs.join(self.ecs.entities, locations, viewsheds):
            if not viewshed.needs_update:
                # No need to recalculate
                continue

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

    def spotted_alert(self, *args, **kwargs):
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

    def run(self, state, *args, **kwargs):
        with perf.Perf('systems.VisibilitySystem.run()'):
            self.invalidate_blocks_vision_changed_viewsheds(*args, **kwargs)
            self.invalidate_has_moved_viewsheds(*args, **kwargs)
            self.update_viewsheds(*args, **kwargs)
            with perf.Perf('systems.VisibilitySystem.spotted_targets()'):
                self.spotted_alert(*args, **kwargs)


class IndexingSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.ACTION_PERFORMED,
    }

    def __init__(self, ecs, spatial):
        super().__init__(ecs)
        self.spatial = spatial

    def calculate_spatial(self, *args, **kwargs):
        if not self.spatial._entities:
            self.spatial.calculate_entities()

    def update_flags(self, *args, **kwargs):
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        locations = self.ecs.manage(components.Location)

        for entity, location in self.ecs.join(blocks_vision_changes.entities, locations):
            self.spatial.update_entity(entity, location)

        for entity, location in self.ecs.join(blocks_movement_changes.entities, locations):
            self.spatial.update_entity(entity, location)

    def run(self, state, *args, **kwargs):
        with perf.Perf('systems.IndexingSystem.run()'):
            self.calculate_spatial(*args, **kwargs)
            self.update_flags(*args, **kwargs)


class QueuecCleanupSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.ACTION_PERFORMED,
    }

    def run(self, state, *args, **kwargs):
        has_moved = self.ecs.manage(components.HasMoved)
        has_moved.clear()

        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_vision_changes.clear()

        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        blocks_movement_changes.clear()


class ParticlesSystem(System):

    INCLUDE_STATES = {
        RunState.TICKING,
        RunState.WAITING_FOR_INPUT,
        RunState.ANIMATIONS,
    }

    def __init__(self, ecs, spatial):
        super().__init__(ecs)
        self.spatial = spatial

    def run(self, state, *args, **kwargs):
        particles = self.ecs.manage(components.Particle)
        outdated = EntitiesSet()
        now = time.time()
        for entity, ttl in self.ecs.join(self.ecs.entities, particles):
            if ttl < now:
                outdated.add(entity)

        locations = self.ecs.manage(components.Location)
        for entity, location in self.ecs.join(outdated, locations):
            self.spatial.remove_entity(entity, location)
        self.ecs.entities.remove(*outdated)

