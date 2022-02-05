from ..collections.attrdict import OrderedAttrDict

from . import core
from . import basic
from . import containers
from . import decorations
from . import renderers
from . import connectable
from . import states


class Widget(
        connectable.SignalsEmitter,
    ):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = None

    def insert(self, manager, element):
        self.manager = manager
        super().insert(manager, element)
        manager.insert(
            element,
            content=self,
        )

    def redraw(self):
        self.manager.redraw(self.element)

    def destroy(self):
        self.manager.destroy(self.element)
        self.emit('destroyed')

    def set_focus(self):
        return False


# TODO: rename to PaddedRow? It could be used for anything, not only Buttons
class ButtonsRow(
        Widget,
        containers.WithListContainer, # TODO: Consider if needed...
        decorations.Padded,
    ):

    def __init__(self, buttons=None, **kwargs):
        self._container = containers.Row(
            content=buttons,
        )
        super().__init__(
            content=self._container,
            **kwargs,
        )
        # NOTE: width, height, align are set to self (Padded), not to container!

#     def set_style(self, *, align=None, **style):
#         self._container.set_style(
#             align=align,
#         )
#         super().set_style(**style)


class Screen(
        Widget,
        decorations.WithClearedContent,
        # decorations.WithPostProcessedContent,
        containers.Stack,
    ):

    # TODO: bind OnKeyPress('actions.QUIT')

    pass

