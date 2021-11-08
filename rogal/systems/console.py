import logging
from operator import itemgetter
import time

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..tiles import Colors

from ..utils import perf


log = logging.getLogger(__name__)


class ConsoleSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

        self.wrapper = self.ecs.resources.wrapper
        self._root = None

    @property
    def root(self):
        if self.ecs.resources.root_panel is None:
            panel = self.wrapper.create_panel()
            self.ecs.resources.root_panel = panel
        self._root = self.ecs.resources.root_panel
        return self._root


class LayoutSytem(ConsoleSystem):

    INCLUDE_STATES = {
        RunState.PRE_RUN, # TODO: Not sure why it MUST be enabled during PRE_RUN...
        RunState.RENDER,
    }

    def get_widgets_to_update(self):
        widgets = self.ecs.manage(components.UIWidget)
        to_update = [
            (widget, content) for widget, content in widgets
            if content.needs_update
        ]
        return to_update

    def run(self):
        widgets = self.get_widgets_to_update()
        if not widgets:
            return
        ui_manager = self.ecs.resources.ui_manager
        consoles = self.ecs.manage(components.Console)
        for widget, content in widgets:
            console = consoles.get(widget)
            if console is None:
                content.layout(ui_manager, widget, panel=self.root, z_order=0)
            else:
                content.layout_content(ui_manager, widget, panel=console.panel, z_order=console.z_order)


class RenderingSystem(ConsoleSystem):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        # Clear panel
        self.root.clear()

        # Render all panels
        consoles = self.ecs.manage(components.Console)
        panel_renderers = self.ecs.manage(components.PanelRenderer)
        # NOTE: Using monotonic timestamp in miliseconds as render timestamp, 
        #       this way all effects depending on time (blinking, fading, etc)
        #       are going to be synchronized
        timestamp = time.monotonic_ns() // 1e6
        for console, panel_renderer in sorted(
            self.ecs.join(consoles, panel_renderers),
            key=itemgetter(0)
        ):
            with perf.Perf(panel_renderer.renderer.render):
                panel_renderer.renderer.render(console.panel, timestamp)

        # Show rendered panel
        with perf.Perf(self.wrapper.render):
            self.wrapper.render(self.root)

