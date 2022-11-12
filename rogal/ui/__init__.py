from .managers import UIManager
from .managers import InputFocusManager
from .stylesheets import StylesheetsManager
from . import systems


def initialize(ecs):
    ecs.resources.register(
        ui_manager=UIManager(ecs),
        focus_manager=InputFocusManager(ecs),
        stylesheets_manager=StylesheetsManager(ecs),
    )

    ecs.register(
        systems.DestroyElementsSystem(ecs),
        systems.CreateElementsSystem(ecs),

        systems.StyleSystem(ecs),
        systems.LayoutSytem(ecs),
        systems.RenderSystem(ecs),
        systems.DisplaySystem(ecs),

        systems.InputFocusSystem(ecs), # TODO: OBSOLETE! Replace with GrabInputFocusSystem, BlurInputFocusSystem
        systems.ScreenPositionFocusSystem(ecs),

        # NOTE: Event places GrabInputFocus component, need signals to propagate
        # systems.GrabInputFocusSystem(ecs)

        # NOTE: Clear up HasFocus flags AFTER focus propagation using signals
        # systems.BlurInputFocusSystem(ecs),
    )


