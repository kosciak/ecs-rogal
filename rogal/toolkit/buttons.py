from . import decorations
from . import states
from . import widgets


class BaseButton(
        states.Hoverable,
        states.Clickable,
        widgets.WidgetWithClearedFramedContents,
        # decorations.WithFramedContent,
        # decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):
    pass


class Button(
        states.Activable,
        BaseButton,
    ):

    # TODO: callbacks should be replaced with signals!

    def __init__(self, content, callback, value, **kwargs):
        super().__init__(
            content=content,
            callback=callback, value=value,
            **kwargs,
        )

    def enter(self):
        super().enter()
        # TODO: self.manager.set_pseudoclass(); move it to States?
        self.manager.set_style(self.element, self.selector, 'hover')

    def leave(self):
        super().leave()
        self.manager.set_style(self.element, self.selector)

    def press(self, position):
        super().press(position)
        self.manager.set_style(self.element, self.selector, 'active')

    def release(self, position):
        super().release(position)
        self.manager.set_style(self.element, self.selector, 'hover')

    def activate(self):
        self.emit('clicked')
        super().activate()


class Label(BaseButton):

    """Simple button without callback."""

    def activate(self):
        self.emit('clicked')


class WithLabel:

    def set_label(self, label):
        label.on('clicked', self.on_label_clicked)

    def on_label_clicked(self, label, value):
        self.activate()


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
        super(widgets.WidgetWithClearedFramedContents, self).set_style(**style)

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
class CheckButton(WithLabel, ToggleButton):
    pass


class RadioButton(WithLabel, ToggleButton):

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

