import random

from . import components
from .renderable import RenderOrder
from .terrain import Terrain
from .tiles import TermTiles as tiles


"""Entities definition and creation."""

# Terrain

def create_all_terrains(ecs):
    ecs.create(
        components.Terrain(),
        components.Name('Empty void of darkness'),
        components.Renderable(tiles.VOID, RenderOrder.TERRAIN),
        components.BlocksVision(),
        components.BlocksMovement(),
        entity_id=Terrain.VOID.id
    )

    ecs.create(
        components.Terrain(),
        components.Name('Stone wall'),
        components.Renderable(tiles.STONE_WALL, RenderOrder.TERRAIN),
        components.BlocksVision(),
        components.BlocksMovement(),
        entity_id=Terrain.STONE_WALL.id
    )

    ecs.create(
        components.Terrain(),
        components.Name('Stone floor'),
        components.Renderable(tiles.STONE_FLOOR, RenderOrder.TERRAIN),
        entity_id=Terrain.STONE_FLOOR.id
    )

    ecs.create(
        components.Terrain(),
        components.Name('Shallow water'),
        components.Renderable(tiles.SHALLOW_WATER, RenderOrder.TERRAIN),
        entity_id=Terrain.SHALLOW_WATER.id
    )


# Foliage

# Props

# Items

# Actors

def create_player(ecs):
    return ecs.create(
        components.Player(),
        components.Actor(),
        components.Name('Player'),
        components.Renderable(tiles.PLAYER, RenderOrder.ACTORS),
        components.BlocksMovement(),
        components.Viewshed(view_range=12),
        components.WaitsForAction(1),
    )

def create_monster(ecs):
    return ecs.create(
        components.Monster(),
        components.Actor(),
        components.Name('Monster'),
        components.Renderable(tiles.MONSTER, RenderOrder.ACTORS),
        components.BlocksMovement(),
        components.Viewshed(view_range=12),
        components.WaitsForAction(random.randint(2,10)),
    )


# Particles

def create_particle(ecs, tile, ttl):
    return ecs.create(
        components.Particle(ttl),
        components.Renderable(tile, RenderOrder.PARTICLES),
    )

def create_meele_hit_particle(ecs):
    return create_particle(ecs, tiles.MEELE_HIT, .05)


# functions

def spawn(ecs, entity, level_id, position):
    locations = ecs.manage(components.Location)
    locations.insert(entity, level_id, position)

