from ..toolkit.core import ZOrder

from ..events.components import (
    GrabInputFocus, InputFocus,
)

from .components import (
    CreateUIElement, DestroyUIElement, DestroyUIElementContent,
    ParentUIElement,
    UIWidget,
    NeedsLayout,
    UIPanel,
    UIRenderer,
)


class UIManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self._events = None

    @property
    def events(self):
        if self._events is None:
            self._events = self.ecs.resources.events_manager
        return self._events

    def create(self, widget_type, context=None):
        widget = self.ecs.create(
            CreateUIElement(
                widget_type=widget_type,
                context=context,
            ),
        )
        return widget

    def destroy(self, element):
        self.ecs.manage(DestroyUIElement).insert(element)

    def create_child(self, parent):
        element = self.ecs.create(
            ParentUIElement(parent),
        )
        return element

    def redraw(self, element):
        # TODO: redraw without destroying contents?
        self.ecs.manage(DestroyUIElementContent).insert(element)
        self.ecs.manage(NeedsLayout).insert(element)

    def insert(self, element, *,
               ui_widget=None,
               panel=None,
               z_order=None,
               renderer=None,
              ):
        if ui_widget:
            self.ecs.manage(UIWidget).insert(
                element, ui_widget,
            )
        if panel:
            self.ecs.manage(UIPanel).insert(
                element, panel, z_order or ZOrder.BASE,
            )
        if renderer:
            self.ecs.manage(UIRenderer).insert(
                element, renderer,
            )

    def bind(self, element, **handlers):
        self.events.bind(element, **handlers)

    def grab_focus(self, element):
        self.ecs.manage(GrabInputFocus).insert(element)

    # TODO: get_focus -> just set current InputFocus value, not higher one!

    def release_focus(self, element):
        self.ecs.manage(InputFocus).remove(element)

    def connect(self, element, signal_handlers):
        # TODO: insert into ECS
        return

