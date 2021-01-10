import collections
import logging
import time

import numpy as np

import tcod

from . import components
from .entities import create_meele_hit_particle, spawn
from .flags import Flag, get_flags
from .run_state import RunState


log = logging.getLogger(__name__)


"""Systems running ecs."""

class System:

    INCLUDE_STATES = set()
    EXCLUDE_STATES = set()

    def should_run(self, state):
        if self.EXCLUDE_STATES and state in self.EXCLUDE_STATES:
            return False
        if self.INCLUDE_STATES and not state in self.INCLUDE_STATES:
            return False
        return True

    def run(self, ecs, state, *args, **kwargs):
        return

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class ActionsQueueSystem(System):

    INCLUDE_STATES = {
        RunState.TICKING,
    }

    def run(self, ecs, state, *args, **kwargs):
        acts_now = ecs.manage(components.ActsNow)
        waiting = ecs.manage(components.WaitsForAction)

        # Clear previous ActsNow flags
        acts_now.clear()

        for entity, waits in ecs.join(ecs.entities, waiting):
            # Decrease wait time
            waits -= 1
            if waits <= 0:
                # No more waiting, time for some action!
                acts_now.insert(entity)


class MovementSystem(System):

    INCLUDE_STATES = {
        RunState.ACTION_PERFORMED,
    }

    def apply_move(self, ecs, *args, **kwargs):
        names = ecs.manage(components.Name)
        locations = ecs.manage(components.Location)
        movement_directions = ecs.manage(components.WantsToMove)
        has_moved = ecs.manage(components.HasMoved)

        for entity, location, direction in ecs.join(ecs.entities, locations, movement_directions):
            log.info(f'{names.get(entity)} MOVE: {direction}')

            # Update position
            location.position = location.position.move(direction)
            has_moved.insert(entity)

        # Clear processed movement intents
        movement_directions.clear()

    def post_movement(self, ecs, *args, **kwargs):
        # Pocess effects of movement
        # Invalidate Viewshed after moving
        has_moved = ecs.manage(components.HasMoved)
        viewsheds = ecs.manage(components.Viewshed)

        for viewshed, moved in ecs.join(viewsheds, has_moved):
            viewshed.invalidate()

        # TODO: Other effects of movement

        # Clear processed has_moved
        has_moved.clear()

    def run(self, ecs, state, *args, **kwargs):
        self.apply_move(ecs, *args, **kwargs)
        self.post_movement(ecs, *args, **kwargs)


class MeleeCombatSystem(System):

    INCLUDE_STATES = {
        RunState.ACTION_PERFORMED,
    }

    def run(self, ecs, state, *args, **kwargs):
        names = ecs.manage(components.Name)
        melee_targets = ecs.manage(components.WantsToMelee)
        locations = ecs.manage(components.Location)

        for entity, target_id in ecs.join(ecs.entities, melee_targets):
            target = ecs.get(target_id)
            log.info(f'{names.get(entity)} ATTACK: {names.get(target)}')
            # TODO: Do some damage!
            particle = create_meele_hit_particle(ecs)
            location = locations.get(target)
            spawn(ecs, particle, location.level_id, location.position)

        # Clear processed targets
        melee_targets.clear()


class OperateSystem(System):

    INCLUDE_STATES = {
        RunState.ACTION_PERFORMED,
    }

    def run(self, ecs, state, *args, **kwargs):
        names = ecs.manage(components.Name)
        operate_targets = ecs.manage(components.WantsToOperate)
        operations = ecs.manage(components.OnOperate)
        blocks_vision_changes = ecs.manage(components.BlocksVisionChanged)

        for entity, target_id in ecs.join(ecs.entities, operate_targets):
            target = ecs.get(target_id)
            log.info(f'{names.get(entity)} OPERATE: {names.get(target)}')
            operation = operations.get(target)
            for component in operation.insert:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                manager = ecs.manage(component)
                manager.insert(target, component=component)
            for component in operation.remove:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                manager = ecs.manage(component)
                manager.remove(target)

        # Clear processed targets
        operate_targets.clear()


class VisibilitySystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN, 
        RunState.ACTION_PERFORMED, 
    }

    def apply_blocks_vision_changes(self, ecs, *args, **kwargs):
        blocks_vision_changes = ecs.manage(components.BlocksVisionChanged)
        locations = ecs.manage(components.Location)
        viewsheds = ecs.manage(components.Viewshed)

        # Invalidate Viewshed of all entities with target in viewshed
        positions_per_level = collections.defaultdict(set)
        for location, changed in ecs.join(locations, blocks_vision_changes):
            positions_per_level[location.level_id].add(location.position)

        viewsheds = ecs.manage(components.Viewshed)
        for viewshed, location in ecs.join(viewsheds, locations):
            if viewshed.visible_tiles & positions_per_level[location.level_id]:
                viewshed.invalidate()

        # Clear processed flags
        blocks_vision_changes.clear()

    def update_viewsheds(self, ecs, *args, **kwargs):
        players = ecs.manage(components.Player)
        locations = ecs.manage(components.Location)
        viewsheds = ecs.manage(components.Viewshed)

        #  Update Viesheds that needs update
        for entity, location, viewshed in ecs.join(ecs.entities, locations, viewsheds):
            level = ecs.levels.get(location.level_id)
            if not location.position in level:
                # Outside map/level boundaries
                continue
            if not viewshed.needs_update:
                # No need to recalculate
                continue

            transparency = level.flags & Flag.BLOCKS_VISION == 0
            pov = location.position
            fov = tcod.map.compute_fov(
                transparency, pov=pov, 
                radius=viewshed.view_range, 
                light_walls=True,
                algorithm=tcod.FOV_BASIC,
                #algorithm=tcod.FOV_SHADOW,
                #algorithm=tcod.FOV_DIAMOND,
                #algorithm=tcod.FOV_RESTRICTIVE,
                #algorithm=tcod.FOV_PERMISSIVE(1),
                #algorithm=tcod.FOV_PERMISSIVE(8),
                #algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST,
            )

            viewshed.update(fov)
            if entity in players:
                # If player, update visible and revealed flags
                level.visible[:] = fov
                level.revealed |= fov

    def run(self, ecs, state, *args, **kwargs):
        self.apply_blocks_vision_changes(ecs, *args, **kwargs)
        self.update_viewsheds(ecs, *args, **kwargs)


class MapIndexingSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.ACTION_PERFORMED,
    }

    def calculate_base_flags(self, ecs, level, *args, **kwargs):
        if not np.any(level.base_flags):
            for terrain_id in np.unique(level.terrain):
                terrain_mask = level.terrain == terrain_id
                terrain = ecs.get(terrain_id)
                terrain_flags = get_flags(ecs, terrain)
                level.base_flags[terrain_mask] = terrain_flags

    def clear_flags(self, ecs, *args, **kwargs):
        for level in ecs.levels:
            # Calculate base_flags if needed
            self.calculate_base_flags(ecs, level, *args, **kwargs)

            # Clear previous data
            level.entities.clear()
            level.flags[:] = level.base_flags

    def update_indexes(self, ecs, *args, **kwargs):
        locations = ecs.manage(components.Location)

        for entity, location in ecs.join(ecs.entities, locations):
            level = ecs.levels.get(location.level_id)

            # Update entities on location
            level.entities[location.position].add(entity)

            # Update flags
            entity_flags = get_flags(ecs, entity)
            level.flags[location.position] |= entity_flags

    def run(self, ecs, state, *args, **kwargs):
        self.clear_flags(ecs, *args, **kwargs)
        self.update_indexes(ecs, *args, **kwargs)


class ParticlesSystem(System):

    INCLUDE_STATES = {
        #RunState.TICKING,
        RunState.WAITING_FOR_INPUT,
        RunState.ANIMATIONS,
    }

    def run(self, ecs, state, *args, **kwargs):
        particles = ecs.manage(components.Particle)
        outdated = set()
        now = time.time()
        for entity, ttl in ecs.join(ecs.entities, particles):
            if ttl < now:
                outdated.add(entity)
        ecs.entities.remove(*outdated)

