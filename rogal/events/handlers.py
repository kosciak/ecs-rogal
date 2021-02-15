import logging
import string

from ..geometry import Direction

from .core import EventHandler


log = logging.getLogger(__name__)


"""EventHandler implementations.

Each Handler should just return simple value, no fancy logic here.

"""


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

