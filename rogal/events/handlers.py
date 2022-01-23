import logging
import string

from ..geometry import Direction

from ..data import KeyBindings

from .keys import Key
from .mouse import MouseButton


log = logging.getLogger(__name__)


"""EventHandler implementations.

Event handlers are expected to accept (entity, event) as arguments,
but most of the time we:
- need to filter out events (only specified key is pressed, only specified button
    mouse button is pressed, etc)
- need to translate this the event to some other, more meaningful value

EventHandlers can do this and call callback only if we got value from event.

Each Handler should just return simple value, no fancy logic here.

"""


class EventHandler:

    PROPAGATE_EVENTS = False

    def __init__(self, callback, propagate=None):
        self.callback = callback
        if propagate is None:
            propagate = self.PROPAGATE_EVENTS
        self.propagate = propagate

    def handle(self, event):
        raise NotImplementedError()

    def __call__(self, entity, event):
        value = self.handle(event)
        if value is not None:
            self.callback(entity, value)
            if not self.propagate:
                return False
        return event


class KeyPressHandler(EventHandler):

    def get_key_bindings(self, key_binding):
        if not isinstance(key_binding, str):
            return key_binding
        category, sep, name = key_binding.partition('.')
        bindings = KeyBindings.get(category)
        return bindings[name]


class OnKeyPress(KeyPressHandler):

    def __init__(self, key_binding, callback, value=None):
        super().__init__(callback)
        self.key_bindings = self.get_key_bindings(key_binding)
        if not self.key_bindings:
            self.key_bindings = {Key.parse(key_binding), }
        self.value = value
        if self.value is None:
            self.value = True

    def handle(self, event):
        if event.key in self.key_bindings:
            return self.value


class DirectionKeyPress(KeyPressHandler):

    """Return Direction value."""

    def handle(self, event):
        for direction in Direction:
            if event.key in KeyBindings.directions[direction.name]:
                return direction


class NextPrevKeyPress(KeyPressHandler):

    def __init__(self, next_key_binding, prev_prev_binding, callback):
        super().__init__(callback)
        self.next_key_bindings = self.get_key_bindings(next_key_binding)
        self.prev_key_bindings = self.get_key_bindings(prev_prev_binding)

    def handle(self, event):
        if event.key in self.next_key_bindings:
            return 1
        if event.key in self.prev_key_bindings:
            return -1


class YesNoKeyPress(KeyPressHandler):

    """Return True for YES, or False for NO or DISCARD."""

    def handle(self, event):
        if event.key in KeyBindings.common.YES:
            return True
        if event.key in KeyBindings.common.NO:
            return False


class ConfirmKeyPress(KeyPressHandler):

    """Return True for CONFIRM."""

    def handle(self, event):
        if event.key in KeyBindings.common.CONFIRM:
            return True


class DiscardKeyPress(KeyPressHandler):

    """Return False for DISCARD."""

    def handle(self, event):
        if event.key in KeyBindings.common.DISCARD:
            return False


class IndexKeypressHandler(KeyPressHandler):

    def __init__(self, callback, size=None):
        super().__init__(callback)
        self.size = size


class AlphabeticIndexKeyPress(IndexKeypressHandler):

    """Return 0-25 index when selecting using ascii letters."""

    def handle(self, event):
        if event.key in KeyBindings.index.ALPHABETIC:
            index = string.ascii_lowercase.index(event.key)
            if self.size and index >= self.size:
                return
            return index


class AlphabeticUpperIndexKeyPress(IndexKeypressHandler):

    """Return 0-25 index when selecting using ascii letters."""

    def handle(self, event):
        if event.key in KeyBindings.index.ALPHABETIC_UPPER:
            index = string.ascii_uppercase.index(event.key)
            if self.size and index >= self.size:
                return
            return index


class NumericIndexKeyPress(IndexKeypressHandler):

    """Return 0-9 index when selecting using digits.

    NOTE: '1' is 0 (first element in 0-indexed lists), '0' is 9

    """

    def handle(self, event):
        if event.key in KeyBindings.index.NUMERIC:
            index = string.digits(event.key)
            index -= 1
            if index < 0:
                index = 9
            if self.size and index >= self.size:
                return
            return index


class TextInput(EventHandler):

    ALLOWED_CHARACTERS = {
        *string.digits,
        *string.ascii_letters,
        *string.punctuation,
        ' ',
    }

    def handle(self, event):
        if event.text in self.ALLOWED_CHARACTERS:
            return event.text


class TextEdit(KeyPressHandler):

    def handle(self, event):
        # TODO: return values should be an enum!
        if event.key in KeyBindings.text_edit.CLEAR:
            return 'CLEAR'
        elif event.key in KeyBindings.text_edit.BACKSPACE:
            return 'BACKSPACE'
        elif event.key in KeyBindings.text_edit.DELETE:
            return 'DELETE'
        elif event.key in KeyBindings.text_edit.HOME:
            return 'HOME'
        elif event.key in KeyBindings.text_edit.END:
            return 'END'
        elif event.key in KeyBindings.text_edit.FORWARD:
            return 'FORWARD'
        elif event.key in KeyBindings.text_edit.BACKWARD:
            return 'BACKWARD'
        elif event.key in KeyBindings.text_edit.PASTE:
            return 'PASTE'


class MouseButtonEvent(EventHandler):

    BUTTONS = {}

    def __init__(self, callback, value=None):
        super().__init__(callback)
        self.value = value

    def handle(self, event):
        if event.button in self.BUTTONS:
            if self.value is None:
                return event.position
            return self.value


class MouseLeftButton(MouseButtonEvent):
    BUTTONS = {MouseButton.LEFT, }

class MouseRightButton(MouseButtonEvent):
    BUTTONS = {MouseButton.RIGHT, }

class MouseMiddleButton(MouseButtonEvent):
    BUTTONS = {MouseButton.MIDDLE, }

class MouseX1Button(MouseButtonEvent):
    BUTTONS = {MouseButton.X1, }

class MouseX2Button(MouseButtonEvent):
    BUTTONS = {MouseButton.X2, }


class MouseOver(EventHandler):

    PROPAGATE_EVENTS = True

    def handle(self, event):
        return event.position


# TODO: OBSOLETE as they always return True, just use callback instead?
class MouseIn(EventHandler):

    PROPAGATE_EVENTS = True

    def handle(self, event):
        return True


class MouseOut(EventHandler):

    PROPAGATE_EVENTS = True

    def handle(self, event):
        return True

