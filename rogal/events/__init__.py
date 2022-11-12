from .core import (
    EventType,
    UnknownEvent,
    Quit,
)

from .window import (
    WindowEvent,
    FocusIn,
    FocusOut,
)

from .keyboard import (
    KeyboardEvent,
    KeyPress,
    KeyUp,
    TextInput,
)

from .mouse import (
    MouseMotion,
    MouseButtonPress,
    MouseButtonUp,
    MouseWheel,
)

from .controller import (
    JoyAxisMotion,
    JoyHatMotion,
    JoyButtonEvent,
    JoyButtonPress,
    JoyButtonUp,
)

from .managers import EventsManager
from . import systems


def initialize(ecs):
    ecs.resources.register(
        events_manager=EventsManager(ecs),
    )

    ecs.register(
        systems.EventsDispatcherSystem(ecs),
    )

