import functools

from ..ecs import Component
from ..ecs.components import Flag, Int, EntityReference


# TODO: Rename widget_* to element_*
class CreateUIElement(Component):
    __slots__ = ('widget_type', 'context', )

    def __init__(self, widget_type, context=None):
        self.widget_type = widget_type
        self.context = context or {}


DestroyUIElement = Flag('DestroyUIElement')

DestroyUIElementContent = Flag('DestroyUIElementContent')


ParentUIElement = EntityReference('ParentUIElement')


class UIElement(Component):
    __slots__ = ('content', )

    def __init__(self, content):
        self.content = content

    def layout(self, ui_manager, parent, panel, z_order=0):
        self.content.layout(ui_manager, parent, panel, z_order)

    def layout_content(self, ui_manager, parent, panel, z_order):
        self.content.layout_content(ui_manager, parent, panel, z_order)


UIElementChanged = Flag('UIElementChanged')


class UIStyle(Component):
    __slots__ = ('base', 'pseudoclass', )

    def __init__(self, base, pseudoclass=None):
        self.base = base # TODO: Consider splitting into type, class(es)
        self.pseudoclass = pseudoclass

    @property
    def selector(self):
        if self.pseudoclass:
            return f'{self.base}:{self.pseudoclass}'
        else:
            return self.base


UIStyleChanged = Flag('UIStyleChanged')


@functools.total_ordering
class UIPanel(Component):
    __slots__ = ('panel', 'z_order', )

    def __init__(self, panel, z_order):
        self.panel = panel
        self.z_order = z_order

    def __lt__(self, other):
        return self.z_order < other.z_order


class UIRenderer(Component):
    __slots__ = ('renderer', )

    def __init__(self, renderer):
        self.renderer = renderer

    def render(self, panel, timestamp):
        self.renderer.render(panel, timestamp)


# TODO: Keyboard input handling needs major redesign!
InputFocus = Int('InputFocus')

GrabInputFocus = Flag('GrabInputFocus')

HasInputFocus = Flag('HasInputFocus')

