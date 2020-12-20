import components
from renderable import RenderOrder
from terrain import Terrain
import tiles


"""Entities definition and creation."""

# Terrain

def create_terrain(ecs):
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
        components.Name('Player'),
        components.Renderable(tiles.PLAYER, RenderOrder.ACTORS),
        components.Viewshed(view_range=12),
    )

def create_monster(ecs):
    return ecs.create(
        components.Monster(),
        components.Name('Generic monster'),
        components.Renderable(tiles.MONSTER, RenderOrder.ACTORS),
        components.BlocksMovement(),
        components.Viewshed(view_range=12),
    )


# functions

def spawn(ecs, entity, level, position):
    locations = ecs.manage(components.Location)
    location = components.Location(level.id, position)
    locations.insert(entity, location)

