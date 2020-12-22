import random

from . import components


ACTION_COST = 60


def random_move(ecs, actor):
    """Return random move direction from allowed exits."""
    locations = ecs.manage(components.Location)
    movement_directions = ecs.manage(components.WantsToMove)

    location = locations.get(actor)
    level = ecs.levels.get(location.level_id)
    exits = level.get_exits(location.position)
    direction = random.choice(list(exits))
    movement_directions.insert(actor, direction)

    return ACTION_COST


def perform_action(ecs, actor):
    return random_move(ecs, actor)

