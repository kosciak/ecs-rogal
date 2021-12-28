import collections
import logging

from ..utils import perf

from ..ecs import System
from ..ecs.run_state import RunState

from ..events import EventType
from ..events.keyboard import KeyboardState
from ..events.mouse import MouseState

from .. import components
from ..ui.components import UIPanel

from .components import (
    EventsSource,
    TextInputEvents,
    KeyPressEvents, KeyUpEvents,
    MousePressEvents, MouseClickEvents, MouseUpEvents,
    MouseInEvents, MouseOverEvents, MouseOutEvents,
    MouseWheelEvents,
    QuitEvents,
    OnTextInput,
    OnKeyPress, OnKeyUp,
    OnMousePress, OnMouseClick, OnMouseUp,
    OnMouseIn, OnMouseOver, OnMouseOut,
    OnMouseWheel,
    OnQuit,
    InputFocus, HasInputFocus, GrabInputFocus,
)


log = logging.getLogger(__name__)

'''
TODO:
- keyboard input focus and mouse input focus should be separate
- only single "thing" can have keyboard focus
- but multiple ones (if not overlapping) can have mouse focus
- mouse wheel should work only for widgets that are hovered

'''

class InputFocusSystem(System):

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
    }

    def run(self):
        # TODO: This is a mess...
        input_focus = self.ecs.manage(InputFocus)
        grab_focus = self.ecs.manage(GrabInputFocus)
        has_focus = self.ecs.manage(HasInputFocus)

        focus_per_priority = collections.defaultdict(set)
        for entity, priority in input_focus:
            focus_per_priority[priority].add(entity)

        max_priority = max(focus_per_priority.keys() or [0, ])
        next_priority = max_priority
        if has_focus:
            next_priority = max_priority + 1

        for entity in grab_focus.entities:
            if entity in has_focus:
                continue
            focus_per_priority[next_priority].add(entity)
            input_focus.insert(entity, next_priority)
        grab_focus.clear()

        has_focus.clear()
        max_priority = max(focus_per_priority.keys() or [0, ])
        for entity in focus_per_priority.get(max_priority, []):
            has_focus.insert(entity)


