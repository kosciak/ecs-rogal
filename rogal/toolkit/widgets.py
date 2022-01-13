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


# TODO: FramedWidget? as base for Buttons, Windows?
class FramedWidget(
        Widget,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def __init__(self, content, frame=None, *,
                 align=None, width=None, height=None,
                 colors=None, padding=None,
                ):
        super().__init__(
            content=content,
            frame=frame,
            align=align, width=width, height=height,
            colors=colors,
            padding=padding,
        )
        self._inner = self._framed

    def set_style(self, **style):
        contents_style = style.pop(self.contents.__class__.__name__, None)
        if contents_style is not None:
            self.contents.set_style(**contents_style)
        super().set_style(**style)

    @property
    def contents(self):
        return self._inner.content

    @contents.setter
    def contents(self, contents):
        self._inner.content = contents
        self.redraw()


# TODO: Consider moving to decorations
class WithOverlay:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overlay = OrderedAttrDict()

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

