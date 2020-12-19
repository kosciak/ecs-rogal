import components
from terrain import TerrainFlag

import numpy as np

import tcod


"""Systems running ecs."""

# NOTE: For now just use <type>_system_run(ecs, level), make some classes later


def movement_system_run(ecs, level):
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


def visibility_system_run(ecs, level):
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

        transparency = level.flags & TerrainFlag.BLOCK_VISION == 0
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
        if entity.has(components.Player):
            # If player, update visible and revealed flags
            level.visible[:] = fov
            level.revealed |= fov

