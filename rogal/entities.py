import random

from . import components
from .renderable import RenderOrder
from .terrain import Terrain
from .tiles import TermTiles as tiles


"""Entities definition and creation."""

# Terrain

VOID = (
    components.Terrain(),
    components.Name('Empty void of darkness'),
    components.Renderable(tiles.VOID, RenderOrder.TERRAIN),
    components.BlocksVision(),
    components.BlocksMovement(),
)

STONE_WALL = (
    components.Terrain(),
    components.Name('Stone wall'),
    components.Renderable(tiles.STONE_WALL, RenderOrder.TERRAIN),
    components.BlocksVision(),
    components.BlocksMovement(),
)

STONE_FLOOR = (
    components.Terrain(),
    components.Name('Stone floor'),
    components.Renderable(tiles.STONE_FLOOR, RenderOrder.TERRAIN),
)

SHALLOW_WATER = (
    components.Terrain(),
    components.Name('Shallow water'),
    components.Renderable(tiles.SHALLOW_WATER, RenderOrder.TERRAIN),
)

ALL_TERRAIN = [
    (Terrain.VOID.id, VOID), 
    (Terrain.STONE_WALL.id, STONE_WALL),
    (Terrain.STONE_FLOOR.id, STONE_FLOOR),
    (Terrain.SHALLOW_WATER.id, SHALLOW_WATER),
]


# Foliage

# Props

OPEN_DOOR = (
    components.Prop(),
    components.Name('Open door'),
    components.Renderable(tiles.OPEN_DOOR, RenderOrder.PROPS),
)

CLOSED_DOOR = (
    components.Prop(),
    components.Name('Closed door'),
    components.Renderable(tiles.CLOSED_DOOR, RenderOrder.PROPS),
    components.BlocksMovement(),
    components.BlocksVision(),
    components.OnOperate(
        insert=OPEN_DOOR,
        remove=(
            components.BlocksVision, 
            components.BlocksMovement, 
            components.OnOperate,
        ),
    ),
)

# Items

# Actors

PLAYER = (
    components.Player(),
    components.Name('Player'),
    components.Renderable(tiles.PLAYER, RenderOrder.ACTORS),
    components.BlocksMovement(),
    components.Viewshed(view_range=12),
    components.WaitsForAction(1),
)

MONSTER = (
    components.Monster(),
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

def create(ecs, template, entity_id=None):
    return ecs.create(*template, entity_id=entity_id)


def spawn(ecs, entity, level_id, position):
    locations = ecs.manage(components.Location)
    locations.insert(entity, level_id, position)

