from ..collections.attrdict import DefaultAttrDict


class HandleEvents:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_handlers = DefaultAttrDict(list)

    def insert(self, manager, element):
        super().insert(manager, element)
        manager.events.bind(
            element,
            **self.events_handlers,
        )
        # TODO: No need to grab focus for mouse only handlers
        if self.events_handlers:
            manager.grab_focus(element)

    def bind(self, event_name, handler):
        self.events_handlers[f'on_{event_name}'].append(handler)
        # TODO: if self.manager: self.manager.bind??
        #       Event handlers should be registered before insertion, 
        #       and should not change...


class EmitsSignals:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals_handlers = DefaultAttrDict(dict)

    def insert(self, manager, element):
        super().insert(manager, element)
        manager.signals.bind(
            element,
            self.signals_handlers,
        )

    def on(self, signal_name, handler, data=None):
        self.signals_handlers[signal_name][handler] = data

    def emit(self, signal_name, value=None):
        self.manager.signals.emit(self.element, signal_name, value)

