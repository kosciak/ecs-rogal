import logging
from operator import itemgetter
import time

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

        # TODO: Needs some rework...
        #       Better names, why insert as UIWidget? To have layout point?
        widgets_builder = self.ecs.resources.widgets_builder
        widgets = self.ecs.manage(components.UIWidget)
        for window, create in to_create:
            widget = widgets_builder.build(
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


class OnScreenContentSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)
        self.onscreen_manager = self.ecs.resources.onscreen_manager

    def run(self):
        widgets = self.ecs.manage(components.UIWidget)
        consoles = self.ecs.manage(components.Console)
        # NOTE: Use only UIWidgets, we don't want renderers that might have higher z_order to mask widgets
        for widget, console in sorted(self.ecs.join(widgets.entities, consoles), key=lambda e: e[1].z_order):
            self.onscreen_manager.update_positions(widget, console.panel)


class RenderSystem(ConsoleSystem):

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

