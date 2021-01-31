import logging
import time

from .geometry import Direction
from .player import try_move, try_change_level, reveal_level


log = logging.getLogger(__name__)


class InputHandler:

    def __init__(self, wrapper, keys):
        self.wrapper = wrapper
        self.keys = keys

    def dispatch(self, event, *args, **kwargs):
        if event.type is None:
            return
        fn_name = f'on_{event.type.lower()}'
        fn = getattr(self, fn_name, None)
        if fn:
            return fn(event, *args, **kwargs)

    def handle(self, wait=None, *args, **kwargs):
        for event in self.wrapper.events(wait):
            # log.debug(f'Event: {event}')
            return self.dispatch(event, *args, **kwargs)

    def on_quit(self, event):
        log.warning('Quitting...')
        raise SystemExit()


class PlayerActionsHandler(InputHandler):

    REPEAT_LIMIT = 1./6

    def __init__(self, ecs, spatial, wrapper, keys):
        super().__init__(wrapper, keys)
        self.ecs = ecs
        self.spatial = spatial
        self.last_keydown = None

    def on_keydown(self, event, actor):
        # log.debug(f'Event: {event}')
        # print(f'Key: {event.key!r}')
        if event.repeat:
            if self.last_keydown and time.time() - self.last_keydown < self.REPEAT_LIMIT:
                # Skip repeated keys to prevent stacking of unprocessed events
                return
        self.last_keydown = time.time()

        if event.key in self.keys.actions.QUIT:
            log.warning('Quitting...')
            raise SystemExit()

        if event.key in self.keys.actions.REVEAL_LEVEL:
            return reveal_level(self.ecs, self.spatial, actor)

        if event.key in self.keys.actions.NEXT_LEVEL:
            return try_change_level(self.ecs, actor, 1)
        if event.key in self.keys.actions.PREV_LEVEL:
            return try_change_level(self.ecs, actor, -1)

        if event.key in self.keys.actions.WAIT:
            log.info('Waiting...')
            return 60

        for direction in Direction:
            if event.key in self.keys.directions[direction.name]:
                return try_move(self.ecs, self.spatial, actor, direction)

