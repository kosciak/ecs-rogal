import logging
import time

from ..geometry import Position, Vector


log = logging.getLogger(__name__)


class EventType:
    UNKNONW = 'unknown'

    QUIT = 'quit'

    WINDOW = 'window' # TODO: Split by event ID

    KEY_PRESS = 'key_press'
    KEY_UP = 'key_up'

    MOUSE_MOTION = 'mouse_motion'
    MOUSE_BUTTON_PRESS = 'mouse_button_press'
    MOUSE_BUTTON_UP = 'mouse_button_up'
    MOUSE_WHEEL = 'mouse_wheel'


class Event:
    __slots__ = ('_source', )

    type = None
    repeat = False

    def __init__(self, source):
        # Original event source (for example original SDL event)
        self._source = source

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class UnknownEvent(Event):
    __slots__ = ()

    type = EventType.UNKNONW


class Quit(Event):
    __slots__ = ()

    type = EventType.QUIT


class WindowEvent(Event):
    __slots__ = ('event_id', )

    type = EventType.WINDOW

    def __init__(self, source, event_id):
        super().__init__(source)
        self.event_id = event_id

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.event_id}>'


class KeyboardEvent(Event):
    __slots__ = ('key', 'repeat', )

    def __init__(self, source, key, repeat):
        super().__init__(source)
        self.key = key
        self.repeat = repeat

    def __repr__(self):
        return f'<{self.__class__.__name__} key={self.key}, repeat={self.repeat}>'


class KeyPress(KeyboardEvent):
    __slots__ = ()

    type = EventType.KEY_PRESS


class KeyUp(KeyboardEvent):
    __slots__ = ()

    type = EventType.KEY_UP


class MouseMotion(Event):
    __slots__ = ('position', 'motion', 'buttons', )


    def __init__(self, source, x, y, dx, dy, buttons):
        super().__init__(source)
        self.position = Position(x, y)
        self.motion = Vector(dx, dy)
        self.buttons = buttons

    def __repr__(self):
        return f'<{self.__class__.__name__} position={self.position}, motion={self.motion}, buttons={self.buttons}>'


class MouseButtonEvent(Event):
    __slots__ = ('position', 'button', 'clicks', )


    def __init__(self, source, x, y, button, clicks=1):
        super().__init__(source)
        self.position = Position(x, y)
        self.button = button
        self.clicks = clicks

    def __repr__(self):
        return f'<{self.__class__.__name__} position={self.position}, button={self.button}, clicks={self.clicks}>'


class MouseButtonPress(MouseButtonEvent):
    __slots__ = ()

    type = EventType.MOUSE_BUTTON_PRESS


class MouseButtonUp(MouseButtonEvent):
    __slots__ = ()

    type = EventType.MOUSE_BUTTON_UP


class MouseWheel(Event):
    __slots__ = ('scroll', )

    def __init__(self, source, dx, dy):
        super().__init__(source)
        self.scroll = Vector(dx, dy)

    def __repr__(self):
        return f'<{self.__class__.__name__} scroll={self.scroll}>'

