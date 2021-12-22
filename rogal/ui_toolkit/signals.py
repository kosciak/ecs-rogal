import collections


Signal = collections.namedtuple(
    'Signal', [
        'source',
        'name',
        'value',
    ])


class SignalsEmitter:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals_handlers = collections.defaultdict(set)

    def on(self, signal_name, handler):
        self.signals_handlers[signal_name].add(handler)

    def off(self, signal_name, handler):
        self.signals_handlers[signal_name].discard(handler)

    def emit(self, signal_name, value=None):
        signal = Signal(
            self.element,
            signal_name,
            value,
        )
        print(signal)
        # TODO: queue in some kind of signals source
        return

    def layout(self, manager, element, panel, z_order):
        manager.connect(
            element,
            self.signals_handlers,
        )
        return super().layout(manager, element, panel, z_order)

