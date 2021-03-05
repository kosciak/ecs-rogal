import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..console import ui

from .. import render

from ..utils import perf


log = logging.getLogger(__name__)


class CreateWindowsSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

        self.ui_manager = self.ecs.resources.ui_manager

    def init_windows(self):
        self.ecs.create(components.CreateWindow('IN_GAME'))

    def create_windows(self):
        to_create = self.ecs.manage(components.CreateWindow)
        if not to_create:
            return

        for window, create in to_create:
            self.ui_manager.create(window, create.window_type, create.context)

        to_create.clear()

    def run(self):
        if self.ecs.run_state == RunState.PRE_RUN:
            self.init_windows()
        self.create_windows()


class DestroyWindowsSystem(System):

    def run(self):
        to_destroy = self.ecs.manage(components.DestroyWindow)
        if not to_destroy:
            return

        for_removal = set(to_destroy.entities)

        parent_windows = self.ecs.manage(components.ParentWindow)
        for entity, parent in parent_windows:
            if parent in to_destroy:
                for_removal.add(entity)

        self.ecs.remove(*for_removal)

