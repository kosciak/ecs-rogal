from . import core
from . import basic
from . import containers
from . import decorations
from . import renderers
from . import states
from . import signals


class Widget:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.element = None
        self.manager = None

    def layout(self, manager, element, panel, z_order):
        self.manager = manager
        self.element = element
        manager.insert(
            element,
            ui_widget=self,
        )
        return super().layout(manager, element, panel, z_order)

    def redraw(self):
        if self.manager:
            self.manager.redraw(self.element)


# TODO: rename to PaddedRow? It could be used for anything, not only Buttons
class ButtonsRow(
        Widget,
        containers.WithContainer,
        decorations.Padded,
    ):

    def __init__(self, buttons=None, *,
                 align=None, padding=None):
        self._container = containers.Row(
            content=buttons,
            align=align,
        )
        super().__init__(
            content=self._container,
            padding=padding,
        )

