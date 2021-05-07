import logging
import time
import sys

from .. import ansi
from ..console import ConsoleRGB

from .core import IOWrapper


log = logging.getLogger(__name__)


class ANSIWrapper(IOWrapper):

    # NOTE: Just proof-of-concept of ansi based Console rendering

    CONSOLE_CLS = ConsoleRGB

    @property
    def is_initialized(self):
        return True

    def initialize(self):
        return

    def events_gen(self, wait=None):
        """Yield events."""
        if not self.is_initialized:
            self.initialize()
        yield from ()

    def create_console(self, size=None):
        return super().create_console(self.console_size)

    def flush(self, panel):
        sys.stdout.write(ansi.erase_display(1))
        sys.stdout.write(ansi.cursor_position(1,1))
        ansi.show_rgb_console(panel.console)
        # sys.stdout.flush()

