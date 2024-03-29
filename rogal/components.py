import functools
import time

import numpy as np

from .ecs import Component
from .ecs.components import Flag, IntFlag, Int, Counter, FloatComponent, String, EntityReference, EntitiesRefs
from .ecs.components import component_type
from . import flags
from .geometry import Direction, Position, Size, WithPositionMixin, WithVectorMixin
from .geometry.rectangle import Rectangular
from . import stats
from .tiles import RenderOrder
from . import terrain


# TODO: Signals

# OnSignal


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


class Level(Component, Rectangular):
    __slots__ = ('depth', 'terrain', )

    position = Position.ZERO

    def __init__(self, depth, terrain):
        self.depth = depth
        self.terrain = terrain

    @property
    def size(self):
        return Size(*self.terrain.shape)

    def serialize(self):
        terrain = []
        for row in self.terrain.T:
            terrain.append(','.join([f'{terrain_id:02x}' for terrain_id in row]))
        data = {
            str(self.id): dict(
                depth=self.depth,
                terrain=terrain,
            )}
        return data

    def __repr__(self):
        return f'<{self.__class__.__name__} depth={self.depth} size={self.size}>'


class OnOperate(Component):
    __slots__ = ('insert', 'remove')

    def __init__(self, insert=None, remove=''):
        self.insert = insert or []
        self.remove = remove or []


Animation = Flag('Animation')

class TTL(FloatComponent):
    __slots__ = ()

    def __new__(cls, value):
        # TODO: instead of time() use monotonic() ?
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


@functools.total_ordering
class Renderable(Component):
    # TODO: Rename to ConsoleTile ?
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


# TODO: needs_update as separate Flag
class Viewshed(Component):
    __slots__ = ('view_range', 'fov', '_positions', 'entities', 'needs_update', )
    params = ('view_range', )

    def __init__(self, view_range):
        self.view_range = view_range # TODO: Use stats Attribute so we can easily alter view_range.modifier?
        self.fov = None
        self._positions = set()
        self.entities = set() # TODO: Needs to be moved somewhere else
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


# TODO: Instead of storing bool array of revealed,
#       copy part of level's terrain?
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


Pool = component_type(Component, stats.Pool)

HitPoints = Pool('HitPoints')


Attribute = component_type(Component, stats.Attribute)

Attack = Attribute('Attack')
Defence = Attribute('Defence')
MovementSpeed = Attribute('MovementSpeed')


# Actions queue

ActsNow = Flag('ActsNow')

WaitsForAction = Counter('WaitsForAction')


class Actor(Component):
    __slots__ = ('handler', )

    def __init__(self, handler):
        self.handler = handler

    def take_action(self, entity):
        return self.handler.take_action(entity)


# Action intentions

WantsToQuit = Flag('WantsToQuit')

WantsToRevealLevel = Flag('WantsToRevealLevel')

WantsToRest = Flag('WantsToRest')


# TODO: WantsToMove: to: Location, how: MovementType
class WantsToMove(WithVectorMixin, Component):
    __slots__ = ('vector', )

    """Move one step in given Direction."""

    def __init__(self, vector):
        if isinstance(vector, str):
            vector = getattr(Direction, vector)
        self.vector = vector

    def serialize(self):
        return self.vector.name

    def __str__(self):
        return self.vector.name

    def __repr__(self):
        return f'<{self.name}={getattr(self.vector, "name", self.vector)}>'


# TODO: HasMoved: from: Location, how: ModeOfTransport/MovementType
HasMoved = Flag('HasMoved')


WantsToChangeLevel = EntityReference('WantsToChangeLevel')


WantsToMelee = EntityReference('WantsToMelee')

WantsToOperate = EntityReference('WantsToOperate')


# TODO: Rework as EntityReference?

#class WantsToShoot(Component):
#    __slots__ = ()
#
#class WantsToDrink(Component):
#    __slots__ = ()
#class WantsToRead(Component):
#    __slots__ = ()
#class WantsToUseItem(Component):
#    # TODO: !!!
#    def __init__(self, item, target=None):
#        pass
#
#class WantsToPickupItem(Component):
#    __slots__ = ()
#class WantsToDropItem(Component):
#    __slots__ = ()
#class WantsToEquipItem(Component):
#    __slots__ = ()
#class WantsToUnEquipItem(Component):
#    __slots__ = ()



# Hidden = Flag('Hidden')

# CursedItem = Flag('CursedItem')

# UnidentifiedItem = Flag('UnidentifiedItem')
