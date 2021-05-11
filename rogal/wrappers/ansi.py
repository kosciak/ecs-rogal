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

    def is_readable(self, wait=None):
        if wait is None or wait is True:
            readable, _, _ = select.select([self._fd, ], [], [])
        else:
            wait = wait or 0 # If wait == False - no delay
            readable, _, _ = select.select([self._fd, ], [], [], wait)
        return self._fd in readable

    def get_byte(self):
        ch = os.read(self._fd, 1)
        return ch

    def get_sequence(self):
        sequence = self.get_byte()
        while self.is_readable(wait=False):
            sequence += self.get_byte()
        return sequence

    def get_events_gen(self, wait=None):
        """Get all pending events."""
        if self.is_readable(wait):
            sequence = self.get_sequence()
            log.warning('INPUT: %s', sequence)
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
        sys.stdout.write(term.set_alternate_buffer())
        # Make numlock change keypad behaviour
        sys.stdout.write(term.set_application_keypad_mode())

        # Mouse support?
        # See: https://stackoverflow.com/questions/5966903/how-to-get-mousemove-and-mouseclick-in-bash
        # NOTE: Seems to be messing with curses mouse support...
        # sys.stdout.write('\033[?1000h')
        # sys.stdout.write('\033[?1002h')
        # sys.stdout.write('\033[?1003h')
        # sys.stdout.write('\033[?1015h')
        # sys.stdout.write('\033[?1006h')

        sys.stdout.flush()

        input_fd = sys.stdin.fileno()
        self.__tty_state = termios.tcgetattr(input_fd)
        self._input = TermInputWrapper(input_fd)

        self._is_initialized = True

    def terminate(self):
        sys.stdout.write(term.show_cursor())
        sys.stdout.write(term.reset_alternate_buffer())
        sys.stdout.write('\033[?1000l')
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

