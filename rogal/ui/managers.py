import collections
import logging

import numpy as np

from ..ecs.core import Entity, EntitiesSet

from ..toolkit.core import ZOrder

from .components import (
    CreateUIElement, DestroyUIElement, DestroyUIElementContent,
    ParentUIElement,
    UIElement, UIElementChanged,
    UIStyle, UIStyleChanged,
    UIRenderer,
    UIPanel,
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
        element = self.ecs.create(
            ParentUIElement(parent),
        )
        return element

    # TODO: Rename to set_pseudoclass()
    def set_style(self, element, selector):
        # TODO: restyling should be done in separate system
        content = self.ecs.manage(UIElement).get(element)
        style = self.stylesheets.get(selector)
        content.content.set_style(**style)
        # TODO: set pseudoclass (to UIStyle component), and add Restyle flag
        self.ecs.manage(UIStyleChanged).insert(element)

    def redraw(self, element):
        # TODO: redraw without destroying contents?
        self.ecs.manage(DestroyUIElementContent).insert(element)
        self.ecs.manage(UIElementChanged).insert(element)

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
        if renderer:
            self.ecs.manage(UIRenderer).insert(
                element, renderer,
            )
        if selector:
            self.ecs.manage(UIStyle).insert(
                element, selector,
            )
        if panel:
            self.ecs.manage(UIPanel).insert(
                element, panel, z_order or ZOrder.BASE,
            )

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
        self.parents = collections.defaultdict(EntitiesSet)
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

    def get_parents_gen(self, entity):
        parents = self.ecs.manage(ParentUIElement)
        while entity:
            yield entity
            entity = parents.get(entity)

    def get_parents(self, entity):
        if not entity in self.parents:
            self.parents[entity].update(self.get_parents_gen(entity))
        return self.parents[entity]

    def update_positions(self, entity, panel):
        self.positions[panel.x : panel.x2, panel.y : panel.y2] = entity.bytes

    def get_entity(self, position):
        # NOTE: On terminal position might be outside root console!
        max_x, max_y = self.positions.shape
        if position.x >= max_x or position.y >= max_y:
            return
        return Entity(self.positions[position].tobytes())

    def get_entities(self, position=None):
        entities = EntitiesSet()
        if position is None:
            has_focus = self.ecs.manage(HasInputFocus)
            for entity in has_focus.entities:
                entities.update(self.get_parents(entity))
        else:
            entity = self.get_entity(position)
            entities.update(self.get_parents(entity))
        return entities

