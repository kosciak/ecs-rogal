import collections


class SignalsEmitter:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals_handlers = collections.defaultdict(dict)

    def on(self, signal_name, handler, data=None):
        self.signals_handlers[signal_name][handler] = data
        if self.manager:
            self.manager.connect(
                self.element,
                self.signals_handlers
            )

    def off(self, signal_name, handler):
        self.signals_handlers[signal_name].pop(handler, None)
        if self.manager:
            self.manager.connect(
                self.element,
                self.signals_handlers
            )

    def emit(self, signal_name, value=None):
        self.manager.emit(self.element, signal_name, value)

    def layout(self, manager, element, panel, z_order):
        manager.connect(
            element,
            self.signals_handlers,
        )
        return super().layout(manager, element, panel, z_order)

