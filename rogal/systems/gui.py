import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class CreateUIElementsSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.RENDER,
    }

    def init_windows(self):
        self.ecs.create(components.CreateUIElement('IN_GAME'))
        # self.ecs.create(components.CreateUIElement('MAIN_MENU'))

    def create_windows(self):
        to_create = self.ecs.manage(components.CreateUIElement)
        if not to_create:
            return

        ui_manager = self.ecs.resources.ui_manager
        widgets = self.ecs.manage(components.UIWidget)
        for window, create in to_create:
            widget = ui_manager.create_widget(
                create.widget_type, create.context,
            )
            widgets.insert(window, widget)

        to_create.clear()

    def run(self):
        if self.ecs.run_state == RunState.PRE_RUN:
            self.init_windows()
        self.create_windows()


class DestroyUIElementsSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def get_children(self, parents):
        parent_elements = self.ecs.manage(components.ParentUIElement)
        children = set()
        for element, parent in parent_elements:
            if parent in parents:
                children.add(element)
        if children:
            children.update(self.get_children(children))
        return children

    def run(self):
        to_destroy = self.ecs.manage(components.DestroyUIElement)
        if to_destroy:
            parents = set(to_destroy.entities)
            self.ecs.remove(*parents)
            children = self.get_children(parents)
            self.ecs.remove(*children)
        to_destroy.clear()

        to_destroy = self.ecs.manage(components.DestroyUIElementContent)
        if to_destroy:
            children = self.get_children(to_destroy.entities)
            self.ecs.remove(*children)
        to_destroy.clear()

