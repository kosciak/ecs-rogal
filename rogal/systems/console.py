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
        panels = self.ecs.manage(components.Console)
        for widget, content in widgets:
            panel = panels.get(widget)
            if panel is None:
                content.layout(ui_manager, widget, self.root)
            else:
                content.layout_content(ui_manager, widget, panel.panel, panel.z_order)


class RenderingSystem(ConsoleSystem):

    FPS = 35

    def __init__(self, ecs):
        super().__init__(ecs)

        self.tileset = self.ecs.resources.tileset
        self.default_colors = Colors(self.tileset.palette.fg, self.tileset.palette.bg)

        self._last_run = None
        self._fps = None
        self.frame = None
        self.fps = self.FPS

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps
        self.frame = 1./self._fps

    def should_run(self, state):
        now = time.time()
        if self._last_run and now - self._last_run < self.frame:
            # Do NOT render more often than once a frame
            return False
        self._last_run = now
        return True

    def render(self):
        # Clear panel
        self.root.clear(self.default_colors)

        # Render all panels
        consoles = self.ecs.manage(components.Console)
        panel_renderers = self.ecs.manage(components.PanelRenderer)
        for console, panel_renderer in sorted(
            self.ecs.join(consoles, panel_renderers),
            key=itemgetter(0)
        ):
            with perf.Perf(panel_renderer.renderer.render):
                # TODO: pass timestamp / self._last_run to synchronize blinking / effects?
                panel_renderer.renderer.render(console.panel)

        # Show rendered panel
        self.wrapper.flush(self.root)

    def run(self):
        if not self.ecs.resources.current_player:
            return False

        self.render()
        return True

