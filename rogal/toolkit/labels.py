from . import basic
from . import decorations
from . import widgets


class Label(
        widgets.Widget,
        basic.WithTextContent,
        decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def __init__(self, txt, *,
                 align=None, width=None, height=None,
                 colors=None, padding=None):
        super().__init__(
            txt=txt,
            align=align,
            width=width,
            height=height,
            padding=padding,
            colors=colors,
        )
        self._inner = self._text


class FramedLabel(
        widgets.FramedWidget,
    ):

    def __init__(self, label, frame, *,
                 align=None, width=None, height=None,
                 colors=None, padding=None):
        super().__init__(
            content=label, frame=frame,
            align=align, width=width, height=height,
            colors=colors,
            padding=padding,
        )

