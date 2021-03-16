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

    def get_valid_handlers(self, handlers_component):
        event_handlers = self.ecs.manage(handlers_component)
        if not event_handlers:
            return []
        ignore_events = self.ecs.manage(components.IgnoreEvents)
        valid_handlers = [
            [entity, handlers] for entity, handlers in event_handlers
            if not entity in ignore_events
        ]
        return valid_handlers

    def get_valid_panel_handlers(self, handlers_component):
        event_handlers = self.ecs.manage(handlers_component)
        if not event_handlers:
            return []
        panels = self.ecs.manage(components.ConsolePanel)
        ignore_events = self.ecs.manage(components.IgnoreEvents)
        valid_handlers = [
            [entity, panel, handlers] for entity, panel, handlers
            in self.ecs.join(event_handlers.entities, panels, event_handlers)
            if not entity in ignore_events
        ]
        return valid_handlers

    def handle_event(self, event, entity, handlers):
        value = None
        for handler, callback in handlers:
            value = handler.handle(event)
            if value is not None:
                # TODO: return? or just call?
                # TODO: Consider removing entity from the call
                return callback(entity, value)

    def is_valid_repeat(self, event):
        now = time.time()
        prev_time = self._prev_times.get(event.type)
        if prev_time and now - prev_time < self.repeat_rate:
            return False
        self._prev_times[event.type] = now
        return True

    def on_key_press(self, event):
        if event.repeat and not self.is_valid_repeat(event):
            return

        event_handlers = self.get_valid_handlers(components.OnKeyPress)
        for entity, handlers in event_handlers:
            self.handle_event(event, entity, handlers)

    def on_mouse_over_event(self, event, handlers_component):
        for entity, panel, handlers in self.get_valid_panel_handlers(handlers_component):
            if not event.position in panel:
                continue
            self.handle_event(event, entity, handlers)

    def on_mouse_in_event(self, event, handlers_component):
        for entity, panel, handlers in self.get_valid_panel_handlers(handlers_component):
            if event.prev_position in panel:
                # cursor did not enter, just moved over
                continue
            if not event.position in panel:
                continue
            self.handle_event(event, entity, handlers)

    def on_mouse_out_event(self, event, handlers_component):
        for entity, panel, handlers in self.get_valid_panel_handlers(handlers_component):
            if not event.prev_position in panel:
                continue
            if event.position in panel:
                # cursor did not leave, just moved over
                continue
            self.handle_event(event, entity, handlers)

    def on_mouse_press(self, event):
        self.on_mouse_over_event(event, components.OnMousePress)

    def on_mouse_click(self, event):
        self.on_mouse_over_event(event, components.OnMouseClick)

    def on_mouse_motion(self, event):
        self.on_mouse_in_event(event, components.OnMouseIn)
        self.on_mouse_over_event(event, components.OnMouseOver)
        # TODO: For MouseOut to be 100% accurate we would need to process mouse leaving game window
        self.on_mouse_out_event(event, components.OnMouseOut)

    def on_mouse_wheel(self, event):
        event_handlers = self.get_valid_handlers(components.OnMouseWheel)
        for entity, handlers in event_handlers:
            self.handle_event(event, entity, handlers)

    def on_quit(self, event):
        log.warning('Quitting...')
        raise SystemExit()

    def run(self):
        acts_now = self.ecs.manage(components.ActsNow)
        if not acts_now:
            return

        # Get valid events and pass them to all entities with appopriate EventHandlers
        # NOTE: It is NOT checked if entity has ActsNow flag, as EventHandlers can be attached
        #       to any entity, not only to actors (for example to GUI elements)
        #       BUT there must be some ActsNow actor for system to be running!
        for event in self.wrapper.events(self.wait):
            log.debug(f'Event: {event}')
            if event.type == EventType.QUIT:
                self.on_quit(event)
            if event.type == EventType.KEY_PRESS:
                self.on_key_press(event)
            if event.type == EventType.MOUSE_BUTTON_PRESS:
                self.on_mouse_press(event)
            if event.type == EventType.MOUSE_BUTTON_UP:
                self.on_mouse_click(event)
            if event.type == EventType.MOUSE_MOTION:
                self.on_mouse_motion(event)
            if event.type == EventType.MOUSE_WHEEL:
                self.on_mouse_wheel(event)
            break

