import logging

from ...events import EventType

from ..sdl.input import SDLInputWrapper


log = logging.getLogger(__name__)


MOUSE_EVENT_TYPES = {
    EventType.MOUSE_MOTION,
    EventType.MOUSE_BUTTON_PRESS,
    EventType.MOUSE_BUTTON_UP,
}


class TcodSDLInputWrapper(SDLInputWrapper):

    def __init__(self, sdl2, context):
        super().__init__(sdl2=sdl2)
        self.context = context

    def update_mouse_event(self, event):
        pixel_position = event.position
        x, y = self.context.pixel_to_tile(*pixel_position)
        event.set_position(x, y)
        event.set_pixel_position(*pixel_position)

        if event.type == EventType.MOUSE_MOTION:
            pixel_motion = event.motion
            prev_position = event.pixel_position.moved_from(pixel_motion)
            prev_x, prev_y = self.context.pixel_to_tile(*prev_position)
            dx = event.position.x - prev_x
            dy = event.position.y - prev_y
            event.set_motion(dx, dy)
            event.set_pixel_motion(*pixel_motion)

        return event

    def process_mouse_position(self, events_gen):
        for event in events_gen:
            if event.type in MOUSE_EVENT_TYPES:
                event = self.update_mouse_event(event)
            yield event

