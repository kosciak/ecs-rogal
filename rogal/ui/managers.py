import collections
import logging

import numpy as np

from ..ecs.core import Entity, EntitiesSet

from ..toolkit.core import ZOrder

from .components import (
    CreateUIElement, DestroyUIElement, DestroyUIElementContent,
    ParentUIElements, ChildUIElements,
    UIElement, UIElementChanged,
    UIStyle, UIStyleChanged,
    UIRenderer,
    UILayout,
    GrabInputFocus, InputFocus, HasInputFocus,
)


log = logging.getLogger(__name__)


class UIManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self._stylesheets = None
        self._events = None
        self._signals = None
        self._focus = None

    @property
    def stylesheets(self):
        if self._stylesheets is None:
            self._stylesheets = self.ecs.resources.stylesheets_manager
        return self._stylesheets

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
        child_elements.insert(element, [])

        parent_elements = self.ecs.manage(ParentUIElements)
        parents = parent_elements.insert(
            element,
            [parent, *parent_elements.get(parent, [])]
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
                element, content,
            )
            self.ecs.manage(UIElementChanged).insert(element)
        if renderer:
            self.ecs.manage(UIRenderer).insert(
                element, renderer,
            )
        if selector:
            self.ecs.manage(UIStyle).insert(
                element, selector,
            )
            self.ecs.manage(UIStyleChanged).insert(element)
        if panel:
            self.ecs.manage(UILayout).insert(
                element, panel, z_order or ZOrder.BASE,
            )

    def update_style(self, element, selector, pseudo_class=None):
        styles = self.ecs.manage(UIStyle)
        style_changed = False
        style = styles.get(element)
        if style is None:
            style = styles.insert(element, '')
        if not (style.base == selector and style.pseudo_class == pseudo_class):
            style.base = selector
            style.pseudo_class = pseudo_class
            style_changed = True
        if style_changed:
            self.ecs.manage(UIStyleChanged).insert(element)

    def redraw(self, element):
        self.ecs.manage(UIElementChanged).insert(element)

    def bind(self, element, **handlers):
        self.events.bind(element, **handlers)

    def connect(self, element, handlers):
        self.signals.bind(element, handlers)

    # TODO: What about connecting to element (as an entity in ECS), not an instance?

    def emit(self, element, name, value=None):
        self.signals.emit(element, name, value)

    def grab_focus(self, element):
        self.focus.grab(element)

    # TODO: get_focus -> just set current InputFocus value, not higher one!
    #       switch_focus?

    def release_focus(self, element):
        self.focus.release(element)


class InputFocusManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self._positions = None
        # TODO: consider adding pixel_positions ??

    @property
    def positions(self):
        if self._positions is None:
            root_panel = self.ecs.resources.root_panel
            self._positions = np.zeros(root_panel.size, dtype=(np.void, 16), order="C")
        return self._positions

    def clear_positions(self):
        self._positions = None
        # self.parents.clear()

    def grab(self, element):
        self.ecs.manage(GrabInputFocus).insert(element)

    # TODO: get(self, element) -> change focus, grab without changing current priority

    def release(self, element):
        self.ecs.manage(InputFocus).remove(element)

    def update_positions(self, entity, panel):
        self.positions[panel.x : panel.x2, panel.y : panel.y2] = entity.bytes

    def propagate_from(self, entity):
        if not entity:
            return
        yield entity
        parent_elements = self.ecs.manage(ParentUIElements)
        for parent in parent_elements.get(entity, []):
            yield parent

    def get_position(self, position):
        # NOTE: On terminal position might be outside root console!
        max_x, max_y = self.positions.shape
        if position.x >= max_x or position.y >= max_y:
            return
        return Entity(self.positions[position].tobytes())

    def propagate_from_position(self, position):
        target = self.get_position(position)
        yield from self.propagate_from(target)

    def propagate_from_focused(self):
        # TODO: Generator with correct order of parents instead of EntitiesSet?
        # TODO: Return single entity that is focused, use propagate_from() to get parents
        #       OR maybe propaget NOT based on parents for focued? Whatever works
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

