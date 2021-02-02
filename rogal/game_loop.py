import logging
import time

from . import ai
from . import components
from .run_state import RunState

from .utils import perf


log = logging.getLogger(__name__)


class GameLoop:

    ANIMATIONS_FPS = 60
    INPUT_FPS = 35

    def __init__(self, ecs, renderer):
        self.ecs = ecs
        self.renderer = renderer
        self.run_state = RunState.PRE_RUN
        self.player = None
        self.last_render = None
        self.frame = None
        self.wait = None
        self.fps = self.INPUT_FPS

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

    def render(self, force=False):
        # TODO: FPS checking should go to renderer!
        if not force and \
           self.last_render and time.time() - self.last_render < self.frame:
            # Do NOT render more often than once a frame
            return
        perf_stats = perf.Perf('render.Renderer.render()')
        if self.renderer.render(self.player):
            self.last_render = time.time()
            perf_stats.elapsed()

    def join(self):
        acts_now = self.ecs.manage(components.ActsNow)
        pending_animations = self.ecs.manage(components.Animation)
        players = self.ecs.manage(components.Player)

        self.run_systems()
        while True:
            # This is ugly...
            for actor in acts_now.entities:
                if actor in players:
                    self.player = actor

            self.render()

            # Check for RunState transitions
            if pending_animations:
                self.run_state = RunState.ANIMATIONS
                # self.fps = self.ANIMATIONS_FPS
                # NOTE: Sleep for half a frame, no need to run continously
                time.sleep(self.frame/2)
                # TODO: When animation stops FPS drops and particle stays too long!
            elif not acts_now:
                if self.run_state == RunState.WAITING_FOR_ACTIONS:
                    self.run_state = RunState.PERFOM_ACTIONS
                else:
                    self.run_state = RunState.TICKING
                # self.fps = self.INPUT_FPS
            else:
                # print('Acts:', len(acts_now))
                self.run_state = RunState.WAITING_FOR_ACTIONS
                # self.fps = self.INPUT_FPS

            # self.queue_actions()
            self.run_systems()

