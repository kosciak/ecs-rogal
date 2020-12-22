import random

from . import components


def random_move(ecs, actor):
    """Return random move direction from allowed exits."""
    locations = ecs.manage(components.Location)
    movement = ecs.manage(components.WantsToMove)

    location = locations.get(actor)
    level = ecs.levels.get(location.level_id)
    exits = level.get_exits(location.position)
    direction = random.choice(list(exits))
    movement.insert(actor, direction)

    return 60


def perform_action(ecs, actor):
    return random_move(ecs, actor)

