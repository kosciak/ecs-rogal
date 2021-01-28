import logging

from . import components


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


ACTION_COST = 60


def try_move(ecs, spatial, player, direction):
    locations = ecs.manage(components.Location)
    movement_directions = ecs.manage(components.WantsToMove)
    movement_speed = ecs.manage(components.MovementSpeed)

    location = locations.get(player)
    exits = spatial.get_exits(location)
    if direction in exits:
        movement_directions.insert(player, direction)
        return movement_speed.get(player)

    target_position = location.position.move(direction)
    target_entities = spatial.get_entities(location, target_position)

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


def reveal_level(ecs, spatial, player):
    locations = ecs.manage(components.Location)
    level_memories = ecs.manage(components.LevelMemory)

    location = locations.get(player)
    memory = level_memories.get(player)
    memory.update(location.level_id, spatial.revealable(location.level_id))

    msg_log.warning('Level revealed!')

    return 0

