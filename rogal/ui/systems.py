import collections
import logging
from operator import itemgetter
import time

from ..utils import perf

from ..ecs import System
from ..ecs.run_state import RunState

from .components import (
    CreateElement, DestroyElement, DestroyElementContent,
    ElementPath, ChildElements,
    Widget, ContentChanged, SelectorChanged,
    Layout, LayoutChanged,
    Renderer,
    InputFocus, HasInputFocus, GrabInputFocus,
)


log = logging.getLogger(__name__)


class CreateElementsSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self._builder = None
        self.ui_manager = self.ecs.resources.ui_manager

    @property
    def builder(self):
        if self._builder is None:
            self._builder = self.ecs.resources.widgets_builder
        return self._builder

    def run(self):
        to_create = self.ecs.manage(CreateElement)
        if not to_create:
            return

        element_paths = self.ecs.manage(ElementPath)
        child_elements = self.ecs.manage(ChildElements)
        for element, create in to_create:
            content = self.builder.build(
                # TODO: pass element to builder?
                create.widget_type, create.context,
            )
            if content:
                element_paths.insert(element, [
                    element,
                ])
                child_elements.insert(element)
                content.insert(self.ui_manager, element)

        to_create.clear()


class DestroyElementsSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        children_to_remove = set()
        child_elements = self.ecs.manage(ChildElements)

        destroy = self.ecs.manage(DestroyElement)
        for element, children in self.ecs.join(destroy.entities, child_elements):
            children_to_remove.update(children)

        # TODO: OBSOLETE? Doesn't seem to be used anywhere now...
        destroy_contents = self.ecs.manage(DestroyElementContent)
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

    def get_selectors_path(self, element):
        element_paths = self.ecs.manage(ElementPath)
        widgets = self.ecs.manage(Widget)
        selectors_path = [
            widgets.get(element).selector
            for element in element_paths.get(element)
            if element in widgets
        ]
        return selectors_path

    def run(self):
        changed_selectors = self.ecs.manage(SelectorChanged)
        if not changed_selectors:
            return
        widgets = self.ecs.manage(Widget)
        for element, widget in self.ecs.join(changed_selectors.entities, widgets):
            selectors_path = self.get_selectors_path(element)
            # print('>>>', selectors_path)
            style = self.stylesheets.get(selectors_path)
            if not style:
                continue
            widget.set_style(**style)
        changed_selectors.clear()


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
        changed_contents = self.ecs.manage(ContentChanged)
        if not changed_contents:
            return
        widgets = self.ecs.manage(Widget)
        child_elements = self.ecs.manage(ChildElements)
        layouts = self.ecs.manage(Layout)
        changed_layouts = self.ecs.manage(LayoutChanged)
        changed_layouts.clear()

        for element, children, widget in self.ecs.join(changed_contents.entities, child_elements, widgets):
            layouts.remove(*children)
            layout = layouts.get(element)
            if layout is None:
                widget.layout(
                    self.ui_manager, panel=self.root, z_order=0, recalc=True,
                )
            else:
                # TODO: This works ONLY if we are redrawing children, but not widget itself
                #       for example after resizing it! It would need panel from it's parent!
                widget.layout_content(self.ui_manager, panel=layout.panel, z_order=layout.z_order)
            changed_layouts.insert(element)
        changed_contents.clear()


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


class FocusSystem(System):

    INCLUDE_STATES = {
        RunState.RENDER, # Maybe: RunState.WAIT_FOR_INPUT ?
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.focus_manager = self.ecs.resources.focus_manager


class GrabInputFocusSystem(FocusSystem):

    def run(self):
        grab_focus = self.ecs.manage(GrabInputFocus)
        if not grab_focus:
            return
        widgets = self.ecs.manage(Widget)
        for element, widget in self.ecs.join(grab_focus.entities, widgets):
            self.focus_manager.set_input_focus(
                widget.set_focus(),
            )
        grab_focus.clear()


class BlurInputFocusSystem(FocusSystem):

    def run(self):
        has_focus = self.ecs.manage(HasInputFocus)
        if not has_focus:
            return
        widgets = self.ecs.manage(Widget)
        to_blur = set()
        focused = self.focus_manager.propagate_from_focused()
        for element, widget in self.ecs.join(has_focus.entities, widgets):
            if not element in focused:
                widget.blur()
                to_blur.add(element)
        has_focus.remove(
            *to_blur,
        )


class ScreenPositionFocusSystem(FocusSystem):

    def run(self):
        changed_layouts = self.ecs.manage(LayoutChanged)
        if not changed_layouts:
            return
        self.focus_manager.clear_positions()
        widgets = self.ecs.manage(Widget)
        layouts = self.ecs.manage(Layout)
        # NOTE: Use only Widgets, we don't want renderers that might have higher z_order to mask widgets
        for element, layout in sorted(self.ecs.join(widgets.entities, layouts), key=lambda e: e[1].z_order):
            self.focus_manager.update_positions(element, layout.panel)


class RenderSystem(UISystem):

    INCLUDE_STATES = {
        RunState.RENDER,
    }

    def run(self):
        # Render all panels
        layouts = self.ecs.manage(Layout)
        renderers = self.ecs.manage(Renderer)
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

