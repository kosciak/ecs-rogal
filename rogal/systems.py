import collections
import logging
import time

import numpy as np

import tcod

from . import components
from .ecs import System
from .ecs import EntitiesSet
from .flags import Flag, get_flags
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
            to_position = from_position.move(direction)
            level = self.ecs.levels.get(location.level_id)
            level.move_entity(self.ecs, entity, from_position, to_position)
            location.position = to_position
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

    def apply_blocks_vision_changes(self, *args, **kwargs):
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

    def invalidate_viewsheds(self, *args, **kwargs):
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
            level = self.ecs.levels.get(location.level_id)

            fov = tcod.map.compute_fov(
                transparency=level.transparent,
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
                memory = level_memories.get(entity)
                memory.update(level, fov)

    def spotted_alert(self, *args, **kwargs):
        # NOTE: It's SLOOOOOOOOOOOW!!! Use only for player for now, needs rewrite anyway
        players = self.ecs.manage(components.Player)
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)

        for entity, location, viewshed in self.ecs.join(players.entities, locations, viewsheds):
            level = self.ecs.levels.get(location.level_id)

            # This! This is the part that is very costly
            visible_entities = level.get_entities(*viewshed.positions)
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
            self.apply_blocks_vision_changes(*args, **kwargs)
            self.invalidate_viewsheds(*args, **kwargs)
            self.update_viewsheds(*args, **kwargs)
            with perf.Perf('systems.VisibilitySystem.spotted_targets()'):
                self.spotted_alert(*args, **kwargs)


class IndexingSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.ACTION_PERFORMED,
    }

    def calculate_base_indexes(self, *args, **kwargs):
        for level in self.ecs.levels:
            # Calculate base_flags if needed
            level.calculate_base(self.ecs)

    def calculate_indexes(self, *args, **kwargs):
        needs_update = set()
        for level in self.ecs.levels:
            if not level.entities:
                needs_update.add(level.id)

        if not needs_update:
            return

        locations = self.ecs.manage(components.Location)

        for entity, location in self.ecs.join(self.ecs.entities, locations):
            if not location.level_id in needs_update:
                continue
            level = self.ecs.levels.get(location.level_id)
            level.update_entity(self.ecs, entity, location.position)

    def update_flags(self, *args, **kwargs):
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        locations = self.ecs.manage(components.Location)

        for entity, location in self.ecs.join(blocks_vision_changes.entities, locations):
            level = self.ecs.levels.get(location.level_id)
            flags = get_flags(self.ecs, entity)
            prev_flags = flags ^ Flag.BLOCKS_VISION
            level.update_entity(self.ecs, entity, location.position, prev_flags)

        for entity, location in self.ecs.join(blocks_movement_changes.entities, locations):
            level = self.ecs.levels.get(location.level_id)
            flags = get_flags(self.ecs, entity)
            prev_flags = flags ^ Flag.BLOCKS_MOVEMENT
            level.update_entity(self.ecs, entity, location.position, prev_flags)

    def run(self, state, *args, **kwargs):
        with perf.Perf('systems.IndexingSystem.run()'):
            self.calculate_base_indexes(*args, **kwargs)
            self.calculate_indexes(*args, **kwargs)
            self.update_flags(*args, **kwargs)


class QueuecCleanupSystem(System):

    def run(self, state, *args, **kwargs):
        has_moved = self.ecs.manage(components.HasMoved)
        has_moved.clear()

        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_vision_changes.clear()

        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        blocks_movement_changes.clear()


class ParticlesSystem(System):

    INCLUDE_STATES = {
        #RunState.TICKING,
        RunState.WAITING_FOR_INPUT,
        RunState.ANIMATIONS,
    }

    def run(self, state, *args, **kwargs):
        particles = self.ecs.manage(components.Particle)
        outdated = EntitiesSet()
        now = time.time()
        for entity, ttl in self.ecs.join(self.ecs.entities, particles):
            if ttl < now:
                outdated.add(entity)

        locations = self.ecs.manage(components.Location)
        for entity, location in self.ecs.join(outdated, locations):
            level = self.ecs.levels.get(location.level_id)
            level.remove_entity(self.ecs, entity, location.position)
        self.ecs.entities.remove(*outdated)

