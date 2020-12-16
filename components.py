import numpy as np

from ecs import Component, Flag, SingleValue


BlocksMovement = Flag('BlocksMovement')

BlockVisibility = Flag('BlockVisibility')

Hidden = Flag('Hidden')

Player = Flag('Player')

Monster = Flag('Monster')

Item = Flag('Item')

CursedItem = Flag('CursedItem')

UnidentifiedItem = Flag('UnidentifiedItem')


Name = SingleValue('Name')


# TODO: Use both Position and Location (for entities not on current map/level)?
Position = SingleValue('Position')

class Location(Component):
    __slots__ = ('map_id', 'position', )

    def __init__(self, map_id, position):
        self.map_id = map_id
        self.position = position


class Renderable(Component):
    __slots__ = ('tile', 'render_order', )

    def __init__(self, tile, render_order):
        self.tile = tile
        self.render_order = render_order


class Viewshed(Component):
    __slots__ = ('view_range', 'visible_tiles', 'needs_update', )
    params = ('view_range', )

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
# TODO: Rework as SingleValue?

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

