import logging

from . import components
from .ecs.run_state import RunState
from .events import handlers
from . import gui
from .rng import rng

from .utils import perf


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


ACTION_COST = 60


class TakeActionHandler:

    def __init__(self, ecs):
        # TODO: Initialize with entity? Or add set_actor(actor)
        #       Do not set_actor, this should be able to run in parallel!
        self.ecs = ecs
        self.spatial = self.ecs.resources.spatial
        self.waiting_queue = self.ecs.manage(components.WaitsForAction)

    def get_movement_cost(self, actor):
        movement_speed = self.ecs.manage(components.MovementSpeed)
        return movement_speed.get(actor) or ACTION_COST

    def get_action_cost(self, actor, action):
        if action == components.WantsToMove:
            return self.get_movement_cost(actor)
        if action == components.WantsToRest:
            return self.get_movement_cost(actor)
        if action == components.WantsToRevealLevel:
            return 0
        return ACTION_COST

    def insert_action(self, actor, action, *args, **kwargs):
        if action:
            manager = self.ecs.manage(action)
            manager.insert(actor, *args, **kwargs)

        # NOTE: Would be better to have it in system, but not sure how to pass action_cost...
        acts_now = self.ecs.manage(components.ActsNow)
        acts_now.remove(actor)

        # TODO: Move it to systems performing actions?!
        actions_queue = self.ecs.manage(components.WaitsForAction)
        action_cost = self.get_action_cost(actor, action)
        actions_queue.insert(actor, action_cost)

        return action_cost

    def take_action(self, actor, *args, **kwargs):
        """Return action_cost if action is taken."""
        return


class PlayerInput(TakeActionHandler):

    def __init__(self, ecs):
        super().__init__(ecs)

        self.on_key_press = components.OnKeyPress()
        for handler_cls, callback in [
            [handlers.DirectionKeyPress, self.try_direction],
        ]:
            self.on_key_press.bind(handler_cls(), callback)

        for key_binding, action, callback in [
            ['actions.QUIT', components.WantsToQuit, self.try_action],
            ['actions.REST', components.WantsToRest, self.try_action],
            ['actions.REVEAL_LEVEL', components.WantsToRevealLevel, self.try_action],
        ]:
            self.on_key_press.bind(
                handlers.OnKeyPress(key_binding, action),
                callback
            )

        self.on_key_press.bind(
            handlers.NextPrevKeyPress('actions.NEXT_LEVEL', 'actions.PREV_LEVEL'),
            self.try_change_level
        )

    def set_event_handlers(self, actor):
        self.ecs.manage(components.OnKeyPress).insert(actor, self.on_key_press)
        self.ecs.manage(components.GrabInputFocus).insert(actor)

    def remove_event_handlers(self, actor):
        self.ecs.manage(components.OnKeyPress).remove(actor)

    def insert_action(self, actor, action, *args, **kwargs):
        self.remove_event_handlers(actor)
        self.ecs.set_run_state(RunState.TAKE_ACTIONS)
        return super().insert_action(actor, action, *args, **kwargs)

    def take_action(self, actor):
        self.ecs.resources.current_player = actor
        self.set_event_handlers(actor)
        self.ecs.set_run_state(RunState.WAIT_FOR_INPUT)

    def try_direction(self, actor, direction):
        locations = self.ecs.manage(components.Location)

        location = locations.get(actor)
        exits = self.spatial.get_exits(location)
        if direction in exits:
            return self.insert_action(actor, components.WantsToMove, direction)

        target_position = location.position.move(direction)
        target_entities = self.spatial.get_entities(location, target_position)

        with_hit_points = self.ecs.manage(components.HitPoints)
        for target, hit_points in self.ecs.join(target_entities, with_hit_points):
            return self.insert_action(actor, components.WantsToMelee, target)

        operables = self.ecs.manage(components.OnOperate)
        for target, is_operable in self.ecs.join(target_entities, operables):
            return self.insert_action(actor, components.WantsToOperate, target)

        msg_log.warning(f'Direction: {direction.name} blocked!')

    def try_change_level(self, actor, direction):
        levels = self.ecs.manage(components.Level)
        locations = self.ecs.manage(components.Location)
        wants_to_change_level = self.ecs.manage(components.WantsToChangeLevel)

        location = locations.get(actor)
        # Fallback to current level
        level_id = location.level_id

        level_ids = []
        for level_id, levels in levels:
            level_ids.append(level_id)
        current_index = level_ids.index(location.level_id)

        if direction > 0:
            # Next level
            next_index = current_index + 1
            if next_index == len(level_ids):
                level_id = 0
            else:
                level_id = level_ids[next_index]

        elif direction < 0:
            # Previous level
            prev_index = max(0, current_index-1)
            level_id = level_ids[prev_index]

        return self.insert_action(actor, components.WantsToChangeLevel, level_id)

    def try_action(self, actor, action):
        if action is components.WantsToRevealLevel:
            manager = self.ecs.manage(action)
            return manager.insert(actor)

        if action is components.WantsToQuit:
            prompt = gui.YesNoPrompt(
            # prompt = gui.TextInputPrompt(
            # prompt = gui.AlphabeticSelectPrompt(
                self.ecs,
                context=dict(
                    title='Quit?',
                    msg='Are you sure you want to quit?',
                ),
                callback=self.insert_action,
                actor=actor,
                action=action,
            )
            return prompt.show()

        return self.insert_action(actor, action)


class AI(TakeActionHandler):

    def is_seen_by_player(self, actor):
        # Move only when seen by player
        players = self.ecs.manage(components.Player)
        viewsheds = self.ecs.manage(components.Viewshed)
        locations = self.ecs.manage(components.Location)

        actor_location = locations.get(actor)
        for player, location, viewshed in self.ecs.join(players.entities, locations, viewsheds):
            if not location.level_id == actor_location.level_id:
                continue

            if actor_location.position in viewshed.positions:
                return True

        return False

    def random_direction_move(self, actor):
        """Return random move direction from allowed exits."""
        locations = self.ecs.manage(components.Location)

        location = locations.get(actor)
        exits = self.spatial.get_exits(location)
        if exits:
            direction = rng.choice(list(exits))
            return self.insert_action(actor, components.WantsToMove, direction)
        else:
            return self.insert_action(actor, components.WantsToRest)

    def take_action(self, actor, skip_if_not_seen=True, *args, **kwargs):
        if skip_if_not_seen and not self.is_seen_by_player(actor):
            # Not in player viewshed, skip turn (but not rest!)
            return self.insert_action(actor, None)

        return self.random_direction_move(actor)


# TODO: SpectatorInput - just wait between turns for non player UI to work

