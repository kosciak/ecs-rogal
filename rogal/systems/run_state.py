import logging
import time

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)

'''
TODO:
- Consider running simulation - user still should be able to interact - pause / play / quit / etc
- Only enabling / disabling input handlers should be used
- UI related systems should run ONLY when we need to render!


In Game Loop where Actors take and perform actions according to WaitsForAction queue:
PRE_RUN
TICKING - until acts_now
TAKE_ACTIONS - until no acts_now left
PERFORM_ACTIONS -> back to TICKING

'''


class RenderStateSystem(System):

    INCLUDE_STATES = {
        RunState.ANIMATIONS,
        RunState.WAIT_FOR_INPUT,
        RunState.RENDER,
    }

    FPS = 30

    def __init__(self, ecs):
        super().__init__(ecs)

        self._last_run = None
        self._fps = None
        self.frame = None
        self.fps = self.FPS
        self.next_state = None

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps
        self.frame = 1./self._fps

    def should_render(self, timestamp):
        if self._last_run and timestamp - self._last_run < self.frame:
            # Do NOT render more often than once a frame
            return False
        return True

    def run(self):
        if self.ecs.run_state == RunState.RENDER:
            return self.ecs.set_run_state(self.next_state)

        now = time.time()
        if self.should_render(now):
            self._last_run = now
            self.next_state = self.ecs.next_state or self.ecs.run_state
            return self.ecs.set_run_state(RunState.RENDER)


class AnimationsStateSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)
        self.next_state = None

    def run(self):
        animations = self.ecs.manage(components.Animation)
        if animations:
            # Stop whatever you were doing and run animations
            if not self.ecs.run_state in [RunState.ANIMATIONS, RunState.RENDER]:
                self.next_state = self.ecs.run_state
                return self.ecs.set_run_state(RunState.ANIMATIONS)
        elif self.ecs.run_state == RunState.ANIMATIONS:
            # Back to whatever was interrupted by animation
            return self.ecs.set_run_state(self.next_state)


class ActionsLoopStateSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.TICKING,
        RunState.TAKE_ACTIONS,
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        if self.ecs.run_state == RunState.PRE_RUN:
            return self.ecs.set_run_state(RunState.TICKING)

        acts_now = self.ecs.manage(components.ActsNow)
        if self.ecs.run_state == RunState.TICKING and acts_now:
            # Keep ticking until something is ready to take action
            return self.ecs.set_run_state(RunState.TAKE_ACTIONS)

        if self.ecs.run_state == RunState.TAKE_ACTIONS and not acts_now:
            # All actions taken, time to perform them
            return self.ecs.set_run_state(RunState.PERFOM_ACTIONS)

        if self.ecs.run_state == RunState.PERFOM_ACTIONS:
            # Actions performed, back to ticking
            return self.ecs.set_run_state(RunState.TICKING)

