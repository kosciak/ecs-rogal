import logging
from operator import itemgetter
import time

from ..utils import perf

from ..ecs import System
from ..ecs.run_state import RunState

from .components import (
    CreateUIElement, DestroyUIElement, DestroyUIElementContent,
    ParentUIElement,
    UIWidget,
    NeedsLayout,
    UIPanel,
    UIRenderer,
)


log = logging.getLogger(__name__)


class CreateUIElementsSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.RENDER,
    }

    def run(self):
        to_create = self.ecs.manage(CreateUIElement)
        if not to_create:
            return

        # TODO: Needs some rework...
        #       Better names, why insert as UIWidget? To have layout point?
        widgets_builder = self.ecs.resources.widgets_builder
        widgets = self.ecs.manage(UIWidget)
        needs_layout = self.ecs.manage(NeedsLayout)
        for element, create in to_create:
            widget = widgets_builder.build(
                create.widget_type, create.context,
            )
            widgets.insert(element, widget)
            needs_layout.insert(element)

        to_create.clear()


class DestroyUIElementsSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def get_children(self, parents):
        parent_elements = self.ecs.manage(ParentUIElement)
        children = set()
        for element, parent in parent_elements:
            if parent in parents:
                children.add(element)
        if children:
            children.update(self.get_children(children))
        return children

    def run(self):
        to_destroy = self.ecs.manage(DestroyUIElement)
        if to_destroy:
            parents = set(to_destroy.entities)
            self.ecs.remove(*parents)
            children = self.get_children(parents)
            self.ecs.remove(*children)
        to_destroy.clear()

        to_destroy = self.ecs.manage(DestroyUIElementContent)
        if to_destroy:
            children = self.get_children(to_destroy.entities)
            self.ecs.remove(*children)
        to_destroy.clear()


class UISystem(System):

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


class LayoutSytem(UISystem):

    INCLUDE_STATES = {
        RunState.PRE_RUN, # TODO: Not sure why it MUST be enabled during PRE_RUN...
        RunState.RENDER,
    }

    def run(self):
        needs_layout = self.ecs.manage(NeedsLayout)
        if not needs_layout:
            return
        ui_manager = self.ecs.resources.ui_manager
        widgets = self.ecs.manage(UIWidget)
        panels = self.ecs.manage(UIPanel)
        for element, content in self.ecs.join(needs_layout.entities, widgets):
            panel = panels.get(element)
            if panel is None:
                content.layout(ui_manager, element, panel=self.root, z_order=0)
            else:
                content.layout_content(ui_manager, element, panel=panel.panel, z_order=panel.z_order)

        needs_layout.clear()


class OnScreenContentSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.onscreen_manager = self.ecs.resources.onscreen_manager

    def run(self):
        widgets = self.ecs.manage(UIWidget)
        panels = self.ecs.manage(UIPanel)
        # NOTE: Use only UIWidgets, we don't want renderers that might have higher z_order to mask widgets
        for widget, panel in sorted(self.ecs.join(widgets.entities, panels), key=lambda e: e[1].z_order):
            self.onscreen_manager.update_positions(widget, panel.panel)


class RenderSystem(UISystem):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        # Clear panel
        self.root.clear()

        # Render all panels
        panels = self.ecs.manage(UIPanel)
        renderers = self.ecs.manage(UIRenderer)
        # NOTE: Using monotonic timestamp in miliseconds as render timestamp, 
        #       this way all effects depending on time (blinking, fading, etc)
        #       are going to be synchronized
        timestamp = time.monotonic_ns() // 1e6
        for panel, renderer in sorted(
            self.ecs.join(panels, renderers),
            key=itemgetter(0) # Sort by panel.z_order
        ):
            with perf.Perf(renderer.renderer.render):
                renderer.render(panel.panel, timestamp)

        # Show rendered panel
        with perf.Perf(self.wrapper.render):
            self.wrapper.render(self.root)

