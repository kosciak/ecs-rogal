import logging
import time

import numpy as np

import tcod

from . import components
from .entities import create_meele_hit_particle, spawn
from .flags import Flag, get_flags


log = logging.getLogger('rogal.systems')


"""Systems running ecs."""

# NOTE: For now just use <type>_system_run(ecs), make some classes later


def actions_queue_system_run(ecs, *args, **kwargs):
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


def movement_system_run(ecs, *args, **kwargs):
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


def melee_system_run(ecs, *args, **kwargs):
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



def visibility_system_run(ecs, *args, **kwargs):
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


def map_indexing_system_run(ecs, *args, **kwargs):
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


def particle_system_run(ecs, *args, **kwargs):
    particles = ecs.manage(components.Particle)
    outdated = set()
    now = time.time()
    for entity, ttl in ecs.join(ecs.entities, particles):
        if ttl < now:
            outdated.add(entity)
    ecs.entities.remove(*outdated)

