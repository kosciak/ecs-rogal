import logging

from ..utils import perf

from ..ecs import System
from ..ecs.run_state import RunState

from ..events import EventType
# from ..events.keyboard import KeyboardState
# from ..events.mouse import MouseState

from ..components import WantsToQuit

from .components import (
    EventsSource,
    OnTextInput,
    OnKeyPress, OnKeyUp,
    OnMousePress, OnMouseClick, OnMouseUp,
    OnMouseIn, OnMouseOver, OnMouseOut,
    OnMouseWheel,
    OnQuit,
)


log = logging.getLogger(__name__)

'''
TODO:
- keyboard input focus and mouse input focus should be separate
- only single "thing" can have keyboard focus
- but multiple ones (if not overlapping) can have mouse focus
- mouse wheel should work only for widgets that are hovered(?? maybe focused?)

'''

class EventsDispatcherSystem(System):

    TIMEOUT = 1./60/3
    # TIMEOUT = False

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.wrapper = self.ecs.resources.wrapper
        self.timeout = self.TIMEOUT
        self.focus = self.ecs.resources.focus_manager

    def on_quit(self, event):
        self.ecs.create(
            WantsToQuit,
        )

    def handle_event(self, entity, event, handlers):
        propagate = True
        for callback in handlers:
            if callback(entity, event) is False:
                propagate = False
        return propagate

    def dispatch_to_entities(self, event, component, *entities):
        # NOTE: Handle events directly so we maintain correct events order
        #       and we can keep track of targets propagation order
        # Entities should be sorted - direct target, followed by parents
        # if handler returns False propagation to next entity stops
        event_handlers = self.ecs.manage(component)
        entities = [
            entity for entity in entities
            if entity in event_handlers
        ]
        if not entities:
            return
        for entity in entities:
            handlers = event_handlers.get(entity)
            propagate = self.handle_event(entity, event, handlers)
            if not propagate:
                break

    def dispatch_from_focused(self, event, component):
        self.dispatch_to_entities(
            event, component,
            *self.focus.propagate_from_focused()
        )

    def dispatch_from_position(self, position, event, component):
        self.dispatch_to_entities(
            event, component,
            *self.focus.propagate_from_position(position)
        )

    def dispatch_mouse_button(self, event, component):
        self.dispatch_from_position(event.position, event, component)

    def dispatch_mouse_motion(self, event):
        curr_entities = set(self.focus.propagate_from_position(event.position))
        prev_entities = set(self.focus.propagate_from_position(event.prev_position))

        in_entities = curr_entities - prev_entities
        self.dispatch_to_entities(
            event, OnMouseIn,
            *in_entities
        )

        self.dispatch_to_entities(
            event, OnMouseOver,
            *self.focus.propagate_from_position(event.position)
        )

        out_entities = prev_entities - curr_entities
        self.dispatch_to_entities(
            event, OnMouseOut,
            *out_entities
        )

    def dispatch(self, event):
        log.debug(f'Event: {event}')
        # print(f'Event: {event}')
        if event.type == EventType.QUIT:
            self.on_quit(event)
        elif event.type == EventType.TEXT_INPUT:
            self.dispatch_from_focused(event, OnTextInput)
        elif event.type == EventType.KEY_PRESS:
            # self.keys.update(press_event=event)
            self.dispatch_from_focused(event, OnKeyPress)
        elif event.type == EventType.KEY_UP:
            # self.keys.update(up_event=event)
            self.dispatch_from_focused(event, OnKeyUp)
        elif event.type == EventType.MOUSE_BUTTON_PRESS:
            # self.mouse.update(press_event=event)
            self.dispatch_mouse_button(event, OnMousePress)
        elif event.type == EventType.MOUSE_BUTTON_UP:
            if event.is_click:
                self.dispatch_mouse_button(event, OnMouseClick)
            self.dispatch_mouse_button(event, OnMouseUp)
            # self.mouse.update(up_event=event)
        elif event.type == EventType.MOUSE_MOTION:
            # self.mouse.update(motion_event=event)
            self.dispatch_mouse_motion(event)
        elif event.type == EventType.MOUSE_WHEEL:
            self.dispatch_from_focused(event, OnMouseWheel)

    def run(self):
        # Get events from sources and dispatch them to all valid entities
        events_sources = self.ecs.manage(EventsSource)
        for source, events_gen in events_sources:
            for event in events_gen(self.timeout):
                self.dispatch(event)

