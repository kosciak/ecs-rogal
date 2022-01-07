from . import decorations
from . import signals
from . import states
from . import widgets


# TODO: Consider: multiple Labels associated with each state, change content on state change?
class BaseButton(
        widgets.Widget,
        signals.SignalsEmitter,
        states.Hoverable,
        states.Clickable,
        decorations.Padded,
    ):

    def __init__(self, content, *,
                 padding=None,
                ):
        super().__init__(
            content=content,
            padding=padding,
        )

    @property
    def button(self):
        return self.content

    @button.setter
    def button(self, button):
        self.content = button
        self.redraw()


class Button(
        states.Activable,
        BaseButton,
    ):

    # TODO: callbacks should be replaced with signals!

    def __init__(self, content, callback, value, *,
                 padding=None,
                 selected_colors=None, press_colors=None,
                 selected_renderers=None,
                ):
        super().__init__(
            content=content,
            callback=callback, value=value,
            padding=padding,
        )
        self.default_colors = self.button.colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.selected_renderers = list(selected_renderers or [])

    def enter(self):
        super().enter()
        self.button.colors = self.selected_colors
        self.button.post_renderers = self.selected_renderers
        # self.redraw();

    def leave(self):
        super().leave()
        self.button.colors = self.default_colors
        self.button.post_renderers = []
        # self.redraw()

    def press(self, position):
        super().press(position)
        self.button.colors = self.press_colors
        self.button.post_renderers = self.selected_renderers
        # self.redraw()

    def release(self, position):
        super().release(position)
        self.button.colors = self.selected_colors
        self.button.post_renderers = self.selected_renderers
        # self.redraw();

    def activate(self):
        self.emit('clicked')
        super().activate()


class Label(BaseButton):

    """Simple button without callback."""

    def __init__(self, content, *,
                 padding=None,
                ):
        super().__init__(
            content=content,
            padding=padding,
        )

    def activate(self):
        self.emit('clicked')



class WithLabel:

    def set_label(self, label):
        label.on('clicked', self.on_label_clicked)

    def on_label_clicked(self, label, value):
        self.activate()


class ToggleButton(BaseButton):

    def __init__(self, content, value=None, *,
                 padding=None,
                ):
        self._buttons = content
        self._value = value or 0
        super().__init__(
            content=self._buttons[self._value],
            padding=padding,
        )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value == self.value:
            return
        self._value = value % len(self._buttons)
        self.button = self._buttons[self._value]
        self.emit('toggled', self.value)

    def next(self):
        self.value += 1

    def prev(self):
        self.value -= 1

    def activate(self):
        self.next()


class CheckButton(WithLabel, ToggleButton):
    pass


class RadioButton(WithLabel, ToggleButton):

    def __init__(self, content, group, value=None, *,
                 padding=None,
                ):
        super().__init__(
            content=content,
            value=value,
            padding=padding,
        )
        group.add(self)

    def activate(self):
        if not self.value:
            self.value = 1


class ButtonsGroup:

    def __init__(self, buttons=None):
        self.buttons = []
        if buttons:
            for button in buttons:
                self.add(button)

    def add(self, button):
        self.buttons.append(button)
        button.on('toggled', self.on_button_toggled)

    def on_button_toggled(self, element, value):
        if not value:
            return
        for button in self.buttons:
            # Turn off other buttons
            if not button.element == element:
                button.value = 0

