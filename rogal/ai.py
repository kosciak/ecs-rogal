import random

from . import components


ACTION_COST = 60


def get_movement_cost(ecs, actor):
    movement_speed = ecs.manage(components.MovementSpeed)
    return movement_speed.get(actor) or ACTION_COST


def random_move(ecs, actor):
    """Return random move direction from allowed exits."""
    locations = ecs.manage(components.Location)
    movement_directions = ecs.manage(components.WantsToMove)

    location = locations.get(actor)
    level = ecs.levels.get(location.level_id)
    exits = level.get_exits(location.position)
    direction = random.choice(list(exits))
    movement_directions.insert(actor, direction)

    return get_movement_cost(ecs, actor)


def perform_action(ecs, actor):
    return random_move(ecs, actor)

