import collections
import logging

import numpy as np

from ..ecs.core import Entity, EntitiesSet

from ..toolkit.core import ZOrder

from .components import (
    CreateElement, DestroyElement, DestroyElementContent,
    ElementPath, ChildElements,
    Widget, ContentChanged, SelectorChanged,
    Renderer,
    Layout,
    GrabInputFocus, InputFocus, HasInputFocus, CurrentInputFocus,
)


log = logging.getLogger(__name__)


class UIManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self._events = None
        self._signals = None
        self._focus = None

    @property
    def events(self):
        if self._events is None:
            self._events = self.ecs.resources.events_manager
        return self._events

    @property
    def signals(self):
        if self._signals is None:
            self._signals = self.ecs.resources.signals_manager
        return self._signals

    @property
    def focus(self):
        if self._focus is None:
            self._focus = self.ecs.resources.focus_manager
        return self._focus

    def create(self, widget_type, context=None):
        widget = self.ecs.create(
            CreateElement(
                widget_type=widget_type,
                context=context,
            ),
        )
        return widget

    def destroy(self, element):
        self.ecs.manage(DestroyElement).insert(element)

    def create_child(self, parent):
        element = self.ecs.create()

        child_elements = self.ecs.manage(ChildElements)
        child_elements.insert(element)

        element_paths = self.ecs.manage(ElementPath)
        path = element_paths.get(parent, [])
        element_paths.insert(
            element, [
                *path,
                element,
            ]
        )
        for parent in path[:-1]:
            parent_children = child_elements.get(parent)
            parent_children.add(element)

        return element

    def insert(self, element, *,
               content=None,
               renderer=None,
               selector=None,
               panel=None,
               z_order=None,
              ):
        if content:
            self.ecs.manage(Widget).insert(
                element, content, selector,
            )
            self.ecs.manage(ContentChanged).insert(element)
            self.ecs.manage(SelectorChanged).insert(element)
        if renderer:
            self.ecs.manage(Renderer).insert(
                element, renderer,
            )
        if panel:
            self.ecs.manage(Layout).insert(
                element, panel, z_order or ZOrder.BASE,
            )

    def update_selector(self, element, pseudo_classes=None):
        widgets = self.ecs.manage(Widget)
        widget = widgets.get(element)
        pseudo_classes = set(pseudo_classes or [])
        if widget.selector.pseudo_classes == pseudo_classes:
            return
        widget.selector.pseudo_classes = pseudo_classes

        child_elements = self.ecs.manage(ChildElements)
        changed_selectors = self.ecs.manage(SelectorChanged)
        changed_selectors.insert(element)
        for child in child_elements.get(element):
            changed_selectors.insert(child)

    def redraw(self, element):
        self.ecs.manage(ContentChanged).insert(element)

    # TODO: focus handling needs rework!
    def grab_focus(self, element):
        self.focus.grab_focus(element)

    # TODO: get_focus -> just set current InputFocus value, not higher one!
    #       switch_focus?

    def release_focus(self, element):
        self.focus.release(element)


class InputFocusManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self._positions = None
        self.input_focus = None
        # TODO: consider adding pixel_positions ??

    @property
    def positions(self):
        if self._positions is None:
            root_panel = self.ecs.resources.root_panel
            self._positions = np.zeros(root_panel.size, dtype=(np.void, 16), order="C")
        return self._positions

    def clear_positions(self):
        self._positions = None

    def grab_focus(self, element):
        self.ecs.manage(GrabInputFocus).insert(element)

    def has_focus(self, element):
        self.ecs.manage(HasInputFocus).insert(element)

    def set_input_focus(self, element):
        self.input_focus = element

    # TODO: Obsolete?
    def release(self, element):
        self.ecs.manage(InputFocus).remove(element)

    def update_positions(self, entity, panel):
        self.positions[panel.x : panel.x2, panel.y : panel.y2] = entity.bytes

    def propagate_from(self, entity, filter_by=None):
        if not entity:
            return
        yield entity
        element_paths = self.ecs.manage(ElementPath)
        path = element_paths.get(entity, [])
        for element in reversed(path[:-1]):
            if filter_by is not None and not element in filter_by:
                continue
            yield element

    def get_position(self, position):
        # NOTE: On terminal position might be outside root console!
        max_x, max_y = self.positions.shape
        if position.x >= max_x or position.y >= max_y:
            return
        return Entity(self.positions[position].tobytes())

    def propagate_from_position(self, position):
        target = self.get_position(position)
        filter_by = self.ecs.manage(Widget)
        yield from self.propagate_from(target, filter_by)

    def propagate_from_focused(self):
        # TODO: Generator with correct order of parents instead of EntitiesSet?
        # TODO: Return single entity that is focused, use propagate_from() to get parents
        #       OR maybe propagate NOT based on parents for focued? Whatever works
        #       Right now Actor can be focused, so it won't work like that
        #       Need to completely redesign keeping track of focus
        elements = EntitiesSet()
        element_paths = self.ecs.manage(ElementPath)
        has_focus = self.ecs.manage(HasInputFocus)
        # for entity, parents in self.ecs.join(has_focus.entities, element_paths):
        for element in has_focus.entities:
            # TODO: Should be removed after all input handlers are bound to Elements
            elements.add(element)
            path = element_paths.get(element, [])
            elements.update(path)
        return elements

