from enum import Enum
import logging
import time


log = logging.getLogger(__name__)


class EventType(Enum):
    QUIT = 'quit'
    KEY_PRESS = 'key_press'
    KEY_UP = 'key_up'
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


class KeyUp(KeyPress):
    __slots__ = ()

    type = EventType.KEY_UP

