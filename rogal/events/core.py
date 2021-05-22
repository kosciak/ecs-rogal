import logging
import time


log = logging.getLogger(__name__)


class EventType:
    UNKNONW = 'unknown'

    QUIT = 'quit'

    FOCUS_IN = 'focus_in'
    FOCUS_OUT = 'focus_out'
    WINDOW_RESIZED = 'window_resized'
    WINDOW_OTHER = 'window' # TODO: Split by event ID

    KEY_PRESS = 'key_press'
    KEY_UP = 'key_up'
    TEXT_INPUT = 'text_input'

    MOUSE_MOTION = 'mouse_motion'
    MOUSE_BUTTON_PRESS = 'mouse_button_press'
    MOUSE_BUTTON_UP = 'mouse_button_up'
    MOUSE_WHEEL = 'mouse_wheel'

    JOY_AXIS_MOTION = 'joy_axis_motion'
    JOY_BALL_MOTION = 'joy_ball_motion'
    JOY_HAT_MOTION = 'joy_hat_motion'
    JOY_BUTTON_PRESS = 'joy_button_press'
    JOY_BUTTON_UP = 'joy_button_up'


class Event:
    __slots__ = ('_source', 'timestamp', )

    type = None
    repeat = False

    def __init__(self, source):
        # Original event source (for example original SDL event)
        self._source = source
        self.timestamp = time.time()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class UnknownEvent(Event):
    __slots__ = ()

    type = EventType.UNKNONW


class Quit(Event):
    __slots__ = ()

    type = EventType.QUIT

