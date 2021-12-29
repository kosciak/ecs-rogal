
from .components import (
    EventsSource,
    OnTextInput,
    OnKeyPress, OnKeyUp,
    OnMousePress, OnMouseClick, OnMouseUp,
    OnMouseIn, OnMouseOver, OnMouseOut,
    OnMouseWheel,
)


class EventsManager:

    def __init__(self, ecs):
        self.ecs = ecs

    def add_source(self, events_source):
        return self.ecs.create(
            EventsSource(events_source),
        )

    def bind(self, entity, *,
             on_text_input=None,
             on_key_press=None, on_key_up=None,
             on_mouse_click=None, on_mouse_press=None, on_mouse_up=None,
             on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
             on_mouse_wheel=None,
            ):
        if on_text_input:
            self.ecs.manage(OnTextInput).insert(
                entity, on_text_input,
            )
        if on_key_press:
            self.ecs.manage(OnKeyPress).insert(
                entity, on_key_press,
            )
        if on_key_up:
            self.ecs.manage(OnKeyUp).insert(
                entity, on_key_up,
            )
        if on_mouse_click:
            self.ecs.manage(OnMouseClick).insert(
                entity, on_mouse_click,
            )
        if on_mouse_press:
            self.ecs.manage(OnMousePress).insert(
                entity, on_mouse_press,
            )
        if on_mouse_up:
            self.ecs.manage(OnMouseUp).insert(
                entity, on_mouse_up,
            )
        if on_mouse_in:
            self.ecs.manage(OnMouseIn).insert(
                entity, on_mouse_in,
            )
        if on_mouse_over:
            self.ecs.manage(OnMouseOver).insert(
                entity, on_mouse_over,
            )
        if on_mouse_out:
            self.ecs.manage(OnMouseOut).insert(
                entity, on_mouse_out,
            )
        if on_mouse_wheel:
            self.ecs.manage(OnMouseWheel).insert(
                entity, on_mouse_wheel,
            )

    def unbind(self, entity, *,
               on_text_input=None,
               on_key_press=None, on_key_up=None,
               on_mouse_click=None, on_mouse_press=None, on_mouse_up=None,
               on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
               on_mouse_wheel=None,
              ):
        if on_text_input:
            self.ecs.manage(OnTextInput).remove(entity)
        if on_key_press:
            self.ecs.manage(OnKeyPress).remove(entity)
        if on_key_up:
            self.ecs.manage(OnKeyUp).remove(entity)
        if on_mouse_click:
            self.ecs.manage(OnMouseClick).remove(entity)
        if on_mouse_press:
            self.ecs.manage(OnMousePress).remove(entity)
        if on_mouse_up:
            self.ecs.manage(OnMouseUp).remove(entity)
        if on_mouse_in:
            self.ecs.manage(OnMouseIn).remove(entity)
        if on_mouse_over:
            self.ecs.manage(OnMouseOver).remove(entity)
        if on_mouse_out:
            self.ecs.manage(OnMouseOut).remove(entity)
        if on_mouse_wheel:
            self.ecs.manage(OnMouseWheel).remove(entity)

