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

    def run(self, ecs, *args, **kwargs):
        return

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class ActionsQueueSystem(System):

    INCLUDE_STATES = {
        RunState.TICKING, 
    }

    def run(self, ecs, *args, **kwargs):
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

    def run(self, ecs, *args, **kwargs):
        names = ecs.manage(components.Name)
        locations = ecs.manage(components.Location)
        movement = ecs.manage(components.WantsToMove)
        viewsheds = ecs.manage(components.Viewshed)
        for entity, location, direction in ecs.join(ecs.entities, locations, movement):
            log.info(f'{names.get(entity)} MOVE: {direction}')

            # Update position
            location.position = location.position.move(direction)

            # Invalidate visibility data
            vieshed = viewsheds.get(entity)
            if vieshed:
                vieshed.invalidate()
            # TODO: Add some HasMoved to flag to entity?

        # Clear processed movement
        movement.clear()


class MeleeCombatSystem(System):

    INCLUDE_STATES = {
        RunState.ACTION_PERFORMED, 
    }

    def run(self, ecs, *args, **kwargs):
        names = ecs.manage(components.Name)
        melee = ecs.manage(components.WantsToMelee)
        for entity, target_id in ecs.join(ecs.entities, melee):
            target = ecs.entities.get(target_id)
            log.info(f'{names.get(entity)} ATTACK: {names.get(target)}')
            # TODO: Do some damage!
            #particle = create_meele_hit_particle(ecs)
            #location = target.get(components.Location)
            #spawn(ecs, particle, location.level_id, location.position)

        # Clear processed melee
        melee.clear()



class VisibilitySystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN, 
        RunState.ACTION_PERFORMED, 
    }

    def run(self, ecs, *args, **kwargs):
        players = ecs.manage(components.Player)
        viewsheds = ecs.manage(components.Viewshed)
        locations = ecs.manage(components.Location)
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
                #algorithm=tcod.FOV_SHADOW,
                #algorithm=tcod.FOV_DIAMOND,
                #algorithm=tcod.FOV_RESTRICTIVE,
                #algorithm=tcod.FOV_PERMISSIVE(1),
                algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST,
            )

            viewshed.update(fov)
            if entity in players:
                # If player, update visible and revealed flags
                level.visible[:] = fov
                level.revealed |= fov


class MapIndexingSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN, 
        RunState.ACTION_PERFORMED, 
    }

    def run(self, ecs, *args, **kwargs):
        for level in ecs.levels:
            # Calculate base_flags if needed
            if not np.any(level.base_flags):
                for terrain_id in np.unique(level.terrain):
                    terrain_mask = level.terrain == terrain_id
                    terrain_flags = get_flags(ecs.entities.get(terrain_id))
                    level.base_flags[terrain_mask] = terrain_flags

            # Clear previous data
            level.entities.clear()
            level.flags[:] = level.base_flags

        locations = ecs.manage(components.Location)
        for entity, location in ecs.join(ecs.entities, locations):
            level = ecs.levels.get(location.level_id)

            # Update entities on location
            level.entities[location.position].add(entity)

            # Update flags
            entity_flags = get_flags(entity)
            level.flags[location.position] |= entity_flags


class ParticlesSystem(System):

    def run(self, ecs, *args, **kwargs):
        particles = ecs.manage(components.Particle)
        outdated = set()
        now = time.time()
        for entity, ttl in ecs.join(ecs.entities, particles):
            if ttl < now:
                outdated.add(entity)
        ecs.entities.remove(*outdated)

