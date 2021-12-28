from ..ecs import Component
from ..ecs.components import Int, Flag, List


class EventsSource(Component):
    __slots__ = ('source', )

    def __init__(self, source):
        self.source = source

    def __call__(self, wait=None):
        yield from self.source.events_gen(wait)


# Text input
TextInputEvents = List('TextInputEvents')
OnTextInput = List('OnTextInput')


# Keyboard presses
KeyPressEvents = List('KeyPressEvents')
OnKeyPress = List('OnKeyPress')

KeyUpEvents = List('KeyUpEvents')
OnKeyUp = List('OnKeyUp')


# Mouse buttons
MousePressEvents = List('MousePressEvents')
OnMousePress = List('OnMousePress')

MouseClickEvents = List('MouseClickEvents')
OnMouseClick = List('OnMouseClick')

MouseUpEvents = List('MouseUpEvents')
OnMouseUp = List('MouseUpEvents')


# Mouse motion
MouseInEvents = List('MouseInEvents')
OnMouseIn = List('OnMouseIn')

MouseOverEvents = List('MouseOverEvents')
OnMouseOver = List('OnMouseOver')

MouseOutEvents = List('MouseOutEvents')
OnMouseOut = List('OnMouseOut')


# Mouse wheels
MouseWheelEvents = List('MouseWheelEvents')
OnMouseWheel = List('OnMouseWheel')


# TODO: Controller related events


QuitEvents = List('QuitEvents')
OnQuit = List('OnQuit')


# TODO: Window related events (FocusIn, FocusOut, etc)


# TODO: Move to ui.focus_manager
InputFocus = Int('InputFocus')

GrabInputFocus = Flag('GrabInputFocus')

HasInputFocus = Flag('HasInputFocus')

