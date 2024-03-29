from . import basic
from . import decorations
from . import widgets


# TODO: Consider renaming FramedLabel to Label
#       and Label to Text
#       Text - no padding, just text that can be styled with selector

class Label(
        widgets.Widget,
        basic.WithTextContent,
        decorations.WithClearedContent,
        # decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def __init__(self, txt, **kwargs):
        super().__init__(
            txt=txt,
            **kwargs,
        )
        self._inner = self._text


class FramedLabel(
        widgets.Widget,
        decorations.WithContents,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.Padded,
    ):

    def __init__(self, label, **kwargs):
        super().__init__(
            content=label,
            **kwargs,
        )

    @property
    def label(self):
        return self.contents

    @label.setter
    def label(self, label):
        self.contents = contents

