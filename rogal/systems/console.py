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
            self.ecs.resources.root_panel = self.wrapper.create_panel()
        self._root = self.ecs.resources.root_panel
        return self._root


class LayoutSytem(ConsoleSystem):

    def run(self):
        ui_manager = self.ecs.resources.ui_manager
        window_wigdets = self.ecs.manage(components.WindowWidgets)
        for window, widgets in window_wigdets:
            if not widgets.needs_update:
                continue
            widgets.layout(ui_manager, window, self.root)


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
        z_order = self.ecs.manage(components.ZOrder)
        panels = self.ecs.manage(components.ConsolePanel)
        renderers = self.ecs.manage(components.PanelRenderer)
        for z, panel, renderer in sorted(
            self.ecs.join(z_order, panels, renderers),
            key=itemgetter(0)
        ):
            with perf.Perf(renderer.renderer.render):
                renderer.clear(panel, self.default_colors)
                renderer.render(panel)

        # Show rendered panel
        self.wrapper.flush(self.root)

    def run(self):
        if not self.ecs.resources.current_player:
            return False

        self.render()
        return True

