import logging
import string

from ..geometry import Direction


log = logging.getLogger(__name__)


"""EventHandler implementations.

Each Handler should just return simple value, no fancy logic here.

"""


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

    def on_key_up(self, event):
        return

    def on_keyup(self, event):
        # TODO: For backward compatibility
        return self.on_key_up(event)

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


class OnKeyPress(EventHandler):

    def __init__(self, ecs, key_binding, value):
        super().__init__(ecs)
        self.key_binding = self.key_bindings.get(key_binding)
        self.value = value

    def on_key_press(self, event):
        if event.key in self.key_binding:
            return self.value


class DirectionKeyPress(EventHandler):

    """Return Direction value."""

    def on_key_press(self, event):
        for direction in Direction:
            if event.key in self.key_bindings.directions[direction.name]:
                return direction


class ChangeLevelKeyPress(EventHandler):

    def on_key_press(self, event):
        if event.key in self.key_bindings.actions.NEXT_LEVEL:
            return 1
        if event.key in self.key_bindings.actions.PREV_LEVEL:
            return -1


class YesNoKeyPress(EventHandler):

    """Return True for YES, or False for NO or DISCARD."""

    def on_key_press(self, event):
        if event.key in self.key_bindings.common.YES:
            return True
        if event.key in self.key_bindings.common.NO:
            return False
        if event.key in self.key_bindings.common.DISCARD:
            return False


class ConfirmKeyPress(EventHandler):

    """Return True for CONFIRM, or False for DISCARD."""

    def on_key_press(self, event):
        if event.key in self.key_bindings.common.CONFIRM:
            return True
        if event.key in self.key_bindings.common.DISCARD:
            return False


class AlphabeticIndexKeyPress(EventHandler):

    """Return 0-25 index when selecting using ascii letters."""

    def on_key_press(self, event):
        if event.key in self.key_bindings.index.ALPHABETIC:
            return string.ascii_lowercase.index(event.key)


class AlphabeticUpperIndexKeyPress(EventHandler):

    """Return 0-25 index when selecting using ascii letters."""

    def on_key_press(self, event):
        if event.key in self.key_bindings.index.ALPHABETIC_UPPER:
            return string.ascii_uppercase.index(event.key)


class NumericIndexKeyPress(EventHandler):

    """Return 0-9 index when selecting using digits.

    NOTE: '1' is 0 (first element in 0-indexed lists), '0' is 9

    """

    def on_key_press(self, event):
        if event.key in self.key_bindings.index.NUMERIC:
            index = string.digits(event.key)
            index -= 1
            if index < 0:
                index = 9
            return index

