import logging

from . import components


log = logging.getLogger(__name__)


def try_move(ecs, level, player, direction):
    movement = ecs.manage(components.WantsToMove)
    melee = ecs.manage(components.WantsToMelee)

    location = player.get(components.Location)

    exits = level.get_exits(location.position)
    if direction in exits:
        movement.insert(player, direction)
        return 60
    
    target_position = location.position.move(direction)
    target_entities = level.get_entities(target_position)

    monsters = ecs.manage(components.Monster)
    for target, monster in ecs.join(target_entities, monsters):
        melee.insert(player, target.id)
        return 60

    log.warning(f'{direction} blocked!')
    return 0

