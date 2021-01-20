import logging

from . import components


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


ACTION_COST = 60


def try_move(ecs, player, direction):
    locations = ecs.manage(components.Location)

    location = locations.get(player)
    level = ecs.levels.get(location.level_id)

    movement_directions = ecs.manage(components.WantsToMove)
    movement_speed = ecs.manage(components.MovementSpeed)
    exits = level.get_exits(location.position)
    if direction in exits:
        movement_directions.insert(player, direction)
        return movement_speed.get(player)

    target_position = location.position.move(direction)
    target_entities = level.get_entities(target_position)

    melee_targets = ecs.manage(components.WantsToMelee)
    with_hit_points = ecs.manage(components.HitPoints)
    for target, hit_points in ecs.join(target_entities, with_hit_points):
        melee_targets.insert(player, target)
        return ACTION_COST

    operate_targets = ecs.manage(components.WantsToOperate)
    operables = ecs.manage(components.OnOperate)
    for target, is_operable in ecs.join(target_entities, operables):
        operate_targets.insert(player, target)
        return ACTION_COST

    msg_log.warning(f'{direction} blocked!')
    return

