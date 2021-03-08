import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class UpdateStateSystem(System):

    def run(self):
        animations = self.ecs.manage(components.Animation)
        if animations:
            self.ecs.run_state = RunState.ANIMATIONS
            return

        if self.ecs.run_state == RunState.PRE_RUN:
            self.ecs.run_state = RunState.TICKING
            return

        if self.ecs.run_state == RunState.PERFOM_ACTIONS:
            self.ecs.run_state = RunState.TICKING
            return

        acts_now = self.ecs.manage(components.ActsNow)
        if self.ecs.run_state == RunState.TICKING:
            if acts_now:
                self.ecs.run_state = RunState.WAITING_FOR_ACTIONS
            return

        on_key_press = self.ecs.manage(components.OnKeyPress)
        # TODO: Check other EventHandlers components
        # TODO: OR! set WaitingForInput to some entity
        if acts_now and on_key_press:
            self.ecs.run_state = RunState.WAITING_FOR_INPUT
        elif acts_now:
            self.ecs.run_state = RunState.WAITING_FOR_ACTIONS
        else:
            self.ecs.run_state = RunState.PERFOM_ACTIONS

