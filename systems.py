import components


"""Systems running ecs."""

# NOTE: For now just use <type>_system_run(ecs, level), make some classes later


def movement_system_run(ecs, level):
    locations = ecs.manage(components.Location)
    movement_intents = ecs.manage(components.WantsToMove)
    for location, direction in ecs.join(locations, movement_intents):
        location.position = location.position.move(direction)
        # TODO: Add some HasMoved to flag to entity?
    movement_intents.clear()

