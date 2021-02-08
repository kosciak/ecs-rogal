import collections
import logging
import time

import numpy as np

import tcod

from . import components
from .ecs import System, EntitiesSet
from .ecs.run_state import RunState

from .utils import perf


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


"""Systems running ecs."""


class LevelsSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs, level_generator):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial
        self.level_generator = level_generator

    def run(self):
        wants_to_change_level = self.ecs.manage(components.WantsToChangeLevel)
        levels = self.ecs.manage(components.Level)
        locations = self.ecs.manage(components.Location)
        has_moved = self.ecs.manage(components.HasMoved)

        for entity, level_id in wants_to_change_level:
            level_id = level_id or int(self.level_generator.init_level())
            populated = level_id in levels
            level_id, starting_position = self.level_generator.generate(
                level_id=level_id, populated=populated)
            prev_location = locations.get(entity)
            if prev_location:
                self.spatial.remove_entity(entity, prev_location)
            location = locations.insert(entity, level_id, starting_position)
            self.spatial.add_entity(entity, location)
            has_moved.insert(entity)

        wants_to_change_level.clear()


class ActionsQueueSystem(System):

    INCLUDE_STATES = {
        RunState.TICKING,
    }

    def update_acts_now(self):
        acts_now = self.ecs.manage(components.ActsNow)
        waiting_queue = self.ecs.manage(components.WaitsForAction)

        # Clear previous ActsNow flags
        acts_now.clear()

        for entity, waits in waiting_queue:
            # Decrease wait time
            waits -= 1
            if waits <= 0:
                # No more waiting, time for some action!
                acts_now.insert(entity)

    def update_run_state(self):
        acts_now = self.ecs.manage(components.ActsNow)
        if acts_now:
            self.ecs.run_state = RunState.WAITING_FOR_ACTIONS

    def run(self):
        self.update_acts_now()


class TakeActionsSystem(System):

    INCLUDE_STATES = {
        RunState.WAITING_FOR_ACTIONS,
    }

    def update_run_state(self):
        events_handlers = self.ecs.manage(components.EventsHandler)
        acts_now = self.ecs.manage(components.ActsNow)
        if events_handlers:
            self.ecs.run_state = RunState.WAITING_FOR_INPUT
        if not acts_now:
            self.ecs.run_state = RunState.PERFOM_ACTIONS

    def run(self):
        acts_now = self.ecs.manage(components.ActsNow)
        if not acts_now:
            return
        actions_handlers = self.ecs.manage(components.Actor)

        for actor, handler in self.ecs.join(acts_now.entities, actions_handlers):
            if not handler.take_action(actor):
                break


class EventsHandlersSystem(System):

    WAIT = 1./60
    REPEAT_RATE = 1./6

    INCLUDE_STATES = {
        RunState.WAITING_FOR_INPUT,
    }

    def __init__(self, ecs, repeat_rate=REPEAT_RATE):
        super().__init__(ecs)
        self.wrapper = self.ecs.resources.wrapper
        self.wait = self.WAIT
        self.repeat_rate = repeat_rate
        self._prev_times = {}

    def is_valid(self, event):
        if event.type is None:
            return False

        now = time.time()
        prev_time = self._prev_times.get(event.type)
        # if event.repeat:
        if getattr(event, 'repeat', False):
            if prev_time and now - prev_time < self.repeat_rate:
                return False

        self._prev_times[event.type] = now
        return True

    def update_run_state(self):
        events_handlers = self.ecs.manage(components.EventsHandler)
        acts_now = self.ecs.manage(components.ActsNow)
        if acts_now and events_handlers:
            self.ecs.run_state = RunState.WAITING_FOR_INPUT
        elif acts_now:
            self.ecs.run_state = RunState.WAITING_FOR_ACTIONS
        else:
            self.ecs.run_state = RunState.PERFOM_ACTIONS

    def run(self):
        acts_now = self.ecs.manage(components.ActsNow)
        if not acts_now:
            return
        events_handlers = self.ecs.manage(components.EventsHandler)
        if not events_handlers:
            return

        # Get valid events and pass them to all entities with EventsHandlers
        # NOTE: It is NOT checked if entity has ActsNow flag, as EventsHandler can be attached
        #       to any entity, not only to actors (for example to GUI elements)
        #       BUT there must be some ActsNow actor for system to be running!
        for event in self.wrapper.events(self.wait):
            if event and self.is_valid(event):
                for entity, handler in list(events_handlers):
                    handler.handle(event, entity)
            return


