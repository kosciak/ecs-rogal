import time

from .core import Event, EventType


class KeyboardState:

    def __init__(self, max_repeat_rate=None):
        self.max_repeat_rate = max_repeat_rate
        self._last_valid_press = {}
        self.pressed_keys = set()

    def is_valid_press(self, key):
        if not self.max_repeat_rate:
            return True
        now = time.time()
        prev_time = self._last_valid_press.get(key)
        if prev_time and now - prev_time < self.max_repeat_rate:
            return False
        self._last_valid_press[key] = now
        return True

    def update(self, press_event=None, up_event=None):
        if press_event:
            self.pressed_keys.add(press_event.key)
        if up_event:
            self.pressed_keys.discard(up_event.key)
            self._last_valid_press.pop(up_event.key, None)


class KeyboardEvent(Event):
    __slots__ = ('key', 'repeat', )

    def __init__(self, source, key, repeat=False):
        super().__init__(source)
        self.key = key
        self.repeat = repeat

    def __repr__(self):
        return f'<{self.__class__.__name__} key="{self.key}", repeat={self.repeat}>'


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
        return f'<{self.__class__.__name__} text={self.text!r}>'

