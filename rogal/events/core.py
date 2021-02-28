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
    TEXT_INPUT = 'text_input'

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


class TextInput(Event):
    __slots__ = ('text', )

    type = EventType.TEXT_INPUT

    def __init__(self, source, text):
        super().__init__(source)
        self.text = text

    def __repr__(self):
        return f'<{self.__class__.__name__} text={self.text}>'


class MouseMotion(Event):
    __slots__ = ('position', 'motion', 'pixel_position', 'pixel_motion', 'buttons', )

    type = EventType.MOUSE_MOTION

    def __init__(self, source, x, y, dx, dy, buttons):
        super().__init__(source)
        self.pixel_position = Position(x, y)
        self.pixel_motion = Vector(dx, dy)
        self.position = Position.ZERO
        self.motion = Vector.ZERO
        self.buttons = buttons

    def set_tile(self, x, y):
        self.position = Position(x, y)

    def set_tile_motion(self, dx, dy):
        self.motion = Vector(dx, dy)

    def __repr__(self):
        return f'<{self.__class__.__name__} position={self.position}, motion={self.motion}, buttons={self.buttons}>'


class MouseButtonEvent(Event):
    __slots__ = ('position', 'pixel_position', 'button', 'clicks', )


    def __init__(self, source, x, y, button, clicks=1):
        super().__init__(source)
        self.pixel_position = Position(x, y)
        self.position = Position.ZERO
        self.button = button
        self.clicks = clicks

    def set_tile(self, x, y):
        self.position = Position(x, y)

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

