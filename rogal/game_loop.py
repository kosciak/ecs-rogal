import logging
import time

from . import ai
from . import components
from .run_state import RunState

from .utils import perf


log = logging.getLogger(__name__)


class GameLoop:

    ANIMATIONS_FPS = 60
    INPUT_FPS = 30

    def __init__(self, ecs, spatial, renderer, input_handler):
        self.ecs = ecs
        self.spatial = spatial
        self.renderer = renderer
        self.input_handler = input_handler
        self.run_state = RunState.PRE_RUN
        self.player = None
        self.last_render = None
        self.frame = None
        self.wait = None
        self.fps = self.INPUT_FPS
        self.performed_count = 0

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps
        self.frame = 1./self._fps
        self.wait = self.frame*3

    def run_systems(self):
        self.ecs.run(self.run_state)

    def queue_actions(self):
        # Each actor performs action
        acts_now = self.ecs.manage(components.ActsNow)
        if not acts_now:
            return
        waiting_queue = self.ecs.manage(components.WaitsForAction)
        players = self.ecs.manage(components.Player)

        performed_action = set()
        for actor in acts_now:
            action_cost = 0
            if actor in players:
                if self.performed_count:
                    # log.debug(f'Actions performed since: {self.performed_count}')
                    self.performed_count = 0
                if not self.player == actor:
                    self.render(force=True)
                self.player = actor
                action_cost = self.input_handler.handle(wait=self.wait, actor=self.player)
                if not action_cost:
                    break
            else:
                # Actor AI move
                action_cost = ai.perform_action(self.ecs, self.spatial, actor)

            if action_cost:
                waiting_queue.insert(actor, action_cost)
                performed_action.add(actor)

        self.performed_count += len(performed_action)
        acts_now.remove(*performed_action)
        if not acts_now:
            self.run_state = RunState.ACTION_PERFORMED

    def render(self, force=False):
        if not force and \
           self.last_render and time.time() - self.last_render < self.frame:
            # Do NOT render more often than once a frame
            return
        if self.renderer.render(self.player):
            self.last_render = time.time()

    def join(self):
        self.run_systems()
        while True:
            with perf.Perf('render.Renderer.render()'):
                self.render()
            acts_now = self.ecs.manage(components.ActsNow)
            pending_animations = self.ecs.manage(components.Animation)
            if pending_animations:
                self.run_state = RunState.ANIMATIONS
                self.fps = self.ANIMATIONS_FPS
                # NOTE: Sleep for half a frame, no need to run continously
                time.sleep(self.frame/2)
                # TODO: When animation stops FPS drops and particle stays too long!
            elif not acts_now:
                self.run_state = RunState.TICKING
                self.fps = self.INPUT_FPS
            else:
                # print('Acts:', len(acts_now))
                self.run_state = RunState.WAITING_FOR_INPUT
                self.fps = self.INPUT_FPS
            self.queue_actions()
            self.run_systems()

