import curses
import functools
import os
import select
import sys
import termios
import tty

from ..geometry import Size, WithSizeMixin

from .capabilities import Capability
from .terminfo import Terminfo
from . import term_seq


TRUECOLOR_TERM = {'truecolor', '24bit', }


class Terminal(WithSizeMixin):

    def __init__(self, in_stream=None, out_stream=None):
        self._term = None
        self._colors_num = None

        self.input = in_stream or sys.__stdin__
        self._in_fd = self.input.fileno()
        self.output = out_stream or sys.__stdout__
        self._out_fd = self.output.fileno()

        self._tty_state = self._get_tty_state(self._in_fd)
        self._exit_modes = {}

        self._size = None

        self._terminfo = None

        self.save_title()

    def close(self):
        for exit in self._exit_modes.values():
            self.output.write(exit)
        self.output.flush()
        self.restore_title()
        self._set_tty_state(self._in_fd, self._tty_state)

    @property
    def term(self):
        if self._term is None:
            self._term = os.environ.get('TERM', 'dumb') or 'dumb'
        return self._term

    @property
    def colors_num(self):
        if self._colors is None:
            if os.environ.get('COLORTERM') in TRUECOLOR_TERM:
                self._colors_num = 256*256*256
            else:
                self._colors_num = self.terminfo.get_flag('colors')
        return self._colors_num

    @property
    def size(self):
        if self._size is None:
            terminal_size = os.get_terminal_size()
            self._size = Size(terminal_size.columns, terminal_size.lines)
        return self._size

    @property
    def terminfo(self):
        if self._terminfo is None:
            self._terminfo = Terminfo(self.term, self._out_fd)
        return self._terminfo

    # TODO: Consider renaming to tparm, and tput() does write and flush
    @functools.lru_cache(maxsize=1024)
    def tput(self, cap_name, *params):
        capability = self.terminfo.get(cap_name)
        if not capability:
            return None
        sequence = self.terminfo.tparm(capability, *params)
        return sequence.decode('utf-8')

    def _get_tty_state(self, fd):
        return termios.tcgetattr(fd)

    def _set_tty_state(self, fd, tty_state):
        termios.tcsetattr(fd, termios.TCSAFLUSH, tty_state)

    def cbreak(self):
        tty.setcbreak(self._in_fd, termios.TCSANOW)

    def raw(self):
        tty.setraw(self._in_fd, termios.TCSANOW)

    def is_readable(self, wait=None):
        if wait is None or wait is True:
            readable, _, _ = select.select([self._in_fd, ], [], [])
        else:
            wait = wait or 0 # If wait == False - no delay
            readable, _, _ = select.select([self._in_fd, ], [], [], wait)
        return self._in_fd in readable

    def read_byte(self):
        ch = os.read(self._in_fd, 1)
        return ch

    def write(self, text):
        self.output.write(text)

    def flush(self):
        self.output.flush()

    def enter_mode(self, mode, enter, exit):
        if exit:
            self._exit_modes[mode] = exit
        if enter:
            self.output.write(enter)
            self.output.flush()

    def exit_mode(self, mode, exit):
        self._exit_modes.pop(mode, None)
        if exit:
            self.output.write(exit)
            self.output.flush()

    def fullscreen(self, enable=True):
        mode = 'fullscreen'
        enter = self.tput(Capability.enter_ca_mode)
        exit = self.tput(Capability.exit_ca_mode)
        if enable:
            self.enter_mode(mode, enter, exit)
        else:
            self.exit_mode(mode, exit)

    def keypad(self, enable=True):
        mode = 'keypad'
        enter = self.tput(Capability.keypad_xmit)
        exit = self.tput(Capability.keypad_local)
        if enable:
            self.enter_mode(mode, enter, exit)
        else:
            self.exit_mode(mode, exit)

    def hide_cursor(self, enable=True):
        mode = 'hide_cursor'
        enter = self.tput(Capability.cursor_invisible)
        exit = self.tput(Capability.cursor_normal)
        if enable:
            self.enter_mode(mode, enter, exit)
        else:
            self.exit_mode(mode, exit)

    def mouse_tracking(self, enable=True):
        mode = 'mouse_tracking'
        enter = self.tput(Capability.XM, 1)
        exit = self.tput(Capability.XM, 0)
        # TODO: manual fallback for enter and exit! Even in Gnome-terminal only basic tracking...

        # See: https://stackoverflow.com/questions/5966903/how-to-get-mousemove-and-mouseclick-in-bash
        # NOTE: Seems to be messing with curses mouse support...
        # sys.stdout.write('\033[?1000h') # Fallback to Down+up tracking
        # sys.stdout.write('\033[?1002h') # Only dragging OR...
        # sys.stdout.write('\033[?1003h') # All motion

        # sys.stdout.write('\033[?1004h') # Focus In/Out tracking

        # sys.stdout.write('\033[?1015h')
        # sys.stdout.write('\033[?1006h')

        if enable:
            self.enter_mode(mode, enter, exit)
        else:
            self.exit_mode(mode, exit)

    def save_title(self):
        self.output.write(term_seq.save_title())
        self.output.flush()

    def set_title(self, title):
        # TODO: first check if status line is available? self.terminfo.get(Capability.hs)
        sequence = self.tput(Capability.TS)
        if not sequence:
            sequence = self.tput(Capability.to_status_line)
        if sequence:
            sequence += title
            sequence += self.tput(Capability.from_status_line)
            self.output.write(sequence)
        else:
            self.output.write(term_seq.set_title(title))
        self.output.flush()

    def restore_title(self):
        self.output.write(term_seq.restore_title())
        self.output.flush()

