import numpy as np

import tcod

from . import components
from .flags import Flag, get_flags


"""Systems running ecs."""

# NOTE: For now just use <type>_system_run(ecs, level), make some classes later


def movement_system_run(ecs, level, *args, **kwargs):
    locations = ecs.manage(components.Location)
    movement_intents = ecs.manage(components.WantsToMove)
    for entity, location, direction in ecs.join(ecs.entities, locations, movement_intents):
        # Update position
        location.position = location.position.move(direction)
        # Invalidate visibility data
        vieshed = entity.get(components.Viewshed)
        if vieshed:
            vieshed.invalidate()
        # TODO: Add some HasMoved to flag to entity?
    movement_intents.clear()


def visibility_system_run(ecs, level, *args, **kwargs):
    players = ecs.manage(components.Player)
    viewsheds = ecs.manage(components.Viewshed)
    locations = ecs.manage(components.Location)
    for entity, location, viewshed in ecs.join(ecs.entities, locations, viewsheds):
        if not location.map_id == level.id:
            # Not on current map/level
            continue
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


def map_indexing_system_run(ecs, level, *args, **kwargs):
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
        if not location.map_id == level.id:
            # Not on current map/level
            continue

        # Update entities on location
        level.entities[location.position].add(entity)

        # Update flags
        entity_flags = get_flags(entity)
        level.flags[location.position] |= entity_flags

