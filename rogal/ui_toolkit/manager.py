from .. import components

from .core import ZOrder
from .builder import WidgetsBuilder


class UIManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self.widgets_builder = WidgetsBuilder(self.ecs)

    def create(self, widget_type, context):
        widget = self.ecs.create(
            components.CreateUIElement(
                widget_type=widget_type,
                context=context,
            ),
        )
        return widget

    def destroy(self, element):
        self.ecs.manage(components.DestroyUIElement).insert(element)

    def create_child(self, parent):
        element = self.ecs.create(
            components.ParentUIElement(parent),
        )
        return element

    def redraw(self, element):
        self.ecs.manage(components.DestroyUIElementContent).insert(element)
        content = self.ecs.manage(components.UIWidget).get(element)
        if content:
            content.invalidate()

    def insert(self, element, *,
               ui_widget=None,
               panel=None,
               z_order=None,
               renderer=None,
              ):
        if ui_widget:
            self.ecs.manage(components.UIWidget).insert(
                element, ui_widget, needs_update=False,
            )
        if panel:
            self.ecs.manage(components.Console).insert(
                element, panel, z_order or ZOrder.BASE,
            )
        if renderer:
            self.ecs.manage(components.PanelRenderer).insert(
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
            self.ecs.manage(components.OnTextInput).insert(
                element, on_text_input,
            )
        if on_key_press:
            self.ecs.manage(components.OnKeyPress).insert(
                element, on_key_press,
            )
        if on_mouse_click:
            self.ecs.manage(components.OnMouseClick).insert(
                element, on_mouse_click,
            )
        if on_mouse_press:
            self.ecs.manage(components.OnMousePress).insert(
                element, on_mouse_press,
            )
        if on_mouse_up:
            self.ecs.manage(components.OnMouseUp).insert(
                element, on_mouse_up,
            )
        if on_mouse_in:
            self.ecs.manage(components.OnMouseIn).insert(
                element, on_mouse_in,
            )
        if on_mouse_over:
            self.ecs.manage(components.OnMouseOver).insert(
                element, on_mouse_over,
            )
        if on_mouse_out:
            self.ecs.manage(components.OnMouseOut).insert(
                element, on_mouse_out,
            )
        if on_mouse_wheel:
            self.ecs.manage(components.OnMouseWheel).insert(
                element, on_mouse_wheel,
            )

    def grab_focus(self, element):
        self.ecs.manage(components.GrabInputFocus).insert(element)

    # TODO: get_focus -> just set current InputFocus value, not higher one!

    def release_focus(self, element):
        self.ecs.manage(components.InputFocus).remove(element)

    def connect(self, element, signal_handlers):
        # TODO: insert into ECS
        return

    def create_widget(self, widget_type, context):
        widget = self.widgets_builder.build(
            widget_type, context,
        )
        return widget

