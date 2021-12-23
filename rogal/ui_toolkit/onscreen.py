import logging

import numpy as np

from ..ecs.core import Entity


log = logging.getLogger(__name__)


class OnScreenManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self._positions = None
        # TODO: consider adding pixel_positions ??

    @property
    def positions(self):
        if self._positions is None:
            root_panel = self.ecs.resources.root_panel
            self._positions = np.zeros(root_panel.size, dtype=(np.void, 16), order="C")
        return self._positions

    def clear(self):
        self._positions = None

    def update_positions(self, entity, panel):
        self.positions[panel.x : panel.x2, panel.y : panel.y2] = entity.bytes

    def get(self, position):
        # NOTE: On terminal position might be outside root console!
        max_x, max_y = self.positions.shape
        if position.x >= max_x or position.y >= max_y:
            return

        return Entity(self.positions[position].tobytes())