class QuitSystem(System):

    INCLUDE_STATES = {
        RunState.WAITING_FOR_ACTIONS,
        RunState.WAITING_FOR_INPUT,
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        wants_to_quit = self.ecs.manage(components.WantsToQuit)
        if wants_to_quit:
            log.warning('Quitting...')
            raise SystemExit()


class RestingSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        players = self.ecs.manage(components.Player)
        wants_to_rest = self.ecs.manage(components.WantsToRest)

        for entity in wants_to_rest.entities:
            if entity in players:
                msg_log.info('Resting...')

        wants_to_rest.clear()


class MovementSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def apply_move(self):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        locations = self.ecs.manage(components.Location)
        movement_directions = self.ecs.manage(components.WantsToMove)
        has_moved = self.ecs.manage(components.HasMoved)

        for entity, location, direction in self.ecs.join(self.ecs.entities, locations, movement_directions):
            if entity in players:
                msg_log.info(f'{names.get(entity)} MOVE: {direction}')

            # Update position
            from_position = location.position
            location.position = location.position.move(direction)
            self.spatial.update_entity(entity, location, from_position)
            has_moved.insert(entity)

        # Clear processed movement intents
        movement_directions.clear()

    def run(self):
        self.apply_move()


class MeleeCombatSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spawner = self.ecs.resources.spawner

    def run(self):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        melee_targets = self.ecs.manage(components.WantsToMelee)
        locations = self.ecs.manage(components.Location)

        for entity, target in melee_targets:
            if entity in players or target in players:
                msg_log.info(f'{names.get(entity)} ATTACK: {names.get(target)}')
            # TODO: Do some damage!
            location = locations.get(target)
            self.spawner.create_and_spawn('particles.HIT_PARTICLE', location.level_id, location.position)

        # Clear processed targets
        melee_targets.clear()


class OperateSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
    }

    def run(self):
        players = self.ecs.manage(components.Player)
        names = self.ecs.manage(components.Name)
        operate_targets = self.ecs.manage(components.WantsToOperate)
        operations = self.ecs.manage(components.OnOperate)
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)

        for entity, target in operate_targets:
            if entity in players:
                msg_log.info(f'{names.get(entity)} OPERATE: {names.get(target)}')
            operation = operations.get(target)
            for component in operation.insert:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                if component == components.BlocksMovement:
                    blocks_movement_changes.insert(target)
                manager = self.ecs.manage(component)
                manager.insert(target, component=component)
            for component in operation.remove:
                if component == components.BlocksVision:
                    blocks_vision_changes.insert(target)
                if component == components.BlocksMovement:
                    blocks_movement_changes.insert(target)
                manager = self.ecs.manage(component)
                manager.remove(target)

        # Clear processed targets
        operate_targets.clear()


class VisibilitySystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.WAITING_FOR_INPUT,
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    # TODO: rename this method!
    def invalidate_blocks_vision_changed_viewsheds(self):
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        if not blocks_vision_changes:
            return
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)

        # Invalidate Viewshed of all entities with target in viewshed
        positions_per_level = collections.defaultdict(set)
        for entity, location in self.ecs.join(blocks_vision_changes.entities, locations):
            positions_per_level[location.level_id].add(location.position)

        if not positions_per_level:
            return

        viewsheds = self.ecs.manage(components.Viewshed)
        for viewshed, location in self.ecs.join(viewsheds, locations):
            if viewshed.positions & positions_per_level[location.level_id]:
                viewshed.invalidate()

    def invalidate_has_moved_viewsheds(self):
        # Invalidate Viewshed after moving
        has_moved = self.ecs.manage(components.HasMoved)
        if not has_moved:
            return
        viewsheds = self.ecs.manage(components.Viewshed)

        for entity, viewshed in self.ecs.join(has_moved.entities, viewsheds):
            viewshed.invalidate()

    def reveal_levels(self):
        wants_to_reveal = self.ecs.manage(components.WantsToRevealLevel)
        if not wants_to_reveal:
            return
        level_memories = self.ecs.manage(components.LevelMemory)
        locations = self.ecs.manage(components.Location)

        for entity, memory, location in self.ecs.join(wants_to_reveal.entities, level_memories, locations):
            memory.update(location.level_id, self.spatial.revealable(location.level_id))
            msg_log.warning('Level revealed!')

        wants_to_reveal.clear()

    def update_viewsheds(self):
        players = self.ecs.manage(components.Player)
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)
        level_memories = self.ecs.manage(components.LevelMemory)

        #  Update Viesheds that needs update
        for entity, location, viewshed in self.ecs.join(self.ecs.entities, locations, viewsheds):
            if not viewshed.needs_update:
                # No need to recalculate
                continue

            # TODO: Move to separate module?
            fov = tcod.map.compute_fov(
                transparency=self.spatial.transparent(location.level_id),
                pov=location.position,
                radius=viewshed.view_range,
                light_walls=True,
                # algorithm=tcod.FOV_BASIC,
                # algorithm=tcod.FOV_SHADOW,
                # algorithm=tcod.FOV_DIAMOND,
                algorithm=tcod.FOV_RESTRICTIVE,
                # algorithm=tcod.FOV_PERMISSIVE(1),
                # algorithm=tcod.FOV_PERMISSIVE(8),
                # algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST,
            )

            viewshed.update(fov)

            memory = level_memories.get(entity)
            if memory:
                memory.update(location.level_id, fov)

    def spotted_alert(self):
        # NOTE: It's SLOOOOOOOOOOOW!!! Use only for player for now, needs rewrite anyway
        players = self.ecs.manage(components.Player)
        locations = self.ecs.manage(components.Location)
        viewsheds = self.ecs.manage(components.Viewshed)

        # for entity, location, viewshed in self.ecs.join(self.ecs.entities, locations, viewsheds):
        for entity, location, viewshed in self.ecs.join(players.entities, locations, viewsheds):

            # This! This is the part that is very costly
            visible_entities = EntitiesSet()
            visible_entities.update(*[entities for entities in 
                                      [self.spatial.get_entities(location, position) 
                                       for position in viewshed.positions]])
            spotted_entities = EntitiesSet(visible_entities - viewshed.entities)
            viewshed.entities = visible_entities

            if spotted_entities and entity in players:
                names = self.ecs.manage(components.Name)
                monsters = self.ecs.manage(components.Monster)
                spotted_targets = []
                for target, is_monster, name in self.ecs.join(spotted_entities, monsters, names):
                    spotted_targets.append(name)
                if spotted_targets:
                    names = ', '.join(spotted_targets)
                    msg_log.info(f'You see: {names}')

    def run(self):
        if self.ecs.run_state == RunState.WAITING_FOR_INPUT:
            self.reveal_levels()
            return
        self.invalidate_blocks_vision_changed_viewsheds()
        self.invalidate_has_moved_viewsheds()
        self.update_viewsheds()
        with perf.Perf(self.spotted_alert):
            self.spotted_alert()


class IndexingSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def calculate_spatial(self):
        if not self.spatial._entities:
            self.spatial.calculate_entities()

    def update_flags(self):
        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        locations = self.ecs.manage(components.Location)

        for entity, location in self.ecs.join(blocks_vision_changes.entities, locations):
            self.spatial.update_entity(entity, location)

        for entity, location in self.ecs.join(blocks_movement_changes.entities, locations):
            self.spatial.update_entity(entity, location)

    def run(self):
        self.calculate_spatial()
        self.update_flags()


class ActionsPerformedSystem(System):

    INCLUDE_STATES = {
        RunState.PRE_RUN,
        RunState.PERFOM_ACTIONS,
    }

    def update_run_state(self):
        self.ecs.run_state = RunState.TICKING

    def run(self):
        has_moved = self.ecs.manage(components.HasMoved)
        has_moved.clear()

        blocks_vision_changes = self.ecs.manage(components.BlocksVisionChanged)
        blocks_vision_changes.clear()

        blocks_movement_changes = self.ecs.manage(components.BlocksMovementChanged)
        blocks_movement_changes.clear()


class AnimationsSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
        RunState.ANIMATIONS,
    }

    def update_run_state(self):
        animations = self.ecs.manage(components.Animation)
        if animations:
            self.ecs.run_state = RunState.ANIMATIONS
        else:
            self.ecs.run_state = RunState.TICKING


class TTLSystem(System):

    INCLUDE_STATES = {
        RunState.PERFOM_ACTIONS,
        RunState.ANIMATIONS,
    }

    def __init__(self, ecs):
        super().__init__(ecs)
        self.spatial = self.ecs.resources.spatial

    def run(self):
        outdated = EntitiesSet()
        ttls = self.ecs.manage(components.TTL)
        now = time.time()
        for entity, ttl in ttls:
            if ttl < now:
                outdated.add(entity)

        if not outdated:
            return

        locations = self.ecs.manage(components.Location)
        for entity, location in self.ecs.join(outdated, locations):
            self.spatial.remove_entity(entity, location)
        self.ecs.remove(*outdated)

