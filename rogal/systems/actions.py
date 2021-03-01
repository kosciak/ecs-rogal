import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


"""Systems running ecs."""


class ActionsQueueSystem(System):

    INCLUDE_STATES = {
        RunState.TICKING,
    }

    def update_acts_now(self):
        acts_now = self.ecs.manage(components.ActsNow)
        waiting_queue = self.ecs.manage(components.WaitsForAction)

        # Clear previous ActsNow flags
        acts_now.clear()

        for entity, waits in waiting_queue:
            # Decrease wait time
            waits -= 1
            if waits <= 0:
                # No more waiting, time for some action!
                acts_now.insert(entity)

    def run(self):
        self.update_acts_now()


class TakeActionsSystem(System):

    INCLUDE_STATES = {
        RunState.WAITING_FOR_ACTIONS,
    }

    def run(self):
        acts_now = self.ecs.manage(components.ActsNow)
        if not acts_now:
            return
        actions_handlers = self.ecs.manage(components.Actor)

        for actor, handler in self.ecs.join(acts_now.entities, actions_handlers):
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

    def apply_move(self):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        locations = self.ecs.manage(components.Location)
        movement_directions = self.ecs.manage(components.WantsToMove)
        has_moved = self.ecs.manage(components.HasMoved)

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

    def run(self):
        self.apply_move()


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
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        has_moved = self.ecs.manage(components.HasMoved)
        has_moved.clear()

        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_vision_changes.clear()

        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        blocks_movement_changes.clear()

