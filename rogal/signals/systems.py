import logging

from ..ecs import System
from ..ecs.run_state import RunState

from .components import SignalsSource, OnSignal


log = logging.getLogger(__name__)


class SignalsHandlerSystem(System):

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
    }

    def run(self):
        signals_sources = self.ecs.manage(SignalsSource)
        on_signal = self.ecs.manage(OnSignal)
        for source, signals_gen in signals_sources:
            for entity, name, value in signals_gen():
                handlers = on_signal.get(entity)
                if not handlers:
                    continue
                if not name in handlers:
                    continue
                for callback in handlers[name]:
                    callback(entity, value)

