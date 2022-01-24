from ..collections.attrdict import DefaultAttrDict


class HandleEvents:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_handlers = DefaultAttrDict(list)

    def insert(self, manager, element):
        super().insert(manager, element)
        manager.bind(
            element,
            **self.events_handlers,
        )
        if self.events_handlers:
            # TODO: No need to grab focus for mouse only handlers
            manager.grab_focus(element)


class EmitsSignals:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals_handlers = DefaultAttrDict(dict)

    def insert(self, manager, element):
        super().insert(manager, element)
        manager.connect(
            element,
            self.signals_handlers,
        )

    def emit(self, signal_name, value=None):
        self.manager.emit(self.element, signal_name, value)

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

