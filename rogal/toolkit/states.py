from enum import Enum, auto

from ..events import handlers


class WidgetState(Enum):
    HOVERED = auto()
    PRESSED = auto()
    FOCUSED = auto()
    # SELECTED = auto()
    # TODO: DISABLED


class Stateful:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = set()

    @property
    def is_hovered(self):
        return WidgetState.HOVERED in self.states

    @property
    def is_pressed(self):
        return WidgetState.PRESSED in self.states

    @property
    def is_focused(self):
        return WidgetState.FOCUSED in self.states

    @property
    def is_selected(self):
        return WidgetState.SELECTED in self.states

    def enter(self):
        self.states.add(WidgetState.HOVERED)

    def leave(self):
        self.states.discard(WidgetState.HOVERED)
        self.states.discard(WidgetState.PRESSED)

    def press(self, position):
        self.states.add(WidgetState.PRESSED)

    def release(self, position):
        self.states.discard(WidgetState.PRESSED)

    def focus(self):
        self.states.add(WidgetState.FOCUSED)

    def unfocus(self):
        self.states.discard(WidgetState.FOCUSED)

    # def select(self):
    #     self.states.add(WidgetState.SELECTED)

    # def unselect(self):
    #     self.states.discard(WidgetState.SELECTED)

    # def toggle(self):
    #     if self.is_selected:
    #         self.unselect()
    #     else:
    #         self.select()


class Clickable(Stateful):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_handlers.on_mouse_click.extend([
            handlers.MouseLeftButton(self.on_click),
            handlers.MouseRightButton(self.on_right_click),
            handlers.MouseMiddleButton(self.on_middle_click),
            handlers.MouseX1Button(self.on_x1_click),
            handlers.MouseX2Button(self.on_x2_click),
        ])
        self.events_handlers.on_mouse_press.extend([
            handlers.MouseLeftButton(self.on_press),
        ])
        self.events_handlers.on_mouse_up.extend([
            handlers.MouseLeftButton(self.on_release),
        ])

    def on_press(self, element, position):
        self.emit('pressed')
        self.press(position)

    def on_release(self, element, position):
        self.emit('released')
        self.release(position)

    def on_click(self, element, position):
        self.emit('activated')
        self.activate()

    def on_right_click(self, element, position):
        pass

    def on_middle_click(self, element, position):
        pass

    def on_x1_click(self, element, position):
        pass

    def on_x2_click(self, element, position):
        pass


class Hoverable(Stateful):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_handlers.on_mouse_in.extend([
            handlers.MouseIn(self.on_enter),
        ])
        self.events_handlers.on_mouse_over.extend([
            handlers.MouseOver(self.on_over),
        ])
        self.events_handlers.on_mouse_out.extend([
            handlers.MouseOut(self.on_leave),
        ])

    # TODO: Instead of calling methods, emit signals?

    def on_enter(self, element, value):
        self.emit('enter')
        self.enter()

    def on_over(self, element, position):
        self.emit('hovered', position)
        self.hover(position)

    def on_leave(self, element, value):
        self.emit('leave')
        self.leave()

    def hover(self, position):
        if not self.is_hovered and not self.is_pressed:
            self.enter()

# TODO: Scrollable?


class WithHotkey(Stateful):

    def __init__(self, ecs, key_binding, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_handlers.on_key_press.extend([
            handlers.OnKeyPress(key_binding, self.on_hotkey),
        ])

    def on_hotkey(self, element, key, *args, **kwargs):
        self.activate()


class Activable:

    def __init__(self, callback, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.value = value

    def activate(self):
        return self.callback(self.element, self.value)

