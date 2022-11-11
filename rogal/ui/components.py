import functools

from ..ecs import Component
from ..ecs.components import Flag, Int, List, EntityReference, EntitiesRefs

from .stylesheets import Selector


# TODO: Rename widget_* to element_*
# TODO: Rename CreateElement to BuildElement?
class CreateElement(Component):
    __slots__ = ('widget_type', 'context', )

    def __init__(self, widget_type, context=None):
        self.widget_type = widget_type
        self.context = context or {}


ElementPath = List('ElementPath')
ChildElements = EntitiesRefs('ChildElements')


DestroyElement = Flag('DestroyElement')

DestroyElementContent = Flag('DestroyElementContent')


class Widget(Component):
    __slots__ = ('content', 'selector', )

    def __init__(self, content, selector=None):
        self.content = content
        self.selector = Selector.parse(selector)

    def __getattr__(self, name):
        return getattr(self.content, name)


ContentChanged = Flag('ContentChanged')
SelectorChanged = Flag('SelectorChanged')


@functools.total_ordering
class Layout(Component):
    __slots__ = ('panel', 'z_order', )

    def __init__(self, panel, z_order):
        self.panel = panel
        self.z_order = z_order

    def __lt__(self, other):
        return self.z_order < other.z_order


LayoutChanged = Flag('LayoutChanged')


class Renderer(Component):
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

