from ..toolkit.core import ZOrder

from ..components import (
    OnTextInput,
    OnKeyPress,
    OnMousePress, OnMouseClick, OnMouseUp,
    OnMouseIn, OnMouseOver, OnMouseOut,
    OnMouseWheel,
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

    def bind(self, element, *,
             on_text_input=None,
             on_key_press=None,
             on_mouse_click=None, on_mouse_press=None, on_mouse_up=None,
             on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
             on_mouse_wheel=None,
            ):
        if on_text_input:
            self.ecs.manage(OnTextInput).insert(
                element, on_text_input,
            )
        if on_key_press:
            self.ecs.manage(OnKeyPress).insert(
                element, on_key_press,
            )
        if on_mouse_click:
            self.ecs.manage(OnMouseClick).insert(
                element, on_mouse_click,
            )
        if on_mouse_press:
            self.ecs.manage(OnMousePress).insert(
                element, on_mouse_press,
            )
        if on_mouse_up:
            self.ecs.manage(OnMouseUp).insert(
                element, on_mouse_up,
            )
        if on_mouse_in:
            self.ecs.manage(OnMouseIn).insert(
                element, on_mouse_in,
            )
        if on_mouse_over:
            self.ecs.manage(OnMouseOver).insert(
                element, on_mouse_over,
            )
        if on_mouse_out:
            self.ecs.manage(OnMouseOut).insert(
                element, on_mouse_out,
            )
        if on_mouse_wheel:
            self.ecs.manage(OnMouseWheel).insert(
                element, on_mouse_wheel,
            )

    def grab_focus(self, element):
        self.ecs.manage(GrabInputFocus).insert(element)

    # TODO: get_focus -> just set current InputFocus value, not higher one!

    def release_focus(self, element):
        self.ecs.manage(InputFocus).remove(element)

    def connect(self, element, signal_handlers):
        # TODO: insert into ECS
        return

