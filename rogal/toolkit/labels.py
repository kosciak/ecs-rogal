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

    def __init__(self, txt, **style):
        super().__init__(
            txt=txt,
            **style,
        )
        self._inner = self._text


class FramedLabel(
        widgets.FramedWidget,
    ):

    def __init__(self, label, **style):
        super().__init__(
            content=label,
            **style,
        )

    @property
    def label(self):
        return self.contents

    @label.setter
    def label(self, label):
        self.contents = contents

