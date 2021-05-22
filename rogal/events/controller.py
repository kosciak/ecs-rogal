from .core import Event, EventType


class JoyAxisMotion(Event):
    __slots__ = ('axis', 'value', )

    type = EventType.JOY_AXIS_MOTION

    def __init__(self, source, axis, value):
        super().__init__(source)
        self.axis = axis
        self.value = value

    def __repr__(self):
        return f'<{self.__class__.__name__} axis={self.axis}, value={self.value}>'


class JoyHatMotion(Event):
    __slots__ = ('hat', 'value', )

    type = EventType.JOY_HAT_MOTION

    def __init__(self, source, hat, value):
        super().__init__(source)
        self.hat = hat
        self.value = value

    def __repr__(self):
        return f'<{self.__class__.__name__} hat={self.hat}, value={self.value}>'


class JoyButtonEvent(Event):
    __slots__ = ('button', )

    def __init__(self, source, button):
        super().__init__(source)
        self.button = button

    def __repr__(self):
        return f'<{self.__class__.__name__} button={self.button}>'


class JoyButtonPress(JoyButtonEvent):
    __slots__ = ()

    type = EventType.JOY_BUTTON_PRESS


class JoyButtonUp(JoyButtonEvent):
    __slots__ = ()

    type = EventType.JOY_BUTTON_UP

