import logging

from . import components


log = logging.getLogger(__name__)


ACTION_COST = 60


def try_move(ecs, level, player, direction):
    movement_directions = ecs.manage(components.WantsToMove)

    location = player.get(components.Location)

    exits = level.get_exits(location.position)
    if direction in exits:
        movement_directions.insert(player, direction)
        return ACTION_COST
    
    target_position = location.position.move(direction)
    target_entities = level.get_entities(target_position)

    melee_targets = ecs.manage(components.WantsToMelee)
    monsters = ecs.manage(components.Monster)
    for target, monster in ecs.join(target_entities, monsters):
        melee_targets.insert(player, target.id)
        return ACTION_COST

    operate_targets = ecs.manage(components.WantsToOperate)
    operables = ecs.manage(components.OnOperate)
    for target, is_operable in ecs.join(target_entities, operables):
        operate_targets.insert(player, target.id)
        return ACTION_COST

    log.warning(f'{direction} blocked!')
    return

