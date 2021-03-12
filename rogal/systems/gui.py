import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class CreateWindowsSystem(System):

    def init_windows(self):
        self.ecs.create(components.CreateWindow('IN_GAME'))

    def create_windows(self):
        to_create = self.ecs.manage(components.CreateWindow)
        if not to_create:
            return

        ui_manager = self.ecs.resources.ui_manager
        window_wigdets = self.ecs.manage(components.WindowWidgets)
        for window, create in to_create:
            widgets_layout = ui_manager.create_widgets_layout(
                window, create.window_type, create.context,
            )
            window_wigdets.insert(window, widgets_layout)

        to_create.clear()

    def run(self):
        if self.ecs.run_state == RunState.PRE_RUN:
            self.init_windows()
        self.create_windows()


class DestroyWindowsSystem(System):

    def get_children(self, parents):
        parent_windows = self.ecs.manage(components.ParentWindow)
        children = set()
        for entity, parent in parent_windows:
            if parent in parents:
                children.add(entity)
        return children

    def run(self):
        to_destroy = self.ecs.manage(components.DestroyWindow)
        if not to_destroy:
            return

        parents = set(to_destroy.entities)
        while parents:
            children = self.get_children(parents)
            self.ecs.remove(*parents)
            parents = children

