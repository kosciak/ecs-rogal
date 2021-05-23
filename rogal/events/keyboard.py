import time

from .core import Event, EventType


MAX_KEY_PRESS_REPEAT_RATE = 1./8


class KeyboardState:

    def __init__(self):
        self.pressed_keys = set()

    def update(self, press_event=None, up_event=None):
        if press_event:
            self.pressed_keys.add(press_event.key)
        if up_event:
            self.pressed_keys.discard(up_event.key)


class ReapetedKeyPressLimiter:

    def __init__(self, clear_on_key_up=True, max_repeat_rate=MAX_KEY_PRESS_REPEAT_RATE):
        self.max_repeat_rate = max_repeat_rate
        self.clear_on_key_up = clear_on_key_up
        self._last_valid_press = {}

    def __call__(self, events_gen):
        now = time.time()
        is_event_repeated = False
        for event in events_gen:
            if event.type == EventType.KEY_PRESS:
                prev_time = self._last_valid_press.get(event.key.keycode)
                if prev_time and now - prev_time < self.max_repeat_rate:
                    is_event_repeated = True
                    continue
                else:
                    is_event_repeated = False
                self._last_valid_press[event.key.keycode] = now

            if event.type == EventType.KEY_UP:
                if self.clear_on_key_up:
                    self._last_valid_press.pop(event.key.keycode, None)
                    is_event_repeated = False
                if is_event_repeated:
                    continue

            if event.type == EventType.TEXT_INPUT:
                if is_event_repeated:
                    continue

            yield event


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

