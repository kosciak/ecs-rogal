from ..ecs import Component
from ..ecs.components import Int, Flag, List, Dict


class EventsSource(Component):
    __slots__ = ('source', )

    def __init__(self, source):
        self.source = source

    def __call__(self, wait=None):
        yield from self.source.events_gen(wait)


# Text input
TextInputEvents = List('TextInputEvents')
OnTextInput = Dict('OnTextInput')


# Keyboard presses
KeyPressEvents = List('KeyPressEvents')
OnKeyPress = Dict('OnKeyPress')

KeyUpEvents = List('KeyUpEvents')
OnKeyUp = Dict('OnKeyUp')


# Mouse buttons
MousePressEvents = List('MousePressEvents')
OnMousePress = Dict('OnMousePress')

MouseClickEvents = List('MouseClickEvents')
OnMouseClick = Dict('OnMouseClick')

MouseUpEvents = List('MouseUpEvents')
OnMouseUp = Dict('MouseUpEvents')


# Mouse motion
MouseInEvents = List('MouseInEvents')
OnMouseIn = Dict('OnMouseIn')

MouseOverEvents = List('MouseOverEvents')
OnMouseOver = Dict('OnMouseOver')

MouseOutEvents = List('MouseOutEvents')
OnMouseOut = Dict('OnMouseOut')


# Mouse wheels
MouseWheelEvents = List('MouseWheelEvents')
OnMouseWheel = Dict('OnMouseWheel')


# TODO: Controller related events


QuitEvents = List('QuitEvents')
OnQuit = Dict('OnQuit')


# TODO: Window related events (FocusIn, FocusOut, etc)


# TODO: Move to ui.focus_manager
InputFocus = Int('InputFocus')

GrabInputFocus = Flag('GrabInputFocus')

HasInputFocus = Flag('HasInputFocus')

