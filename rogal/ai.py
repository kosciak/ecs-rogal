import random

from . import components

from .utils import perf


ACTION_COST = 60


class AI:

    def __init__(self, ecs, spatial):
        self.ecs = ecs
        self.spatial = spatial

    def get_movement_cost(self, actor):
        movement_speed = self.ecs.manage(components.MovementSpeed)
        return movement_speed.get(actor) or ACTION_COST

    def take_action(self, actor, *args, **kwargs):
        return ACTION_COST


class MonsterAI(AI):

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

    def random_move(self, actor):
        """Return random move direction from allowed exits."""
        locations = self.ecs.manage(components.Location)
        movement_directions = self.ecs.manage(components.WantsToMove)

        location = locations.get(actor)
        exits = self.spatial.get_exits(location)
        if exits:
            direction = random.choice(list(exits))
            movement_directions.insert(actor, direction)

        return self.get_movement_cost(actor)

    def take_action(self, actor, skip_if_not_seen=False, *args, **kwargs):
        if skip_if_not_seen and not self.is_seen_by_player(actor):
            # Not in player viewshed, skip turn
            return get_movement_cost(actor)

        return self.random_move(actor)

