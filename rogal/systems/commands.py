import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class QuitSystem(System):

    INCLUDE_STATES = {
        RunState.WAITING_FOR_ACTIONS,
        RunState.WAITING_FOR_INPUT,
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        wants_to_quit = self.ecs.manage(components.WantsToQuit)
        if wants_to_quit:
            log.warning('Quitting...')
            raise SystemExit()

