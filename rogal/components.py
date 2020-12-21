import time

import numpy as np

from .ecs import Component, SingleValueComponent, Flag, SingleValue
from .geometry import Position, WithPositionMixin


# Flags

BlocksMovement = Flag('BlocksMovement')

BlocksVision = Flag('BlocksVision')


# Entity type

Terrain = Flag('Terrain')

Foliage = Flag('Foliage')

Prop = Flag('Prop')

Item = Flag('Item')

Player = Flag('Player')

Monster = Flag('Monster')

Actor = Flag('Actor')

class Particle(SingleValueComponent):

    def __init__(self, value):
        super().__init__(time.time()+value)


# Common components

Name = SingleValue('Name')

class Location(WithPositionMixin, Component):
    __slots__ = ('level_id', 'position', )

    def __init__(self, level_id, position):
        self.level_id = level_id
        self.position = position

    def serialize(self):
        data = dict(
            level_id=str(self.level_id),
            x=self.x, 
            y=self.y,
        )
        return data


class Renderable(Component):
    __slots__ = ('_tile', 'render_order', )
    params = ('tile', 'render_order', )

    def __init__(self, tile, render_order):
        self._tile = tile
        self.render_order = render_order

    @property
    def tile(self):
        return self._tile.tile

    @property
    def tile_visible(self):
        return self._tile.visible

    @property
    def tile_revealed(self):
        return self._tile.revealed

    def __lt__(self, other):
        return self.render_order < other.render_order

    def serialize(self):
        data = dict(
            tile=self._tile.name,
            render_order=int(self.render_order),
        )
        return data


class Viewshed(Component):
    __slots__ = ('view_range', 'visible_tiles', 'needs_update', )
    params = ('view_range', )

    def __init__(self, view_range):
        self.view_range = view_range
        self.visible_tiles = set()
        self.needs_update = True

    def invalidate(self):
        self.visible_tiles = set()
        self.needs_update = True

    def update(self, fov):
        self.needs_update = False
        self.visible_tiles = {
            Position(x, y) for x, y in np.transpose(fov.nonzero())
        }


Hidden = Flag('Hidden')

CursedItem = Flag('CursedItem')

UnidentifiedItem = Flag('UnidentifiedItem')


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

class WantsToMove(SingleValueComponent):

    """Move one step in given Direction."""

    def serialize(self):
        return self.value.name


WantsToMelee = SingleValue('WantsToMelee')


# TODO: Rework as SingleValue?

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

