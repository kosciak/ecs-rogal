
class MouseButton:
    LEFT = 'LMB'
    MIDDLE = 'MMB'
    RIGHT = 'RMB'
    X1 = 'X1MB'
    X2 = 'X2MB'


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

