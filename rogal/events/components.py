from ..ecs import Component
from ..ecs.components import List


class EventsSource(Component):
    __slots__ = ('source', )

    def __init__(self, source):
        self.source = source

    def __call__(self, wait=None):
        yield from self.source.events_gen(wait)


# Text input
OnTextInput = List('OnTextInput')


# Keyboard presses
OnKeyPress = List('OnKeyPress')
OnKeyUp = List('OnKeyUp')


# Mouse buttons
OnMousePress = List('OnMousePress')
OnMouseClick = List('OnMouseClick')
OnMouseUp = List('OnMouseUp')


# Mouse motion
OnMouseIn = List('OnMouseIn')
OnMouseOver = List('OnMouseOver')
OnMouseOut = List('OnMouseOut')


# Mouse wheels
OnMouseWheel = List('OnMouseWheel')


# TODO: Controller related events

OnQuit = List('OnQuit')


# TODO: Window related events (FocusIn, FocusOut, etc)

