import logging

from . import components
from .events import handlers
from .rng import rng

from .utils import perf


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


ACTION_COST = 60


# TODO: Move to separate module! gui?
class YesNoPrompt:

    def __init__(self, ecs, entity, callback, *args, **kwargs):
        self.ecs = ecs
        self.ignore_events = self.ecs.manage(components.IgnoreEvents)
        self.entity = entity
        self.window = None
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def show(self):
        # Show prompt window and set events_handler
        msg_log.warning('Quit? Yes / No')
        self.window = self.ecs.create(
            components.CreateWindow(
                window_type='YES_NO_PROMPT',
                context=dict(
                    title='Quit?',
                    msg='Are you sure you want to quit?',
                    callback=self.on_event,
                ),
            ),
        )

        # Ignore event_handlers from entity
        self.ignore_events.insert(self.entity)

    def close(self):
        # Close prompt window
        self.ecs.manage(components.DestroyWindow).insert(self.window)

        # Restore previous event_handlers for entity
        self.ignore_events.remove(self.entity)

    def on_event(self, entity, value):
        self.close()
        if value is True:
            self.callback(self.entity, *self.args, **self.kwargs)
        if value is False:
            log.debug('Quit aborted...')


class TakeActionHandler:

    def __init__(self, ecs):
        self.ecs = ecs
        self.spatial = self.ecs.resources.spatial
        self.waiting_queue = self.ecs.manage(components.WaitsForAction)

    def get_movement_cost(self, actor):
        movement_speed = self.ecs.manage(components.MovementSpeed)
        return movement_speed.get(actor) or ACTION_COST

    def action_taken(self, actor):
        acts_now = self.ecs.manage(components.ActsNow)
        acts_now.remove(actor)

    def insert_action(self, actor, action, *args, action_cost=ACTION_COST, **kwargs):
        if action is None or action is False:
            return
        # TODO: Some generic get_action_cost(actor, action)
        manager = self.ecs.manage(action)
        manager.insert(actor, *args, **kwargs)
        if action_cost:
            self.waiting_queue.insert(actor, action_cost)
        self.action_taken(actor)

    def take_action(self, actor, *args, **kwargs):
        """Return True if action is taken."""
        return


class PlayerInput(TakeActionHandler):

    def __init__(self, ecs):
        super().__init__(ecs)
        self._deafault_events_handler = None

    def set_event_handlers(self, actor):
        on_key_press = self.ecs.manage(components.OnKeyPress).insert(actor)

        for handler_cls, callback in [
            [handlers.DirectionKeyPress, self.try_direction],
            [handlers.ChangeLevelKeyPress, self.try_change_level],
        ]:
            on_key_press.bind(handler_cls(self.ecs), callback)

        for key_binding, action, callback in [
            ['actions.QUIT', components.WantsToQuit, self.try_action],
            ['actions.REST', components.WantsToRest, self.try_action],
            ['actions.REVEAL_LEVEL', components.WantsToRevealLevel, self.try_action],
        ]:
            on_key_press.bind(handlers.OnKeyPress(self.ecs, key_binding, action), callback)

    def remove_event_handlers(self, actor):
        self.ecs.manage(components.OnKeyPress).remove(actor)

    def action_taken(self, actor):
        super().action_taken(actor)
        self.remove_event_handlers(actor)

    def take_action(self, actor):
        self.ecs.resources.current_player = actor
        self.set_event_handlers(actor)

    def try_direction(self, actor, direction):
        locations = self.ecs.manage(components.Location)

        location = locations.get(actor)
        exits = self.spatial.get_exits(location)
        if direction in exits:
            action_cost = self.get_movement_cost(actor)
            return self.insert_action(actor, components.WantsToMove, direction, action_cost=action_cost)

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

        self.insert_action(actor, components.WantsToChangeLevel, level_id)

    def try_action(self, actor, action):
        if action is components.WantsToRevealLevel:
            manager = self.ecs.manage(action)
            return manager.insert(actor)

        if action is components.WantsToQuit:
            return YesNoPrompt(self.ecs, actor, self.insert_action, action).show()

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
            action_cost = self.get_movement_cost(actor)
            self.insert_action(actor, components.WantsToMove, direction, action_cost=action_cost)

        return True

    def take_action(self, actor, skip_if_not_seen=False, *args, **kwargs):
        if skip_if_not_seen and not self.is_seen_by_player(actor):
            # Not in player viewshed, skip turn
            action_cost = self.get_movement_cost(actor)
            self.waiting_queue.insert(actor, action_cost)
            return True

        return self.random_direction_move(actor)

