import logging
import time

from . import components

from .utils import perf


log = logging.getLogger(__name__)


class GameLoop:

    ANIMATIONS_FPS = 60
    INPUT_FPS = 35

    def __init__(self, ecs, renderer):
        self.ecs = ecs
        self.renderer = renderer

    def render(self, actor):
        perf_stats = perf.Perf('render.Renderer.render()')
        if self.renderer.render(actor):
            perf_stats.elapsed()

    def join(self):
        acts_now = self.ecs.manage(components.ActsNow)
        players = self.ecs.manage(components.Player)
        player = None

        self.ecs.run()
        while True:
            # This is ugly...
            for actor in players.entities:
                if actor in acts_now:
                    player = actor

            self.render(player)

            self.ecs.run()

