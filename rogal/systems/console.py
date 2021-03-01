import logging
import time

from .. import components
from ..ecs import System
from ..ecs.run_state import RunState

from ..tiles import Colors

from ..utils import perf


log = logging.getLogger(__name__)


class RenderingSystem(System):

    FPS = 35

    def __init__(self, ecs):
        super().__init__(ecs)

        self.tileset = self.ecs.resources.tileset
        self.default_colors = Colors(self.tileset.palette.fg, self.tileset.palette.bg)

        self.wrapper = self.ecs.resources.wrapper
        self._root = None

        self._last_run = None
        self._fps = None
        self.frame = None
        self.fps = self.FPS

    @property
    def root(self):
        if self.ecs.resources.root_panel is None:
            self.ecs.resources.root_panel = self.wrapper.create_panel()
        self._root = self.ecs.resources.root_panel
        return self._root

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
        renderers = self.ecs.manage(components.PanelRenderer)
        for panel, renderer in renderers:
            with perf.Perf(renderer.renderer.render):
                renderer.clear(self.default_colors)
                renderer.render()

        # Show rendered panel
        self.wrapper.flush(self.root)

    def run(self):
        if not self.ecs.resources.current_player:
            return False

        self.render()
        return True

