import logging
import time
import sys

from .. import ansi
from ..console import RootPanel

from .core import IOWrapper


log = logging.getLogger(__name__)


class ANSIConsoleWrapper(IOWrapper):

    # NOTE: Just proof-of-concept of ansi based Console rendering

    def create_console(self, size=None):
        return super().create_console(self.console_size)

    def flush(self, console):
        if isinstance(console, RootPanel):
            console = console.console
        sys.stdout.write(ansi.erase_display(1))
        sys.stdout.write(ansi.cursor_position(1,1))
        ansi.show_console(console)
        # sys.stdout.flush()

