import logging
import time

from . import ai
from . import components
from .run_state import RunState


log = logging.getLogger(__name__)


class GameLoop:

    FPS = 60

    def __init__(self, ecs, renderer, input_handler):
        self.ecs = ecs
        self.renderer = renderer
        self.input_handler = input_handler
        self.run_state = RunState.PRE_RUN
        self.player = None
        self.last_render = None
        self.frame = 1./self.FPS

    def run_systems(self):
        self.ecs.run(self.run_state)

    def queue_actions(self):
        # Each actor performs action
        acts_now = self.ecs.manage(components.ActsNow)
        waiting = self.ecs.manage(components.WaitsForAction)
        players = self.ecs.manage(components.Player)
        locations = self.ecs.manage(components.Location)

        performed_action = set()
        for actor, location in self.ecs.join(acts_now.entities, locations):
            action_cost = 0
            if actor in players:
                self.run_state = RunState.WAITING_FOR_INPUT
                self.player = actor
                action_cost = self.input_handler(actor, wait=True)
            else:
                # Actor AI move
                action_cost = ai.perform_action(self.ecs, actor)

            if action_cost:
                waiting.insert(actor, action_cost)
                performed_action.add(actor)
                self.run_state = RunState.ACTION_PERFORMED
                # TODO: Perform all actions at once for all actors (including Player)?
                break
        acts_now.remove(*performed_action)

    def render(self):
        if self.last_render and time.time() - self.last_render < self.frame:
            return
        if self.renderer(self.player):
            self.last_render = time.time()

    def join(self):
        self.run_systems()
        while True:
            self.render()
            acts_now = self.ecs.manage(components.ActsNow)
            pending_animations = self.ecs.manage(components.Animation)
            if pending_animations:
                self.run_state = RunState.ANIMATIONS
                # NOTE: Sleep for half a frame, no need to run continously
                time.sleep(self.frame/2)
            elif not acts_now:
                self.run_state = RunState.TICKING
            self.queue_actions()
            self.run_systems()

