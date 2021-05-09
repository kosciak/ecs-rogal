import logging
import time
import os
import sys

# NOTE: Only on *NIX!
import select
import termios
import tty

from ..console import ConsoleRGB
from ..escape_seq import ansi
from ..escape_seq import term

from .core import IOWrapper, InputWrapper


log = logging.getLogger(__name__)


class TermInputWrapper(InputWrapper):

    # NOTE: Just proof-of-concept of ansi based raw terminal input handling

    def __init__(self, input_fd):
        super().__init__()
        self._fd = input_fd
        # tty.setraw(self._fd, termios.TCSANOW)
        tty.setcbreak(self._fd, termios.TCSANOW)

    def get_events_gen(self, wait=None):
        """Get all pending events."""
        log.info('reading input...')
        readable, _, _ = select.select([self._fd, ], [], [], wait)
        if readable:
            ch = os.read(self._fd, 1)
            if ch:
                log.warning(ch)
            yield from ()


class ANSIWrapper(IOWrapper):

    # NOTE: Just proof-of-concept of ansi based Console rendering

    CONSOLE_CLS = ConsoleRGB

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_initialized = False
        self.__tty_state = None

    @property
    def is_initialized(self):
        return self._is_initialized

    def initialize(self):
        sys.stdout.write(term.hide_cursor())
        sys.stdout.flush()

        input_fd = sys.stdin.fileno()
        self.__tty_state = termios.tcgetattr(input_fd)
        self._input = TermInputWrapper(input_fd)

        self._is_initialized = True

    def terminate(self):
        sys.stdout.write(term.show_cursor())
        sys.stdout.flush()

        termios.tcsetattr(self._input._fd, termios.TCSAFLUSH, self.__tty_state)

        self._is_initialized = False

    def create_console(self, size=None):
        return super().create_console(self.console_size)

    def flush(self, panel):
        sys.stdout.write(ansi.erase_display(1))
        sys.stdout.write(ansi.cursor_position(1,1))
        ansi.show_rgb_console(panel.console)
        # sys.stdout.flush()

