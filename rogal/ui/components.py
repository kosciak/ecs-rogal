import functools

from ..ecs import Component
from ..ecs.components import Flag, Int, List, EntityReference, EntitiesRefs

from .stylesheets import Selector


# TODO: Rename widget_* to element_*
# TODO: Rename CreateUIElement to BuildUIElement?
class CreateUIElement(Component):
    __slots__ = ('widget_type', 'context', )

    def __init__(self, widget_type, context=None):
        self.widget_type = widget_type
        self.context = context or {}


ParentUIElements = List('ParentUIElements') # TODO: UIPath? From root element to element itself
ChildUIElements = EntitiesRefs('ChildUIElements') # TODO: Descendants? These are ALL children, added recursively


DestroyUIElement = Flag('DestroyUIElement')

DestroyUIElementContent = Flag('DestroyUIElementContent')


# TODO: rename to UIWidget, combine with UIStyle (and use stylesheets.Selector)
class UIElement(Component):
    __slots__ = ('content', 'selector', )

    def __init__(self, content, selector=None):
        self.content = content
        self.selector = Selector.parse(selector)

    def __getattr__(self, name):
        return getattr(self.content, name)


# TODO: rename to UIContentChanged
UIElementChanged = Flag('UIElementChanged')


UIStyleChanged = Flag('UIStyleChanged')


@functools.total_ordering
class UILayout(Component):
    __slots__ = ('panel', 'z_order', )

    def __init__(self, panel, z_order):
        self.panel = panel
        self.z_order = z_order

    def __lt__(self, other):
        return self.z_order < other.z_order


UILayoutChanged = Flag('UILayoutChanged')


class UIRenderer(Component):
    __slots__ = ('renderer', )

    def __init__(self, renderer):
        self.renderer = renderer

    def __getattr__(self, name):
        return getattr(self.renderer, name)


# TODO: Keyboard input handling needs major redesign!
InputFocus = Int('InputFocus')

GrabInputFocus = Flag('GrabInputFocus')

HasInputFocus = Flag('HasInputFocus')

CurrentInputFocus = Flag('CurrentInputFocus')

