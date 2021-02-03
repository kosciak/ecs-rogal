import logging
import time

from . import components

from .utils import perf


log = logging.getLogger(__name__)


class GameLoop:

    def __init__(self, ecs):
        self.ecs = ecs

    def join(self):
        self.ecs.run()
        while True:
            self.ecs.run()

