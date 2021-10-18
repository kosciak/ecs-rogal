import logging

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


class CreateUIWidgetsSystem(System):

    # INCLUDE_STATES = {
    #     RunState.WAIT_FOR_INPUT,
    #     RunState.RENDER,
    # }

    def init_windows(self):
        self.ecs.create(components.CreateUIWidget('IN_GAME'))
        # self.ecs.create(components.CreateUIWidget('MAIN_MENU'))

    def create_windows(self):
        to_create = self.ecs.manage(components.CreateUIWidget)
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


class DestroyUIWidgetsSystem(System):

#     INCLUDE_STATES = {
#         RunState.WAIT_FOR_INPUT,
#         RunState.RENDER,
#     }

    def get_children(self, parents):
        parent_windows = self.ecs.manage(components.ParentUIWidget)
        children = set()
        for entity, parent in parent_windows:
            if parent in parents:
                children.add(entity)
        if children:
            children.update(self.get_children(children))
        return children

    def run(self):
        to_destroy = self.ecs.manage(components.DestroyUIWidget)
        if to_destroy:
            parents = set(to_destroy.entities)
            self.ecs.remove(*parents)
            children = self.get_children(parents)
            self.ecs.remove(*children)
        to_destroy.clear()

        to_destroy = self.ecs.manage(components.DestroyUIWidgetChildren)
        if to_destroy:
            children = self.get_children(to_destroy.entities)
            self.ecs.remove(*children)
        to_destroy.clear()

