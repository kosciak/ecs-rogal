from . import decorations
from . import states
from . import widgets


class BaseButton(
        states.Hoverable,
        states.Clickable,
        widgets.Widget,
        decorations.WithContents,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def activate(self):
        super().activate()
        self.emit('clicked')


class Button(
        states.Activable,
        BaseButton,
    ):

    pass


class Label(BaseButton):

    """Simple label button."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assigned_activables = []

    def assign(self, activable):
        self.assigned_activables.append(activable)

    def activate(self):
        super().activate()
        for activable in self.assigned_activables:
            activable.activate()


class ToggleButton(BaseButton):

    def __init__(self, content, value=None, **kwargs):
        self._buttons = content
        self._value = value or 0
        super().__init__(
            content=self._buttons[self._value],
            **kwargs,
        )

    def set_style(self, **style):
        contents_style = style.pop(self.contents.__class__.__name__, None)
        if contents_style is not None:
            for button in self._buttons:
                button.set_style(**contents_style)
        super(decorations.WithContents, self).set_style(**style)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value == self.value:
            return
        self._value = value % len(self._buttons)
        self.contents = self._buttons[self._value]
        self.emit('toggled', self.value)

    def next(self):
        self.value += 1

    def prev(self):
        self.value -= 1

    def activate(self):
        self.next()

    def __iter__(self):
        yield from super().__iter__()
        yield from (button for button in self._buttons if not button.element)


# TODO: Rename to IndicatorButton?
#       And CheckButton / RadioButton would be Indicator+Label inside single Widget?
class CheckButton(ToggleButton):
    pass


class RadioButton(ToggleButton):

    def __init__(self, content, group, value=None, **kwargs):
        super().__init__(
            value=value,
            content=content,
            **kwargs,
        )
        group.add(self)

    def activate(self):
        if not self.value:
            self.value = 1


# TODO: Rename to ToggleGroup?
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

