import random

from . import components

from .utils import perf


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
    if exits:
        direction = random.choice(list(exits))
        movement_directions.insert(actor, direction)

    return get_movement_cost(ecs, actor)


def perform_action(ecs, actor, skip_if_not_seen=False):
    if skip_if_not_seen:
        # Move only when seen by player
        players = ecs.manage(components.Player)
        viewsheds = ecs.manage(components.Viewshed)
        locations = ecs.manage(components.Location)

        actor_location = locations.get(actor)
        for player in players:
            player_location = locations.get(player)
            if not player_location.level_id == actor_location.level_id:
                continue

            player_viewshed = viewsheds.get(player)
            if actor_location.position in player_viewshed.positions:
                return random_move(ecs, actor)

        # Not in player viewshed, skip turn
        return get_movement_cost(ecs, actor)

    else:
        return random_move(ecs, actor)
