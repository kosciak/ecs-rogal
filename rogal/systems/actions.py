import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


"""Systems running ecs."""


'''
TODO:
- instead of checking if entity is player just stack messages on log with source entity (and maybe target)
  then log renderer should be able to filter out what it wants (for example only player related messages)
  this way it would be possible to easily debug other entites as well, not only player

'''


class ActionsQueueSystem(System):

    INCLUDE_STATES = {
        RunState.TICKING,
    }

    def run(self):
        acts_now = self.ecs.manage(components.ActsNow)
        actions_queue = self.ecs.manage(components.WaitsForAction)

        # Clear previous ActsNow flags
        acts_now.clear()

        for entity, wait_time in actions_queue:
            # Decrease wait time
            wait_time -= 1
            if wait_time <= 0:
                # No more waiting, time for some action!
                acts_now.insert(entity)


# TODO: AIActionsSystem, for player just wait?
class TakeActionsSystem(System):

    INCLUDE_STATES = {
        RunState.TAKE_ACTIONS,
    }

    def run(self):
        acts_now = self.ecs.manage(components.ActsNow)
        if not acts_now:
            return
        actions_handlers = self.ecs.manage(components.Actor)

        for actor, handler in self.ecs.join(acts_now.entities, actions_handlers):
            # TODO: Initialize handler with actor, and set to component for later?
            if not handler.take_action(actor):
                break


class RestingSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        players = self.ecs.manage(components.Player)
        wants_to_rest = self.ecs.manage(components.WantsToRest)

        for entity in wants_to_rest.entities:
            if entity in players:
                msg_log.info('Resting...')

        wants_to_rest.clear()


class MovementSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def run(self):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        locations = self.ecs.manage(components.Location)
        movement_directions = self.ecs.manage(components.WantsToMove)
        has_moved = self.ecs.manage(components.HasMoved)

        has_moved.clear()

        for entity, location, direction in self.ecs.join(self.ecs.entities, locations, movement_directions):
            if entity in players:
                msg_log.info(f'{names.get(entity)} MOVE: {direction}')

            # Update position
            from_position = location.position
            location.position = location.position.move(direction)
            self.spatial.update_entity(entity, location, from_position)
            has_moved.insert(entity)

        # Clear processed movement intents
        movement_directions.clear()


class MeleeCombatSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spawner = self.ecs.resources.spawner

    def run(self):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        melee_targets = self.ecs.manage(components.WantsToMelee)
        locations = self.ecs.manage(components.Location)

        for entity, target in melee_targets:
            if entity in players or target in players:
                msg_log.info(f'{names.get(entity)} ATTACK: {names.get(target)}')
            # TODO: Do some damage!
            location = locations.get(target)
            self.spawner.create_and_spawn('particles.HIT_PARTICLE', location.level_id, location.position)

        # Clear processed targets
        melee_targets.clear()


class OperateSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        operate_targets = self.ecs.manage(components.WantsToOperate)
        operations = self.ecs.manage(components.OnOperate)
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)

        blocks_vision_changes.clear()
        blocks_movement_changes.clear()

        for entity, target in operate_targets:
            if entity in players:
                msg_log.info(f'{names.get(entity)} OPERATE: {names.get(target)}')
            operation = operations.get(target)
            for component in operation.insert:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                if component == components.BlocksMovement:
                    blocks_movement_changes.insert(target)
                manager = self.ecs.manage(component)
                manager.insert(target, component=component)
            for component in operation.remove:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                if component == components.BlocksMovement:
                    blocks_movement_changes.insert(target)
                manager = self.ecs.manage(component)
                manager.remove(target)

        # Clear processed targets
        operate_targets.clear()


class ActionsPerformedSystem(System):

    INCLUDE_STATES = {
        RunState.ACTIONS_PERFORMED,
    }

    def run(self):
        pass

