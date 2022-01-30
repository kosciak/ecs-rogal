from enum import Enum, auto

from ..events import EventType
from ..events import handlers

from . import connectable


class State(Enum):
    HOVERED = auto()
    ACTIVE = auto()
    FOCUSED = auto()
    # TODO: DISABLED


class Stateful(connectable.EmitsSignals):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = set()

    @property
    def is_hovered(self):
        return State.HOVERED in self.states

    @property
    def is_active(self):
        return State.ACTIVE in self.states

    @property
    def is_focused(self):
        return State.FOCUSED in self.states

    @property
    def is_selected(self):
        return State.SELECTED in self.states

    def update_style(self):
        # Read: https://bitsofco.de/when-do-the-hover-focus-and-active-pseudo-classes-apply/
        pseudo_class = None
        if self.is_active:
            pseudo_class = 'active'
        elif self.is_hovered:
            pseudo_class = 'hover'
        elif self.is_focused:
            pseudo_class = 'focus'
        self.manager.update_style(self.element, self.selector, pseudo_class)

    def enter(self):
        self.states.add(State.HOVERED)
        self.emit('enter')
        self.update_style()

    def hover(self, position):
        if not self.is_hovered:
            self.enter()
        self.emit('hovered', position)
        self.update_style()

    def leave(self):
        self.states.discard(State.ACTIVE)
        self.states.discard(State.HOVERED)
        self.emit('leave')
        self.update_style()

    def press(self, position):
        self.states.add(State.ACTIVE)
        self.emit('pressed')
        self.update_style()

    def release(self, position):
        self.states.discard(State.ACTIVE)
        self.emit('released')
        self.update_style()

    def focus(self):
        self.states.add(State.FOCUSED)
        self.emit('focus')
        self.update_style()

    def blur(self):
        self.states.discard(State.FOCUSED)
        # self.emit('blur')
        self.update_style()


class Clickable(Stateful, connectable.HandleEvents):

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

    def activate(self):
        self.emit('activated')

    def on_press(self, element, position):
        self.press(position)

    def on_release(self, element, position):
        self.release(position)

    def on_click(self, element, position):
        self.activate()

    def on_right_click(self, element, position):
        pass

    def on_middle_click(self, element, position):
        pass

    def on_x1_click(self, element, position):
        pass

    def on_x2_click(self, element, position):
        pass


class Hoverable(Stateful, connectable.HandleEvents):

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

    def on_enter(self, element, value):
        self.enter()

    def on_over(self, element, position):
        self.hover(position)

    def on_leave(self, element, value):
        self.leave()

# TODO: Scrollable?


class Focusable(Stateful, connectable.HandleEvents):

    def focus(self):
        super().focus()
        # TODO: Call manager.focus with get_focus(self.element)

    def set_focus(self):
        if not self.is_focused:
            self.focus()
        return True


class FucusableContainer(Focusable):

    # TODO: for child in self.children: child.on('focus', self.on_child_focus)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.focused_child_element = None

    def set_focus(self):
        # TODO: Select child to focus, use focused_child_element if not None
        return super().set_focus()

    def on_child_focus(self, element, value=None):
        if self.is_focused():
            return
        self.focused_child_element = element
        self.focus()


class Activable(Focusable, connectable.HandleEvents):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind(
            EventType.KEY_PRESS,
            handlers.OnKeyPress('common.ACTIVATE', self.on_activate)
        )

    def on_activate(self, element, value=None):
        # TODO: Re-enable after sorting out focus setting and changing
        print('ACTIVATED:', self)
        # self.activate()

