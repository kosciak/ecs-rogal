import collections
import logging

import numpy as np

from ..ecs.core import Entity, EntitiesSet

from ..toolkit.core import ZOrder

from .components import (
    CreateUIElement, DestroyUIElement, DestroyUIElementContent,
    ParentUIElements, ChildUIElements,
    UIElement, UIElementChanged,
    UIStyleChanged,
    UIRenderer,
    UILayout,
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
            CreateUIElement(
                widget_type=widget_type,
                context=context,
            ),
        )
        return widget

    def destroy(self, element):
        self.ecs.manage(DestroyUIElement).insert(element)

    def create_child(self, parent):
        element = self.ecs.create()

        child_elements = self.ecs.manage(ChildUIElements)
        child_elements.insert(element)

        parent_elements = self.ecs.manage(ParentUIElements)
        parents = parent_elements.get(parent, [])
        parent_elements.insert(
            element, [
                *parents,
                element,
            ]
        )
        for parent in parents:
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
            self.ecs.manage(UIElement).insert(
                element, content, selector,
            )
            self.ecs.manage(UIElementChanged).insert(element)
            self.ecs.manage(UIStyleChanged).insert(element)
        if renderer:
            self.ecs.manage(UIRenderer).insert(
                element, renderer,
            )
        if panel:
            self.ecs.manage(UILayout).insert(
                element, panel, z_order or ZOrder.BASE,
            )

    def update_selector(self, element, pseudo_classes=None):
        widgets = self.ecs.manage(UIElement)
        widget = widgets.get(element)
        pseudo_classes = set(pseudo_classes or [])
        if widget.selector.pseudo_classes == pseudo_classes:
            return
        widget.selector.pseudo_classes = pseudo_classes

        child_elements = self.ecs.manage(ChildUIElements)
        style_changed = self.ecs.manage(UIStyleChanged)
        style_changed.insert(element)
        for child in child_elements.get(element):
            style_changed.insert(child)

    def redraw(self, element):
        self.ecs.manage(UIElementChanged).insert(element)

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
        parent_elements = self.ecs.manage(ParentUIElements)
        for parent in reversed(parent_elements.get(entity, [])):
            if filter_by is not None and not parent in filter_by:
                continue
            yield parent

    def get_position(self, position):
        # NOTE: On terminal position might be outside root console!
        max_x, max_y = self.positions.shape
        if position.x >= max_x or position.y >= max_y:
            return
        return Entity(self.positions[position].tobytes())

    def propagate_from_position(self, position):
        target = self.get_position(position)
        filter_by = self.ecs.manage(UIElement)
        yield from self.propagate_from(target, filter_by)

    def propagate_from_focused(self):
        # TODO: Generator with correct order of parents instead of EntitiesSet?
        # TODO: Return single entity that is focused, use propagate_from() to get parents
        #       OR maybe propagate NOT based on parents for focued? Whatever works
        #       Right now Actor can be focused, so it won't work like that
        #       Need to completely redesign keeping track of focus
        entities = EntitiesSet()
        parent_elements = self.ecs.manage(ParentUIElements)
        has_focus = self.ecs.manage(HasInputFocus)
        # for entity, parents in self.ecs.join(has_focus.entities, parent_elements):
        for entity in has_focus.entities:
            entities.add(entity)
            # TODO: Should be removed after all input handlers are bound to UIElements
            parents = parent_elements.get(entity, [])
            entities.update(parents)
        return entities

