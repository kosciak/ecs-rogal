import functools
import time

import numpy as np

from .ecs import Component, ConstantValueComponent, SingleValueComponent
from .ecs import Flag, Constant, Counter, component_type
from .geometry import Position, WithPositionMixin
from .renderable import RenderOrder
from . import terrain


# Flags

BlocksMovement = Flag('BlocksMovement')

BlocksVision = Flag('BlocksVision')

BlocksVisionChanged = Flag('BlocksVisionChanged')


# Entity type

class Terrain(Component):
    __slots__ = ('type', 'material')

    def __init__(self, type, material=None):
        if isinstance(type, str):
            type = getattr(terrain.Type, type)
        self.type = type
        if isinstance(material, str):
            material = getattr(terrain.Material, material)
        self.material = material


Foliage = Flag('Foliage')

Prop = Flag('Prop')

Item = Flag('Item')

Player = Flag('Player')

Monster = Flag('Monster')


class OnOperate(Component):
    __slots__ = ('insert', 'remove')

    def __init__(self, insert=None, remove=''):
        self.insert = insert or []
        self.remove = remove or []


Animation = Flag('Animation')

class Particle(ConstantValueComponent, SingleValueComponent):
    __slots__ = ()

    def __init__(self, value):
        super().__init__(time.time()+value)

# TODO: RealTimeParticles and TickBasedParticles based on ClockTicks like WaitsForAction


# Common components

Name = Constant('Name')

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
        if isinstance(render_order, str):
            render_order = getattr(RenderOrder, render_order)
        self.render_order = render_order

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


class PoolComponent(Component):
    __slots__ = ('_value', 'max_value', )
    params = ('value', 'max_value', )

    def __init__(self, value, max_value=None):
        self._value = 0
        value = int(value)
        max_value = max_value and int(max_value)
        self.max_value = max_value or value
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = max(0, min(value, self.max_value))

Pool = component_type(PoolComponent)

HitPoints = Pool('HitPoints')


class AttributeComponent(Component):
    __slots__ = ('base', 'bonus')
    params = ('base', 'bonus')

    def __init__(self, base, bonus=None):
        self.base = base
        self.bonus = bonus or 0

    @property
    def total(self):
        return self.base + self.bonus

Attribute = component_type(AttributeComponent)

Attack = Attribute('Attack')
Defence = Attribute('Defence')


# Actions queue

ActsNow = Flag('ActsNow')

WaitsForAction = Counter('WaitsForAction')


# Action intentions

class WantsToMove(ConstantValueComponent, SingleValueComponent):

    """Move one step in given Direction."""

    def serialize(self):
        return self.value.name

HasMoved = Flag('HasMoved')


WantsToMelee = Constant('WantsToMelee')

WantsToOperate = Constant('WantsToOperate')


# TODO: Rework as Constant?

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



Hidden = Flag('Hidden')

CursedItem = Flag('CursedItem')

UnidentifiedItem = Flag('UnidentifiedItem')
