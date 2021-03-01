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

        self.wrapper = self.ecs.resources.wrapper
        self._root = None

    @property
    def root(self):
        if self.ecs.resources.root_panel is None:
            self.ecs.resources.root_panel = self.wrapper.create_panel()
        self._root = self.ecs.resources.root_panel
        return self._root

    def init_windows(self):
        self.ecs.create(components.CreateWindow('IN_GAME'))

    def create_windows(self):
        to_create = self.ecs.manage(components.CreateWindow)
        window_renderers = self.ecs.manage(components.WindowRenderers)

        # TODO: some kind of console.UIManager should be called!
        #       Window system should not be aware of underlying wrapper / rendering
        layouts = []
        for window, create in to_create:
            if create.window_type == 'YES_NO_PROMPT':
                layout = ui.YesNoPrompt(**create.context)
                layouts.append([window, layout, self.root])

            if create.window_type == 'IN_GAME':
                cam_panel, msg_log_panel = self.root.split(bottom=12)
                # cam_panel = self.root.create_panel(Position(10,10), CAMERA_SIZE)
                layout = ui.Window(title='logs')
                widget = render.MessageLog()
                layout.content.append(widget)
                layouts.append([window, layout, msg_log_panel])

                layout = ui.Window(title='mapcam')
                widget = render.Camera(self.ecs)
                layout.content.append(widget)
                layouts.append([window, layout, cam_panel])

        for window, layout, panel in layouts:
            renderers = window_renderers.insert(window)
            for renderer in layout.layout(panel):
                renderer = self.ecs.create(
                    components.PanelRenderer(renderer),
                )
                renderers.add(renderer)

        to_create.clear()

    def run(self):
        if self.ecs.run_state == RunState.PRE_RUN:
            self.init_windows()
        self.create_windows()


class DestroyWindowsSystem(System):

    def run(self):
        to_destroy = self.ecs.manage(components.DestroyWindow)
        window_renderers = self.ecs.manage(components.WindowRenderers)

        for window, renderers in self.ecs.join(to_destroy.entities, window_renderers):
            self.ecs.remove(*renderers)

        self.ecs.remove(*to_destroy.entities)

