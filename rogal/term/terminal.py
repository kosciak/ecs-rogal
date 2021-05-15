import codecs
import curses
import functools
import locale
import os
import select
import signal
import sys
import termios
import tty

from ..geometry import Size, WithSizeMixin

from .capabilities import Capability
from .terminfo import Terminfo
from .escape_seq import Mode
from .keys import SequenceParser
from . import term_seq


UNKNOWN_TERM = 'dumb'
TRUECOLOR_TERM = {'truecolor', '24bit', }


class Terminal(WithSizeMixin):

    def __init__(self, in_stream=None, out_stream=None):
        self._term = None
        self._colors_num = None

        self.input = in_stream or sys.__stdin__
        self._in_fd = self.input.fileno()
        self.output = out_stream or sys.__stdout__
        self._out_fd = self.output.fileno()

        self._encoding = locale.getpreferredencoding() or 'utf-8'
        self._char_decoder = codecs.getincrementaldecoder(self._encoding)()
        self._sequence_parser = None

        self._tty_state = self._get_tty_state(self._in_fd)
        self._exit_modes = {}

        self._size = None

        self._terminfo = None

        # TODO: add some on_resize hook registration?
        signal.signal(signal.SIGWINCH, self._resize_handler)

    def close(self):
        for exit_seq in self._exit_modes.values():
            self.output.write(exit_seq)
        self.output.flush()
        self._set_tty_state(self._in_fd, self._tty_state)

    # Properties

    @property
    def term(self):
        if self._term is None:
            self._term = os.environ.get('TERM', UNKNOWN_TERM) or UNKNOWN_TERM
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

    def _resize_handler(self, signal_no, frame):
        self._size = None

    @property
    def terminfo(self):
        if self._terminfo is None:
            self._terminfo = Terminfo(self.term, self._out_fd)
        return self._terminfo

    @property
    def sequence_parser(self):
        if self._sequence_parser is None:
            self._sequence_parser = SequenceParser(self._terminfo, self._encoding)
        return self._sequence_parser

    # Terminfo / capabilities

    # TODO: Consider renaming to tparm, and tput() does write and flush
    @functools.lru_cache(maxsize=1024)
    def tput(self, cap_name, *params):
        capability = self.terminfo.get(cap_name)
        if not capability:
            return None
        sequence = self.terminfo.tparm(capability, *params)
        return sequence.decode(self._encoding)

    # Low level TTY stuff 

    def _get_tty_state(self, fd):
        return termios.tcgetattr(fd)

    def _set_tty_state(self, fd, tty_state):
        termios.tcsetattr(fd, termios.TCSAFLUSH, tty_state)

    def cbreak(self):
        tty.setcbreak(self._in_fd, termios.TCSANOW)

    def raw(self):
        tty.setraw(self._in_fd, termios.TCSANOW)

    # Input handling

    def is_readable(self, timeout=None):
        if timeout is None:
            readable, _, _ = select.select([self._in_fd, ], [], [])
        else:
            readable, _, _ = select.select([self._in_fd, ], [], [], timeout)
        return self._in_fd in readable

    def read_byte(self):
        byte = os.read(self._in_fd, 1)
        return byte

    def read_bytes(self):
        yield self.read_byte()
        while self.is_readable(timeout=False):
            yield self.read_byte()

    def read_char(self):
        for byte in self.read_bytes():
            char = self._char_decoder.decode(byte)
            if char:
                return char
        return None

    def read_chars(self):
        for byte in self.read_bytes():
            char = self._char_decoder.decode(byte)
            if char:
                yield char

    def read_keys(self):
        input_sequence = ''.join(self.read_chars())
        for sequence in self.sequence_parser.parse(input_sequence):
            yield sequence

    # Output handling

    def write(self, text):
        self.output.write(text)

    def flush(self):
        self.output.flush()

    # Modes manipulation

    def enter_mode(self, mode, enter_seq, exit_seq):
        if exit_seq:
            self._exit_modes[mode] = exit_seq
        if enter_seq:
            self.output.write(enter_seq)
            self.output.flush()

    def exit_mode(self, mode, exit_seq):
        self._exit_modes.pop(mode, None)
        if exit_seq:
            self.output.write(exit_seq)
            self.output.flush()

    def change_mode(self, mode, enable, enter_seq, exit_seq):
        if enable:
            self.enter_mode(mode, enter_seq, exit_seq)
        else:
            self.exit_mode(mode, exit_seq)

    def fullscreen(self, enable=True):
        mode = 'fullscreen' # smcup / rmcup
        enter_seq = self.tput(Capability.enter_ca_mode)
        exit_seq = self.tput(Capability.exit_ca_mode)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def keypad(self, enable=True):
        mode = 'keypad' # smkx / rmkx
        enter_seq = self.tput(Capability.keypad_xmit)
        exit_seq = self.tput(Capability.keypad_local)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def meta(self, enable=True):
        mode = 'meta' # smm / rmm
        enter_seq = self.tput(Capability.meta_on)
        exit_seq = self.tput(Capability.meta_off)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def hide_cursor(self, enable=True):
        mode = 'hide_cursor' # civis / cnorm
        enter_seq = self.tput(Capability.cursor_invisible)
        exit_seq = self.tput(Capability.cursor_normal)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def mouse_tracking(self, enable=True):
        mode = 'mouse_tracking'
        # enter_seq = self.tput(Capability.xterm_mouse_mode, 1)
        # exit_seq = self.tput(Capability.xterm_mouse_mode, 0)

        mouse_modes = [
            Mode.VT200_MOUSE,
            Mode.BTN_EVENT_MOUSE,
            Mode.ANY_EVENT_MOUSE,
            Mode.URXVT_EXT_MODE_MOUSE,
            Mode.SGR_EXT_MODE_MOUSE,
        ]

        enter_seq = ''.join(term_seq.set_private_mode(mouse_mode) for mouse_mode in mouse_modes)
        exit_seq = ''.join(term_seq.reset_private_mode(mouse_mode) for mouse_mode in mouse_modes)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def report_focus(self, enable=True):
        mode = 'report_focus'
        enter_seq = term_seq.set_private_mode(Mode.FOCUS_EVENT_MOUSE)
        exit_seq = term_seq.reset_private_mode(Mode.FOCUS_EVENT_MOUSE)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def bracketed_paste(self, enable=True):
        mode = 'bracketed_paste'
        enter_seq = term_seq.set_private_mode(Mode.BRACKETED_PASTE)
        exit_seq = term_seq.reset_private_mode(Mode.BRACKETED_PASTE)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def save_title(self):
        self.output.write(term_seq.save_title())
        self.output.flush()

    def set_title(self, title):
        self._exit_modes['set_title'] = term_seq.restore_title()

        # TODO: first check if status line is available? self.terminfo.get(Capability.has_status_line)
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

    def request_cursor(self):
        # self.output.write(term_seq.csi(term_seq.CSI.CPR))
        self.output.write(self.tput(Capability.cursor_request)) # Answer with Capability.u6 format
        self.output.flush()
        # TODO: Read cursor position from input

