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

    def __init__(self, text, *,
                 align=None, width=None, colors=None, padding=None):
        text = self._text(text, align=align, width=width)
        super().__init__(
            content=text,
            padding=padding,
            colors=colors,
        )


class FramedLabel(
        widgets.Widget,
        basic.WithTextContent,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def __init__(self, label, frame, *,
                 align=None, width=None, colors=None, padding=None):
        self.label = self._text(label, align=align, width=width)
        super().__init__(
            content=self.label,
            frame=frame,
            # align=align,
            colors=colors,
            padding=padding,
        )

