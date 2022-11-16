from . import basic
from . import decorations
from . import widgets


class WithSeparatorContent:

    def __init__(self, **kwargs):
        super().__init__(
            content=self._separator,
            **kwargs,
        )

    def set_style(self, *, separator=None, colors=None, **style):
        self._separator.set_style(
            separator=separator,
            colors=colors,
        )
        super().set_style(
            **style,
        )


class Separator(
        widgets.Widget,
        WithSeparatorContent,
        decorations.WithOverlayedContent,
        decorations.Padded,
    ):

    ELEMENT_TYPE = 'Separator'
    SEPARATOR_CLS = None

    def __init__(self, **kwargs):
        self._separator = self.SEPARATOR_CLS()
        super().__init__(**kwargs)


class HorizontalSeparator(Separator):

    SEPARATOR_CLS = basic.HorizontalSeparator


class VerticalSeparator(Separator):

    SEPARATOR_CLS = basic.VerticalSeparator

