from ..ecs import Component
from ..ecs.components import Dict


class SignalsSource(Component):
    __slots__ = ('source', )

    def __init__(self, source):
        self.source = source

    def __call__(self):
        yield from self.source.signals_gen()


OnSignal = Dict('OnSignal')

