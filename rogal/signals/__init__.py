from .managers import SignalsManager
from . import systems


def initialize(ecs):
    ecs.resources.register(
        signals_manager=SignalsManager(ecs),
    )

    ecs.register(
        systems.SignalsHandlerSystem(ecs),
    )

