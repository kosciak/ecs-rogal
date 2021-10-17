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
            return self.ecs.set_run_state(RunState.ANIMATIONS)

        # TODO: Need more convenient way of getting out of WAITING_FOR_INPUT state
        # has_input_focus = self.ecs.manage(components.HasInputFocus)
        has_input_focus = self.ecs.manage(components.OnKeyPress)
        if has_input_focus:
            return self.ecs.set_run_state(RunState.WAITING_FOR_INPUT)

        actions_queue = self.ecs.manage(components.WaitsForAction)
        # TODO: All state changes below are valid only if actions_queue is ready
        # TODO: If no actions_queue set WAITING_FOR_INPUT?

        # TODO: How to trigger PRE_RUN state (after creating player / loading a game?)
        if self.ecs.run_state == RunState.PRE_RUN:
            return self.ecs.set_run_state(RunState.TICKING)

        acts_now = self.ecs.manage(components.ActsNow)
        if self.ecs.run_state == RunState.TICKING:
            # Keep ticking until something is ready to take action
            if acts_now:
                return self.ecs.set_run_state(RunState.WAITING_FOR_ACTIONS)
            return

        if self.ecs.run_state == RunState.WAITING_FOR_ACTIONS and not acts_now:
            # All actions taken, perform them
            return self.ecs.set_run_state(RunState.PERFOM_ACTIONS)

        if self.ecs.run_state == RunState.PERFOM_ACTIONS:
            # Back to ticking
            return self.ecs.set_run_state(RunState.TICKING)

        # Back to waiting for action from any other state
        return self.ecs.set_run_state(RunState.WAITING_FOR_ACTIONS)

