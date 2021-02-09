import logging
import string

from . import components
from .events import EventHandler
from .geometry import Direction


log = logging.getLogger(__name__)


"""EventHandler implementations.

Each Handler should just return simple value, no fancy logic here.

"""


class DirectionHandler(EventHandler):

    """Return Direction value."""

    def on_key_press(self, event):
        for direction in Direction:
            if event.key in self.key_bindings.directions[direction.name]:
                return direction


class ActionsHandler(EventHandler):

    def on_key_press(self, event):
        # TODO: Maybe use some bindings: component dict instead of hardcoding?
        if event.key in self.key_bindings.actions.QUIT:
            return components.WantsToQuit()

        if event.key in self.key_bindings.actions.REST:
            return components.WantsToRest()

        if event.key in self.key_bindings.actions.REVEAL_LEVEL:
            return components.WantsToRevealLevel()


class ChangeLevelHandler(EventHandler):

    def on_key_press(self, event):
        if event.key in self.key_bindings.actions.NEXT_LEVEL:
            return 1
        if event.key in self.key_bindings.actions.PREV_LEVEL:
            return -1


class YesNoHandler(EventHandler):

    """Return True for YES, or False for NO or DISCARD."""

    def on_key_press(self, event):
        if event.key in self.key_bindings.common.YES:
            return True
        if event.key in self.key_bindings.common.NO:
            return False
        if event.key in self.key_bindings.common.DISCARD:
            return False


class ConfirmHandler(EventHandler):

    """Return True for CONFIRM, or False for DISCARD."""

    def on_key_press(self, event):
        if event.key in self.key_bindings.common.CONFIRM:
            return True
        if event.key in self.key_bindings.common.DISCARD:
            return False


class AlphabeticIndexHandler(EventHandler):

    """Return 0-25 index when selecting using ascii letters."""

    def on_key_press(self, event):
        if event.key in self.key_bindings.index.ALPHABETIC:
            return string.ascii_lowercase.index(event.key)


class NumericIndexHandler(EventHandler):

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

