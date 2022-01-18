from ..collections.attrdict import OrderedAttrDict

from . import core
from . import basic
from . import containers
from . import decorations
from . import renderers
from . import handlers
from . import states


class Widget(
        handlers.EmitsSignals,
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
        if self.manager:
            self.manager.redraw(self.element)

    def destroy(self):
        self.manager.destroy(self.element)
        self.emit('destroyed')


class FramedWidget(
        Widget,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        # decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def set_style(self, **style):
        contents_style = style.pop(self.contents.__class__.__name__, None)
        if contents_style is not None:
            self.contents.set_style(**contents_style)
        super().set_style(**style)

    @property
    def contents(self):
        return self._framed.content

    @contents.setter
    def contents(self, contents):
        self._framed.content = contents
        self.redraw()


# TODO: Consider moving to decorations or containers
# TODO: containers.Overlayed - content+containers.Overlay
class WithOverlay:

    def __init__(self, *args, **kwargs):
        self.overlay = OrderedAttrDict()
        super().__init__(*args, **kwargs)

    def layout_content(self, manager, panel, z_order):
        # Layout padded, framed, cleared contents...
        z_order = super().layout_content(manager, panel, z_order)

        # ... and all overlayed elements
        for child in self.overlay.values():
            _, z_order = child.layout(manager, panel, z_order+1)
        return z_order

    def __iter__(self):
        yield from super().__iter__()
        yield from self.overlay.values()


# TODO: rename to PaddedRow? It could be used for anything, not only Buttons
class ButtonsRow(
        Widget,
        containers.WithContainer,
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