class ObsoleteEventsHandlersSystem(System):

    TIMEOUT = 1./60/3
    # TIMEOUT = False

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.wrapper = self.ecs.resources.wrapper
        self.timeout = self.TIMEOUT

        self.ecs.resources.keyboard_state = KeyboardState()
        self.keys = self.ecs.resources.keyboard_state

        self.mouse_over_entities = set()
        self.ecs.resources.mouse_state = MouseState()
        self.mouse = self.ecs.resources.mouse_state

        self.onscreen_manager = self.ecs.resources.onscreen_manager

    def handle_event(self, event, entity, handlers):
        value = None
        for handler, callback in handlers:
            value = handler.handle(event)
            if value is not None:
                # TODO: Is entity needed here?
                callback(entity, value)

    def get_handlers_with_focus(self, handlers_component):
        event_handlers = self.ecs.manage(handlers_component)
        if not event_handlers:
            return []
        has_focus = self.ecs.manage(components.HasInputFocus)
        valid_handlers = [
            [entity, handlers] for entity, with_focus, handlers
            in self.ecs.join(event_handlers.entities, has_focus, event_handlers)
        ]
        return valid_handlers

    def on_text_input(self, event):
        event_handlers = self.get_handlers_with_focus(components.OnTextInput)
        for entity, handlers in event_handlers:
            self.handle_event(event, entity, handlers)

    def on_key_press(self, event):
        event_handlers = self.get_handlers_with_focus(components.OnKeyPress)
        for entity, handlers in event_handlers:
            self.handle_event(event, entity, handlers)

    def get_handlers_over_position(self, handlers_component, position):
        panels = self.ecs.manage(UIPanel)
        event_handlers = self.ecs.manage(handlers_component)
        entities = self.onscreen_manager.get_entities(position)
        yield from self.ecs.join(entities, panels, event_handlers)

    def on_mouse_over_event(self, event, handlers_component):
        for entity, panel, handlers in self.get_handlers_over_position(handlers_component, event.position):
            self.mouse_over_entities.add(entity)
            # TODO: Need to pass: event.position.offset(panel.panel.position)
            #       So event_handler will get position relative to panel
            # print(event.position.offset(panel.panel.position))
            self.handle_event(event, entity, handlers)

    def on_mouse_in_event(self, event, handlers_component):
        for entity, panel, handlers in self.get_handlers_over_position(handlers_component, event.position):
            if entity in self.mouse_over_entities and \
               self.mouse.prev_position and self.mouse.prev_position in panel.panel:
                # cursor did not enter, just moved over
                continue
            self.mouse_over_entities.add(entity)
            self.handle_event(event, entity, handlers)

    def on_mouse_out_event(self, event, handlers_component):
        for entity, panel, handlers in self.get_handlers_over_position(handlers_component, event.prev_position):
            if event.position in panel.panel:
                # cursor did not leave, just moved over
                continue
            self.handle_event(event, entity, handlers)

    def on_mouse_press(self, event):
        self.on_mouse_over_event(event, components.OnMousePress)

    def on_mouse_up(self, event):
        self.on_mouse_over_event(event, components.OnMouseUp)

    def on_mouse_click(self, event):
        # Fire OnMouseClick if button was pressed and released without moving
        # TODO: Press, show button, release -> click is registered! WHAT this even mean?!?
        self.on_mouse_over_event(event, components.OnMouseClick)

    def on_mouse_motion(self, event):
        # Removing obsolete entities
        self.mouse_over_entities.intersection_update(self.ecs.entities)

        self.on_mouse_in_event(event, components.OnMouseIn)
        self.on_mouse_over_event(event, components.OnMouseOver)
        # TODO: For OnMouseOut to be 100% accurate we would need to process mouse leaving (game) window
        self.on_mouse_out_event(event, components.OnMouseOut)

    def on_mouse_wheel(self, event):
        # TODO: Wheel should work only OVER element
        #       BUT! We don't have mouse position associated with wheel event!
        event_handlers = self.get_handlers_with_focus(components.OnMouseWheel)
        for entity, handlers in event_handlers:
            self.handle_event(event, entity, handlers)

    def on_quit(self, event):
        self.ecs.create(
            components.WantsToQuit,
        )

    def run(self):
        # Get valid events and pass them to all entities with appopriate EventHandlers
        # NOTE: It is NOT checked if entity has ActsNow flag, as EventHandlers can be attached
        #       to any entity, not only to actors (for example to GUI elements)
        #       BUT there must be some ActsNow actor for system to be running!
        for event in self.wrapper.events_gen(self.timeout):
            log.debug(f'Event: {event}')
            if event.type == EventType.QUIT:
                self.on_quit(event)
            elif event.type == EventType.TEXT_INPUT:
                self.on_text_input(event)
            elif event.type == EventType.KEY_PRESS:
                self.keys.update(press_event=event)
                self.on_key_press(event)
            elif event.type == EventType.KEY_UP:
                self.keys.update(up_event=event)
            elif event.type == EventType.MOUSE_BUTTON_PRESS:
                self.mouse.update(press_event=event)
                self.on_mouse_press(event)
            elif event.type == EventType.MOUSE_BUTTON_UP:
                if event.is_click:
                    self.on_mouse_click(event)
                self.on_mouse_up(event)
                self.mouse.update(up_event=event)
            elif event.type == EventType.MOUSE_MOTION:
                self.mouse.update(motion_event=event)
                self.on_mouse_motion(event)
            elif event.type == EventType.MOUSE_WHEEL:
                self.on_mouse_wheel(event)
            break



