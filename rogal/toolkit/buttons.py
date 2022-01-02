from . import decorations
from . import signals
from . import states
from . import widgets


# TODO: Consider: multiple Labels associated with each state, change content on state change?
class Button(
        widgets.Widget,
        signals.SignalsEmitter,
        states.Activable,
        states.Hoverable,
        states.Clickable,
        decorations.Padded,
    ):

    def __init__(self, value, callback, content, *,
                 padding=None,
                 selected_colors=None, press_colors=None,
                 selected_renderers=None,
                ):
        self._button = content
        super().__init__(
            callback=callback, value=value,
            content=self._button,
            padding=padding,
        )
        self.default_colors = self._button.colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.selected_renderers = list(selected_renderers or [])

    def enter(self):
        super().enter()
        self._button.colors = self.selected_colors
        self._button.post_renderers = self.selected_renderers
        # self.redraw();

    def leave(self):
        super().leave()
        self._button.colors = self.default_colors
        self._button.post_renderers = []
        # self.redraw()

    def press(self, position):
        super().press(position)
        self._button.colors = self.press_colors
        self._button.post_renderers = self.selected_renderers
        # self.redraw()

    def release(self, position):
        super().release(position)
        self._button.colors = self.selected_colors
        self._button.post_renderers = self.selected_renderers
        # self.redraw();

    def activate(self):
        self.emit('clicked')
        super().activate()

