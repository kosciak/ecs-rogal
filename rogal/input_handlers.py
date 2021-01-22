import logging
import time

from . import keys
from .player import try_move


log = logging.getLogger(__name__)


class InputHandler:

    def __init__(self, wrapper):
        self.wrapper = wrapper

    def dispatch(self, event, *args, **kwargs):
        if event.type is None:
            return
        fn_name = f'on_{event.type.lower()}'
        fn = getattr(self, fn_name, None)
        if fn:
            return fn(event, *args, **kwargs)

    def handle(self, wait=None, *args, **kwargs):
        for event in self.wrapper.events(wait):
            log.debug(f'Event: {event}')
            return self.dispatch(event, *args, **kwargs)

    def on_quit(self, event):
        log.warning('Quitting...')
        raise SystemExit()


class PlayerActionsHandler(InputHandler):

    REPEAT_LIMI = 1./17

    def __init__(self, ecs, wrapper):
        self.ecs = ecs
        super().__init__(wrapper)
        self.last_keydown = None

    def on_keydown(self, event, actor):
        if event.repeat:
            if self.last_keydown and time.time() - self.last_keydown < self.REPEAT_LIMI:
                # Skip repeated keys to prevent stacking of unprocessed events
                return
        key = event.sym
        self.last_keydown = time.time()
        if key == keys.ESCAPE_KEY:
            log.warning('Quitting...')
            raise SystemExit()

        if key in keys.WAIT_KEYS:
            log.info('Waiting...')
            return 60

        direction = keys.MOVE_KEYS.get(key)
        if direction:
            return try_move(self.ecs, actor, direction)

