import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class QuitSystem(System):

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
        RunState.TAKE_ACTIONS,
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        wants_to_quit = self.ecs.manage(components.WantsToQuit)
        if wants_to_quit:
            log.warning('Quitting...')
            raise SystemExit()

