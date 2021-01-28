import functools
import time

import numpy as np

from .ecs import Component, FloatComponent
from .ecs import Flag, IntFlag, Int, Counter, String, EntityRef, component_type
from .ecs import EntitiesSet
from . import flags
from .geometry import Direction, Position, WithPositionMixin
from .renderable import RenderOrder
from . import terrain


# Flags

BlocksMovement = IntFlag('BlocksMovement', flags.Flag.BLOCKS_MOVEMENT)
BlocksMovementChanged = Flag('BlocksMovementChanged')

BlocksVision = IntFlag('BlocksVision', flags.Flag.BLOCKS_VISION)
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

class Particle(FloatComponent):
    __slots__ = ()

    def __new__(cls, value):
        return super().__new__(cls, time.time()+value)

# TODO: RealTimeParticles and TickBasedParticles based on ClockTicks like WaitsForAction


# Common components

Name = String('Name')

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
    params = ('tile_visible', 'tile_revealed', 'render_order', )

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
    __slots__ = ('view_range', 'fov', '_positions', 'entities', 'needs_update', )
    params = ('view_range', )

    def __init__(self, view_range):
        self.view_range = view_range
        self.fov = None
        self._positions = set()
        self.entities = set()
        self.needs_update = True

    def invalidate(self):
        self.fov = None
        self._positions.clear()
        self.needs_update = True

    def update(self, fov):
        self.fov = fov
        self.needs_update = False

    @property
    def positions(self):
        if self.fov is not None and \
           not self._positions:
            self._positions.update(
                Position(x, y) for x, y in np.transpose(self.fov.nonzero())
            )
        return self._positions


class LevelMemory(Component):
    __slots__ = ('shared', 'revealed', )
    params = ('shared', )

    _SHARED = {}

    def __new__(cls, shared=False):
        memory = shared and cls._SHARED.get(shared)
        if not memory:
            memory = super(Component, cls).__new__(cls)
            memory.shared = shared
            memory.revealed = {}
            cls._SHARED[shared] = memory
        return memory

    def update(self, level_id, fov):
        if not level_id in self.revealed:
            self.revealed[level_id] = fov == True
        else:
            self.revealed[level_id] |= fov


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
    __slots__ = ('base', 'modifier')
    params = ('base', 'modifier')

    def __init__(self, base, modifier=None):
        self.base = base
        self.modifier = modifier or 0

    @property
    def total(self):
        return self.base + self.modifier

    def __int__(self):
        return self.total

Attribute = component_type(AttributeComponent)

Attack = Attribute('Attack')
Defence = Attribute('Defence')
MovementSpeed = Attribute('MovementSpeed')


# Actions queue

ActsNow = Flag('ActsNow')

WaitsForAction = Counter('WaitsForAction')


# Action intentions

class WantsToMove(Component):
    __slots__ = ('direction', )

    """Move one step in given Direction."""

    def __init__(self, direction):
        if isinstance(direction, str):
            direction = getattr(Direction, direction)
        self.direction = direction

    @property
    def dx(self):
        return self.direction.dx

    @property
    def dy(self):
        return self.direction.dy

    def serialize(self):
        return self.direction.name

    def __str__(self):
        return self.direction.name

    def __repr__(self):
        return f'<{self.name}={self.direction.name}>'

HasMoved = Flag('HasMoved')


WantsToMelee = EntityRef('WantsToMelee')

WantsToOperate = EntityRef('WantsToOperate')


# TODO: Rework as EntityRef?

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
