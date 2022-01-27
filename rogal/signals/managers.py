from .core import Signal, SignalsQueue
from .components import SignalsSource, OnSignal


class SignalsManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self.queue = SignalsQueue()
        self.add_source(self.queue)

    def add_source(self, signals_source):
        return self.ecs.create(
            SignalsSource(signals_source),
        )

    def emit(self, entity, name, value=None):
        signal = Signal(
            entity,
            name,
            value,
        )
        self.queue.put(signal)

    def bind(self, entity, handlers):
        if handlers:
            self.ecs.manage(OnSignal).insert(entity, handlers)

    def on(self, entity, signal_name, handler, data=None):
        handlers = self.ecs.manage(OnSignal).get(entity)
        if not handlers:
            handlers = self.ecs.manage(OnSignal).insert(entity, {})
        signal_handlers = handlers.setdefault(signal_name, {})
        signal_handlers[handler] = data

    # TODO: def off(self, entity, signal_name, handler):

