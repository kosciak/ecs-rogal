import components
from renderable import RenderOrder
import tiles


"""Entities definition and creation."""


def create_player(ecs):
    return ecs.create(
        components.Player(),
        components.Name('Player'),
        components.Renderable(tiles.PLAYER, RenderOrder.ACTORS),
        components.Viewshed(view_range=8),
    )

def create_monster(ecs):
    return ecs.create(
        components.Monster(),
        components.Name('Generic monster'),
        components.Renderable(tiles.MONSTER, RenderOrder.ACTORS),
        components.Viewshed(view_range=8),
    )


def spawn(ecs, entity, level, position):
    locations = ecs.manage(components.Location)
    location = components.Location(level.id, position)
    locations.insert(entity, location)