class EventsDispatchSystem(System):

    TIMEOUT = 1./60/3
    # TIMEOUT = False

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.wrapper = self.ecs.resources.wrapper
        self.timeout = self.TIMEOUT
        self.onscreen_manager = self.ecs.resources.onscreen_manager

    def on_quit(self, event):
        self.ecs.create(
            components.WantsToQuit,
        )

    def dispatch_to_entities(self, event, entities, component):
        if not entities:
            return
        manager = self.ecs.manage(component)
        for entity in entities:
            events = manager.get(entity)
            if not events:
                events = manager.insert(entity)
            events.append(event)

    def dispatch_has_focus(self, event, component):
        # TODO: Use focus_manager
        has_focus = self.ecs.manage(HasInputFocus)
        self.dispatch_to_entities(event, has_focus.entities, component)

    def dispatch_onscreen_position(self, position, event, component):
        entities = self.onscreen_manager.get_entities(position)
        self.dispatch_to_entities(event, entities, component)

    def dispatch_mouse_button(self, event, component):
        self.dispatch_onscreen_position(event.position, event, component)

    def dispatch_mouse_motion(self, event):
        current_entities = self.onscreen_manager.get_entities(event.position) or set()
        prev_entities = self.onscreen_manager.get_entities(event.prev_position) or set()

        self.dispatch_to_entities(event, current_entities, MouseOverEvents)

        out_entities = prev_entities - current_entities
        self.dispatch_to_entities(event, out_entities, MouseOutEvents)

        in_entities = current_entities - prev_entities
        self.dispatch_to_entities(event, in_entities, MouseInEvents)

    def dispatch(self, event):
        log.debug(f'Event: {event}')
        # print(f'Event: {event}')
        if event.type == EventType.QUIT:
            self.on_quit(event)
        elif event.type == EventType.TEXT_INPUT:
            self.dispatch_has_focus(event, TextInputEvents)
        elif event.type == EventType.KEY_PRESS:
            self.dispatch_has_focus(event, KeyPressEvents)
        elif event.type == EventType.KEY_UP:
            self.dispatch_has_focus(event, KeyUpEvents)
        elif event.type == EventType.MOUSE_BUTTON_PRESS:
            self.dispatch_mouse_button(event, MousePressEvents)
        elif event.type == EventType.MOUSE_BUTTON_UP:
            if event.is_click:
                self.dispatch_mouse_button(event, MouseClickEvents)
            self.dispatch_mouse_button(event, MouseUpEvents)
        elif event.type == EventType.MOUSE_MOTION:
            self.dispatch_mouse_motion(event)
        elif event.type == EventType.MOUSE_WHEEL:
            self.dispatch_has_focus(event, MouseWheelEvents)

    def run(self):
        # Get valid events and pass them to all entities with appopriate EventHandlers
        # NOTE: It is NOT checked if entity has ActsNow flag, as EventHandlers can be attached
        #       to any entity, not only to actors (for example to GUI elements)
        #       BUT there must be some ActsNow actor for system to be running!
        events_sources = self.ecs.manage(EventsSource)
        for source, events_gen in events_sources:
            for event in events_gen(self.timeout):
                self.dispatch(event)


class EventsHandleSystem(System):

    INCLUDE_STATES = {
        RunState.WAIT_FOR_INPUT,
    }

    EVENTS_HANDLERS = [
        (TextInputEvents, OnTextInput),
        (KeyPressEvents, OnKeyPress),
        (KeyUpEvents, OnKeyUp),
        (MousePressEvents, OnMousePress),
        (MouseClickEvents, OnMouseClick),
        (MouseUpEvents, OnMouseUp),
        (MouseInEvents, OnMouseIn),
        (MouseOverEvents, OnMouseOver),
        (MouseOutEvents, OnMouseOut),
        (MouseWheelEvents, OnMouseWheel),
        (QuitEvents, OnQuit),
    ]

    def run(self):
        for events_component, handlers_component in self.EVENTS_HANDLERS:
            event_queues = self.ecs.manage(events_component)
            if not event_queues:
                continue
            event_handlers = self.ecs.manage(handlers_component)
            if not event_handlers:
                continue
            for entity, events, handlers in self.ecs.join(self.ecs.entities, event_queues, event_handlers):
                for event in events:
                    for handler, callback in handlers.items():
                        value = handler.handle(event)
                        if value is not None:
                            callback(entity, value)
            event_queues.clear()

