import functools

from ..ecs import Component

from ..ecs.components import Flag, EntityReference


class CreateUIElement(Component):
    __slots__ = ('widget_type', 'context', )

    def __init__(self, widget_type, context=None):
        self.widget_type = widget_type
        self.context = context or {}


DestroyUIElement = Flag('DestroyUIElement')

DestroyUIElementContent = Flag('DestroyUIElementContent')


ParentUIElement = EntityReference('ParentUIElement')


class UIWidget(Component):
    __slots__ = ('widget', )

    def __init__(self, widget):
        self.widget = widget

    def layout(self, ui_manager, parent, panel, z_order=0):
        self.widget.layout(ui_manager, parent, panel, z_order)

    def layout_content(self, ui_manager, parent, panel, z_order):
        self.widget.layout_content(ui_manager, parent, panel, z_order)


NeedsLayout = Flag('NeedsLayout')


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

