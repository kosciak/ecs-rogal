from .. import components

from .core import ZOrder
from .builder import WidgetsBuilder


class UIManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self.widgets_builder = WidgetsBuilder(self.ecs)

    def create(self, widget_type, context):
        widget = self.ecs.create(
            components.CreateUIWidget(
                widget_type=widget_type,
                context=context,
            ),
        )
        return widget

    def destroy(self, widget):
        self.ecs.manage(components.DestroyUIWidget).insert(widget)

    def create_child(self, parent):
        widget = self.ecs.create(
            components.ParentUIWidget(parent),
        )
        return widget

    def redraw(self, widget):
        self.ecs.manage(components.DestroyUIWidgetChildren).insert(widget)
        content = self.ecs.manage(components.UIWidget).get(widget)
        if content:
            content.invalidate()

    def insert(self, widget, *,
               ui_widget=None,
               panel=None,
               z_order=None,
               renderer=None,
              ):
        if ui_widget:
            self.ecs.manage(components.UIWidget).insert(
                widget, ui_widget, needs_update=False,
            )
        if panel:
            self.ecs.manage(components.Console).insert(
                widget, panel, z_order or ZOrder.BASE,
            )
        if renderer:
            self.ecs.manage(components.PanelRenderer).insert(
                widget, renderer,
            )

    def bind(self, widget, *,
             on_text_input=None,
             on_key_press=None,
             on_mouse_click=None, on_mouse_press=None, on_mouse_up=None,
             on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
             on_mouse_wheel=None,
            ):
        if on_text_input:
            self.ecs.manage(components.OnTextInput).insert(
                widget, on_text_input,
            )
        if on_key_press:
            self.ecs.manage(components.OnKeyPress).insert(
                widget, on_key_press,
            )
        if on_mouse_click:
            self.ecs.manage(components.OnMouseClick).insert(
                widget, on_mouse_click,
            )
        if on_mouse_press:
            self.ecs.manage(components.OnMousePress).insert(
                widget, on_mouse_press,
            )
        if on_mouse_up:
            self.ecs.manage(components.OnMouseUp).insert(
                widget, on_mouse_up,
            )
        if on_mouse_in:
            self.ecs.manage(components.OnMouseIn).insert(
                widget, on_mouse_in,
            )
        if on_mouse_over:
            self.ecs.manage(components.OnMouseOver).insert(
                widget, on_mouse_over,
            )
        if on_mouse_out:
            self.ecs.manage(components.OnMouseOut).insert(
                widget, on_mouse_out,
            )
        if on_mouse_wheel:
            self.ecs.manage(components.OnMouseWheel).insert(
                widget, on_mouse_wheel,
            )

    def grab_focus(self, widget):
        self.ecs.manage(components.GrabInputFocus).insert(widget)

    # TODO: get_focus -> just set current InputFocus value, not higher one!

    def release_focus(self, widget):
        self.ecs.manage(components.InputFocus).remove(widget)

    def create_widget(self, widget_type, context):
        widget = self.widgets_builder.create(
            widget_type, context,
        )
        return widget

