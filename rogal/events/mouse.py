import enum

from ..geometry import Position, Vector

from .core import Event, EventType


class MouseButton(enum.IntEnum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    X1 = 4
    X2 = 5


class MouseState:

    def __init__(self):
        self.position = None
        self.prev_position = None
        self.press_positions = {}
        self._clicks = set()

    @property
    def pressed_buttons(self):
        return self.press_positions.keys()

    def drag_start(self, button):
        return self.press_positions.get(button)

    def is_click(self, button):
        # TODO: Add click interval? So click only if interval between press and up is < X miliseconds
        return button in self._clicks

    def update(self, motion_event=None, press_event=None, up_event=None):
        if motion_event:
            self.prev_position = self.position
            self.position = motion_event.position
            if motion_event.motion:
                self._clicks.clear()
        if press_event:
            if self.position is None:
                self.position = press_event.position
            self.press_positions[press_event.button] = press_event.position
            self._clicks.add(press_event.button)
        if up_event:
            if self.position is None:
                self.position = up_event.position
            self.press_positions.pop(up_event.button, None)
            self._clicks.discard(up_event.button)


class MouseMotion(Event):
    __slots__ = ('position', 'motion', 'pixel_position', 'pixel_motion', 'buttons', )

    type = EventType.MOUSE_MOTION

    def __init__(self, source, x, y, dx, dy, buttons):
        super().__init__(source)
        self.position = Position(x, y)
        self.motion = Vector(dx, dy)
        self.pixel_position = Position.ZERO
        self.pixel_motion = Vector.ZERO
        self.buttons = buttons

    def set_position(self, x, y):
        self.position = Position(x, y)

    def set_motion(self, dx, dy):
        self.motion = Vector(dx, dy)

    def set_pixel_position(self, x, y):
        self.pixel_position = Position(x, y)

    def set_pixel_motion(self, dx, dy):
        self.pixel_motion = Vector(dx, dy)

    @property
    def prev_position(self):
        return self.position.moved_from(self.motion)

    @property
    def prev_pixel_position(self):
        return self.pixel_position.moved_from(self.motion)

    def __repr__(self):
        buttons = [button.name for button in sorted(self.buttons)]
        return f'<{self.__class__.__name__} position={self.position}, motion={self.motion}, buttons={buttons}>'


class MouseButtonEvent(Event):
    __slots__ = ('position', 'pixel_position', 'button', 'clicks', )

    def __init__(self, source, x, y, button, clicks=1):
        super().__init__(source)
        self.position = Position(x, y)
        self.pixel_position = Position.ZERO
        self.button = button
        self.clicks = clicks

    def set_position(self, x, y):
        self.position = Position(x, y)

    def set_pixel_position(self, x, y):
        self.pixel_position = Position(x, y)

    def __repr__(self):
        return f'<{self.__class__.__name__} position={self.position}, button={self.button.name}, clicks={self.clicks}>'


class MouseButtonPress(MouseButtonEvent):
    __slots__ = ()

    type = EventType.MOUSE_BUTTON_PRESS


class MouseButtonUp(MouseButtonEvent):
    __slots__ = ()

    type = EventType.MOUSE_BUTTON_UP


class MouseWheel(Event):
    __slots__ = ('scroll', )

    type = EventType.MOUSE_WHEEL

    def __init__(self, source, dx, dy):
        super().__init__(source)
        self.scroll = Vector(dx, dy)

    def __repr__(self):
        return f'<{self.__class__.__name__} scroll={self.scroll}>'

