import logging
import time

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..events import EventType

from ..utils import perf


log = logging.getLogger(__name__)


class EventsHandlersSystem(System):

    WAIT = 1./60
    REPEAT_EVENT_TYPES = {EventType.KEY_PRESS, EventType.KEY_UP}
    REPEAT_RATE = 1./6

    INCLUDE_STATES = {
        RunState.WAITING_FOR_INPUT,
    }

    def __init__(self, ecs, repeat_rate=REPEAT_RATE):
        super().__init__(ecs)
        self.wrapper = self.ecs.resources.wrapper
        self.wait = self.WAIT
        self.repeat_rate = repeat_rate
        self._prev_times = {}

    def is_valid(self, event):
        if event.type is None:
            return False

        now = time.time()
        prev_time = self._prev_times.get(event.type)
        if event.type in self.REPEAT_EVENT_TYPES and event.repeat:
            if prev_time and now - prev_time < self.repeat_rate:
                return False

        self._prev_times[event.type] = now
        return True

    def run(self):
        acts_now = self.ecs.manage(components.ActsNow)
        if not acts_now:
            return
        events_handlers = self.ecs.manage(components.EventsHandler)
        if not events_handlers:
            return

        # Get valid events and pass them to all entities with EventsHandlers
        # NOTE: It is NOT checked if entity has ActsNow flag, as EventsHandler can be attached
        #       to any entity, not only to actors (for example to GUI elements)
        #       BUT there must be some ActsNow actor for system to be running!
        for event in self.wrapper.events(self.wait):
            log.debug(f'Event: {event}')
            if event and self.is_valid(event):
                for entity, handler in list(events_handlers):
                    handler.handle(event, entity)
            return

