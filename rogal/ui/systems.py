import collections
import logging
from operator import itemgetter
import time

from ..utils import perf

from ..ecs import System
from ..ecs.run_state import RunState

from .components import (
    CreateUIElement, DestroyUIElement, DestroyUIElementContent,
    ParentUIElement,
    UIElement,
    UIElementChanged,
    UIPanel,
    UIRenderer,
    InputFocus, HasInputFocus, GrabInputFocus,
)


log = logging.getLogger(__name__)


class CreateUIElementsSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.RENDER,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.builder = self.ecs.resources.widgets_builder

    def run(self):
        to_create = self.ecs.manage(CreateUIElement)
        if not to_create:
            return

        elements = self.ecs.manage(UIElement)
        changed = self.ecs.manage(UIElementChanged)
        for element, create in to_create:
            content = self.builder.build(
                # TODO: pass element to builder?
                create.widget_type, create.context,
            )
            elements.insert(element, content)
            changed.insert(element)

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
        # RunState.PRE_RUN, # TODO: Not sure why it MUST be enabled during PRE_RUN...
        RunState.RENDER,
    }

    def run(self):
        changed = self.ecs.manage(UIElementChanged)
        if not changed:
            return
        ui_manager = self.ecs.resources.ui_manager
        elements = self.ecs.manage(UIElement)
        panels = self.ecs.manage(UIPanel)
        for element, content in self.ecs.join(changed.entities, elements):
            panel = panels.get(element)
            if panel is None:
                content.layout(ui_manager, element, panel=self.root, z_order=0)
            else:
                # TODO: This works ONLY if we are redrawing children, but not widget itself
                #       for example after resizing it! It would need panel from it's parent!
                content.layout_content(ui_manager, element, panel=panel.panel, z_order=panel.z_order)

        changed.clear()


class InputFocusSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        # TODO: This is a mess...
        # TODO: Integrate with ui.managers.InputFocusManager
        input_focus = self.ecs.manage(InputFocus)
        grab_focus = self.ecs.manage(GrabInputFocus)
        has_focus = self.ecs.manage(HasInputFocus)

        focus_per_priority = collections.defaultdict(set)
        for entity, priority in input_focus:
            focus_per_priority[priority].add(entity)

        max_priority = max(focus_per_priority.keys() or [0, ])
        next_priority = max_priority
        if has_focus:
            next_priority = max_priority + 1

        for entity in grab_focus.entities:
            if entity in has_focus:
                continue
            focus_per_priority[next_priority].add(entity)
            input_focus.insert(entity, next_priority)
        grab_focus.clear()

        has_focus.clear()
        max_priority = max(focus_per_priority.keys() or [0, ])
        for entity in focus_per_priority.get(max_priority, []):
            has_focus.insert(entity)


class OnScreenFocusSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.focus_manager = self.ecs.resources.focus_manager

    def run(self):
        self.focus_manager.clear_positions()
        elements = self.ecs.manage(UIElement)
        panels = self.ecs.manage(UIPanel)
        # NOTE: Use only UIElements, we don't want renderers that might have higher z_order to mask widgets
        for element, panel in sorted(self.ecs.join(elements.entities, panels), key=lambda e: e[1].z_order):
            self.focus_manager.update_positions(element, panel.panel)


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

