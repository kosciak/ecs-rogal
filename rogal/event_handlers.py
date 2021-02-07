import logging
import string

from . import components
from .events import EventHandler
from .geometry import Direction


log = logging.getLogger(__name__)


class QuitHandler(EventHandler):

    def on_key_press(self, event):
        if event.key in self.key_bindings.actions.QUIT:
            return -1


class DirectionHandler(EventHandler):

    def on_key_press(self, event):
        for direction in Direction:
            if event.key in self.key_bindings.directions[direction.name]:
                return direction


class ActionsHandler(EventHandler):

    def on_key_press(self, event):
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

    def on_key_press(self, event):
        if event.key in self.key_bindings.common.YES:
            return True
        if event.key in self.key_bindings.common.NO:
            return False


class ConfirmHandler(EventHandler):

    def on_key_press(self, event):
        if event.key in self.key_bindings.common.CONFIRM:
            return True
        if event.key in self.key_bindings.common.DISCARD:
            return False


class IndexHandler(EventHandler):

    def on_key_press(self, event):
        if event.key in self.key_bindings.index.ALPHABETIC:
            return string.ascii_lowercase.index(event.key)

        if event.key in self.key_bindings.index.NUMERIC:
            index = string.digits(event.key) - 1
            if index < 0:
                index = 10
            return index

