import logging
import string

from ..geometry import Direction

from .mouse import MouseButton


log = logging.getLogger(__name__)


"""EventHandler implementations.

Each Handler should just return simple value, no fancy logic here.

"""


class EventHandler:

    def handle(self, event):
        raise NotImplementedError()


class KeyPressHandler(EventHandler):

    def __init__(self, ecs):
        self.ecs = ecs
        self.key_bindings = self.ecs.resources.key_bindings


class OnKeyPress(KeyPressHandler):

    def __init__(self, ecs, key_binding, value):
        super().__init__(ecs)
        self.key_binding = self.key_bindings.get(key_binding)
        self.value = value

    def handle(self, event):
        if event.key in self.key_binding:
            return self.value


class DirectionKeyPress(KeyPressHandler):

    """Return Direction value."""

    def handle(self, event):
        for direction in Direction:
            if event.key in self.key_bindings.directions[direction.name]:
                return direction


class ChangeLevelKeyPress(KeyPressHandler):

    def handle(self, event):
        if event.key in self.key_bindings.actions.NEXT_LEVEL:
            return 1
        if event.key in self.key_bindings.actions.PREV_LEVEL:
            return -1


class YesNoKeyPress(KeyPressHandler):

    """Return True for YES, or False for NO or DISCARD."""

    def handle(self, event):
        if event.key in self.key_bindings.common.YES:
            return True
        if event.key in self.key_bindings.common.NO:
            return False


class ConfirmKeyPress(KeyPressHandler):

    """Return True for CONFIRM."""

    def handle(self, event):
        if event.key in self.key_bindings.common.CONFIRM:
            return True


class DiscardKeyPress(KeyPressHandler):

    """Return False for DISCARD."""

    def handle(self, event):
        if event.key in self.key_bindings.common.DISCARD:
            return False


class IndexKeypressHandler(KeyPressHandler):

    def __init__(self, ecs, size, *args, **kwargs):
        super().__init__(ecs, *args, **kwargs)
        self.size = size


class AlphabeticIndexKeyPress(IndexKeypressHandler):

    """Return 0-25 index when selecting using ascii letters."""

    def handle(self, event):
        if event.key in self.key_bindings.index.ALPHABETIC:
            index = string.ascii_lowercase.index(event.key)
            if index < self.size:
                return index


class AlphabeticUpperIndexKeyPress(IndexKeypressHandler):

    """Return 0-25 index when selecting using ascii letters."""

    def handle(self, event):
        if event.key in self.key_bindings.index.ALPHABETIC_UPPER:
            index = string.ascii_uppercase.index(event.key)
            if index < self.size:
                return index


class NumericIndexKeyPress(IndexKeypressHandler):

    """Return 0-9 index when selecting using digits.

    NOTE: '1' is 0 (first element in 0-indexed lists), '0' is 9

    """

    def handle(self, event):
        if event.key in self.key_bindings.index.NUMERIC:
            index = string.digits(event.key)
            index -= 1
            if index < 0:
                index = 9
            if index < self.size:
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
        if event.key in self.key_bindings.text_edit.CLEAR:
            return 'CLEAR'
        elif event.key in self.key_bindings.text_edit.BACKSPACE:
            return 'BACKSPACE'
        elif event.key in self.key_bindings.text_edit.DELETE:
            return 'DELETE'
        elif event.key in self.key_bindings.text_edit.HOME:
            return 'HOME'
        elif event.key in self.key_bindings.text_edit.END:
            return 'END'
        elif event.key in self.key_bindings.text_edit.FORWARD:
            return 'FORWARD'
        elif event.key in self.key_bindings.text_edit.BACKWARD:
            return 'BACKWARD'
        elif event.key in self.key_bindings.text_edit.PASTE:
            return 'PASTE'


class MouseButtonEvent(EventHandler):

    BUTTONS = {}

    def __init__(self, value=None):
        super().__init__()
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

    def handle(self, event):
        return event.position


class MouseIn(EventHandler):

    def handle(self, event):
        return True


class MouseOut(EventHandler):

    def handle(self, event):
        return True

