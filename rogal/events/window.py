from .core import Event, EventType


class WindowEvent(Event):
    __slots__ = ('event_id', )

    type = EventType.WINDOW_OTHER

    def __init__(self, source, event_id):
        super().__init__(source)
        self.event_id = event_id

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.event_id}>'


class FocusIn(Event):
    __slots__ = ()

    type = EventType.FOCUS_IN


class FocusOut(Event):
    __slots__ = ()

    type = EventType.FOCUS_OUT

