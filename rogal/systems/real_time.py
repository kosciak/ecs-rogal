import logging
import time

from .. import components
from ..ecs import System, EntitiesSet
from ..ecs.run_state import RunState

from ..utils import perf


log = logging.getLogger(__name__)


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

