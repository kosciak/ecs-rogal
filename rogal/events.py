from enum import Enum
import logging
import time


log = logging.getLogger(__name__)


class EventType(Enum):
    QUIT = 'quit'
    KEY_PRESS = 'key_press'
    # TODO: MOUSE_MOTION, MOUSE_CLICK, MOUSE_WHEEL


class Event:
    __slots__ = ()

    type = None
    repeat = False


class Quit(Event):
    __slots__ = ()

    type = EventType.QUIT


class KeyPress(Event):
    __slots__ = ('key', 'repeat', )

    type = EventType.KEY_PRESS

    def __init__(self, key, repeat):
        self.key = key
        self.repeat = repeat


class EventHandler:

    def __init__(self, ecs):
        self.ecs = ecs
        self.key_bindings = self.ecs.resources.key_bindings

    def handle(self, event):
        value = None
        fn_name = f'on_{getattr(event.type, "name", event.type)}'
        fn = getattr(self, fn_name, None)
        if fn:
            value = fn(event, *args, **kwargs)
        return value

    def on_key_press(self, event):
        return

    def on_keydown(self, event):
        # TODO: For backward compatibility
        return self.on_key_press(event)

    def on_quit(self, event):
        log.warning('Quitting...')
        raise SystemExit()


class EventsHandler:

    def __init__(self, *handler_callback):
        self.event_handlers = []
        for handler, callback in handler_callback:
            self.add(handler, callback)

    def add(self, handler, callback):
        self.event_handlers.append([handler, callback])

    def handle(self, event, entity):
        value = None
        fn_name = f'on_{getattr(event.type, "name", event.type).lower()}'
        for handler, callback in self.event_handlers:
            fn = getattr(handler, fn_name, None)
            if fn:
                value = fn(event)
            if value is not None:
                return callback(entity, value)

