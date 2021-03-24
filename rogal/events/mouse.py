
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
        self.drag_position = {}
        self.clicks = set()

    def is_click(self, button):
        return button in self.clicks

    def update(self, motion_event=None, press_event=None, up_event=None):
        if motion_event:
            self.prev_position = self.position
            self.position = motion_event.position
            if motion_event.motion:
                self.clicks.clear()
        if press_event:
            if self.position is None:
                self.position = press_event.position
            self.drag_position[press_event.button] = press_event.position
            self.clicks.add(press_event.button)
        if up_event:
            if self.position is None:
                self.position = up_event.position
            self.drag_position.pop(up_event.button, None)
            self.clicks.discard(up_event.button)

