from ..collections.attrdict import OrderedAttrDict

from . import core
from . import basic
from . import containers
from . import decorations
from . import renderers
from . import states
from . import signals


class Widget(
        signals.SignalsEmitter,
    ):

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

    def destroy(self):
        self.manager.destroy(self.element)
        self.emit('destroyed')


class FramedWidget(
        Widget,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
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


# TODO: Consider moving to decorations
class WithOverlay:

    def __init__(self, *args, **kwargs):
        self.overlay = OrderedAttrDict()
        super().__init__(*args, **kwargs)

    def layout_content(self, manager, parent, panel, z_order):
        # Layout padded, framed, cleared contents...
        z_order = super().layout_content(manager, parent, panel, z_order)

        # ... and all overlayed elements
        for child in self.overlay.values():
            element = manager.create_child(parent)
            z_order = child.layout(manager, element, panel, z_order+1)
        return z_order


# TODO: rename to PaddedRow? It could be used for anything, not only Buttons
class ButtonsRow(
        Widget,
        containers.WithContainer,
        decorations.Padded,
    ):

    def __init__(self, buttons=None, **style):
        self._container = containers.Row(
            content=buttons,
        )
        super().__init__(
            content=self._container,
            **style,
        )
        # NOTE: width, height, align are set to self (Padded), not to container!

#     def set_style(self, *, align=None, **style):
#         self._container.set_style(
#             align=align,
#         )
#         super().set_style(**style)

