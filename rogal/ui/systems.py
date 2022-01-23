import collections
import logging
from operator import itemgetter
import time

from ..utils import perf

from ..ecs import System
from ..ecs.run_state import RunState

from .components import (
    CreateUIElement, DestroyUIElement, DestroyUIElementContent,
    ParentUIElements, ChildUIElements,
    UIElement, UIElementChanged,
    UIStyle, UIStyleChanged,
    UILayout, UILayoutChanged,
    UIRenderer,
    InputFocus, HasInputFocus, GrabInputFocus,
)


log = logging.getLogger(__name__)


class CreateUIElementsSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.builder = self.ecs.resources.widgets_builder
        self.ui_manager = self.ecs.resources.ui_manager

    def run(self):
        to_create = self.ecs.manage(CreateUIElement)
        if not to_create:
            return

        parent_elements = self.ecs.manage(ParentUIElements)
        child_elements = self.ecs.manage(ChildUIElements)
        for element, create in to_create:
            content = self.builder.build(
                # TODO: pass element to builder?
                create.widget_type, create.context,
            )
            if content:
                parent_elements.insert(element, [])
                child_elements.insert(element, [])
                content.insert(self.ui_manager, element)

        to_create.clear()


class DestroyUIElementsSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        children_to_remove = set()
        child_elements = self.ecs.manage(ChildUIElements)

        destroy = self.ecs.manage(DestroyUIElement)
        if destroy:
            for element, children in self.ecs.join(destroy.entities, child_elements):
                children_to_remove.update(children)

        destroy_contents = self.ecs.manage(DestroyUIElementContent)
        for element, children in self.ecs.join(destroy_contents.entities, child_elements):
            children_to_remove.update(children)

        self.ecs.remove(
            *children_to_remove,
            *destroy.entities,
        )
        destroy_contents.clear()


class StyleSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.stylesheets = self.ecs.resources.stylesheets_manager

    def run(self):
        changed = self.ecs.manage(UIStyleChanged)
        if not changed:
            return
        styles = self.ecs.manage(UIStyle)
        elements = self.ecs.manage(UIElement)
        for element, content, style in self.ecs.join(changed.entities, elements, styles):
            content.content.set_style(**self.stylesheets.get(style.selector))
        changed.clear()


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
        RunState.RENDER,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.ui_manager = self.ecs.resources.ui_manager

    def run(self):
        changed_elements = self.ecs.manage(UIElementChanged)
        if not changed_elements:
            return
        elements = self.ecs.manage(UIElement)
        child_elements = self.ecs.manage(ChildUIElements)
        layouts = self.ecs.manage(UILayout)
        changed_layouts = self.ecs.manage(UILayoutChanged)
        changed_layouts.clear()

        for element, children, content in self.ecs.join(changed_elements.entities, child_elements, elements):
            layouts.remove(*children)
            layout = layouts.get(element)
            if layout is None:
                content.layout(self.ui_manager, panel=self.root, z_order=0)
            else:
                # TODO: This works ONLY if we are redrawing children, but not widget itself
                #       for example after resizing it! It would need panel from it's parent!
                content.layout_content(self.ui_manager, panel=layout.panel, z_order=layout.z_order)
            changed_layouts.insert(element)
        changed_elements.clear()


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
        changed_layouts = self.ecs.manage(UILayoutChanged)
        if not changed_layouts:
            return
        self.focus_manager.clear_positions()
        elements = self.ecs.manage(UIElement)
        layouts = self.ecs.manage(UILayout)
        # NOTE: Use only UIElements, we don't want renderers that might have higher z_order to mask widgets
        for element, layout in sorted(self.ecs.join(elements.entities, layouts), key=lambda e: e[1].z_order):
            self.focus_manager.update_positions(element, layout.panel)


class RenderSystem(UISystem):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        # Render all panels
        layouts = self.ecs.manage(UILayout)
        renderers = self.ecs.manage(UIRenderer)
        # NOTE: Using monotonic timestamp in miliseconds as render timestamp, 
        #       this way all effects depending on time (blinking, fading, etc)
        #       are going to be synchronized
        timestamp = time.monotonic_ns() // 1e6
        for layout, renderer in sorted(
            self.ecs.join(layouts, renderers),
            key=itemgetter(0) # Sort by layout.z_order
        ):
            with perf.Perf(renderer.renderer.render):
                renderer.render(layout.panel, timestamp)


class DisplaySystem(UISystem):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        # Show rendered panel
        with perf.Perf(self.wrapper.render):
            self.wrapper.render(self.root)

