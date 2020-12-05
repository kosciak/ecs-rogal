import numpy as np

from ecs import Component


class BlocksMovement(Component):
    __slots__ = ()

class BlockVisibility(Component):
    __slots__ = ()

class Hidden(Component):
    __slots__ = ()

class Player(Component):
    __slots__ = ()


class Monster(Component):
    __slots__ = ()


class Item(Component):
    __slots__ = ()

class CursedItem(Component):
    __slots__ = ()

class UnidentifiedItem(Component):
    __slots__ = ()


class Name(Component):
    __slots__ = ('name', )

    def __init__(self, name):
        self.name = name


class Position(Component):
    __slots__ = ('position', )
    _attrs_ = ('x', 'y', )

    def __init__(self, position):
        self.position = position

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

# TODO: Position on different level/depth/map, not currentl one


class Renderable(Component):
    __slots__ = ('character', 'fg_color', 'bg_color', 'render_order', )

    def __init__(self, character, fg_color, *, bg_color=None, render_order):
        self.character = character
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.render_order = render_order


class Viewshed(Component):
    __slots__ = ('view_range', 'visible_tiles', 'needs_update', )
    _attrs_ = ('view_range', )

    def __init__(self, view_range):
        self.view_range = view_range
        self.visible_tiles = set()
        self.needs_update = True

    def update(self, fov):
        self.needs_update = True
        self.visible_tiles = np.transpose(fov.nonzero())


class Pool:

    def __init__(self, value, max_value):
        self._value = 0
        self.max_value = max_value
        self.value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = max(0, min(value, self.max_value))


# Action intentions

class WantsToMove(Component):
    __slots__ = ()

class WantsToMelee(Component):
    __slots__ = ()
class WantsToShoot(Component):
    __slots__ = ()

class WantsToDrink(Component):
    __slots__ = ()
class WantsToRead(Component):
    __slots__ = ()
class WantsToUseItem(Component):
    # TODO: !!!
    def __init__(self, item, target=None):
        pass

class WantsToPickupItem(Component):
    __slots__ = ()
class WantsToDropItem(Component):
    __slots__ = ()
class WantsToEquipItem(Component):
    __slots__ = ()
class WantsToUnEquipItem(Component):
    __slots__ = ()

