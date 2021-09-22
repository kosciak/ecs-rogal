import codecs
import collections
import curses
import functools
import locale
import logging
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
from .input import SequenceParser
from . import ansi
from . import term_seq


log = logging.getLogger(__name__)


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

        self._terminfo = None

        self._encoding = locale.getpreferredencoding() or 'utf-8'
        self._char_decoder = codecs.getincrementaldecoder(self._encoding)()
        self._sequence_parser = None
        self._sequence_buffer = collections.deque()
        self._unget_buffer = collections.deque()

        self._tty_state = self._get_tty_state(self._in_fd)
        self._exit_modes = {}

        self._size = None

        # TODO: add some on_resize hook registration?
        signal.signal(signal.SIGWINCH, self._resize_handler)

    def close(self):
        for exit_seq in self._exit_modes.values():
            self.output.write(exit_seq)
        self.output.flush()
        self._set_tty_state(self._in_fd, self._tty_state)

    def dump_term_info(self):
        fn = f'{self.term}.info.txt'
        with open(fn, 'w') as f:
            f.write(f'TERM={self.term}\n')
            f.write(f'COLORTERM={os.environ.get("COLORTERM")}\n')
            f.write(f'COLORS_NUM={self.colors_num}\n')

            supported_capabilities = self.terminfo.list_all()
            for capability in sorted(supported_capabilities.keys()):
                f.write(f'{capability}={supported_capabilities[capability]}\n')

    # Properties

    @property
    def term(self):
        if self._term is None:
            self._term = os.environ.get('TERM', UNKNOWN_TERM) or UNKNOWN_TERM
        return self._term

    @property
    def colors_num(self):
        if self._colors_num is None:
            if os.environ.get('COLORTERM') in TRUECOLOR_TERM:
                self._colors_num = 256*256*256
            else:
                self._colors_num = self.terminfo.get_num('colors')
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
            self._sequence_parser = SequenceParser(self.terminfo, self._encoding)
        return self._sequence_parser

    # Terminfo / capabilities

    @functools.lru_cache(maxsize=1024)
    def tput(self, cap_name, *params):
        capability = self.terminfo.get(cap_name)
        if not capability:
            return '' # Capability not supported
        sequence = self.terminfo.tparm(capability, *params)
        return sequence.decode(self._encoding)

    # Low level TTY state and mode

    def _get_tty_state(self, fd):
        return termios.tcgetattr(fd)

    def _set_tty_state(self, fd, tty_state):
        termios.tcsetattr(fd, termios.TCSAFLUSH, tty_state)

    def cbreak(self):
        tty.setcbreak(self._in_fd, termios.TCSANOW)

    def raw(self):
        tty.setraw(self._in_fd, termios.TCSANOW)

    # Input handling - from very low-level (reading single bytes) to parsed, and buffered sequences

    def is_readable(self, timeout=None):
        if timeout is None:
            readable, _, _ = select.select([self._in_fd, ], [], [])
        else:
            readable, _, _ = select.select([self._in_fd, ], [], [], timeout or 0)
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

    def read_sequences(self):
        input_sequence = ''.join(self.read_chars())
        for sequence in self.sequence_parser.parse(input_sequence):
            yield sequence

    def get_sequences(self, timeout=None):
        self._sequence_buffer.extendleft(self._unget_buffer)
        self._unget_buffer.clear()

        while self._sequence_buffer:
            yield self._sequence_buffer.popleft()

        if self.is_readable(timeout):
            self._sequence_buffer.extend(self.read_sequences())

        while self._sequence_buffer:
            yield self._sequence_buffer.popleft()

    def get_sequence(self, timeout=None):
        for sequence in self.get_sequences(timeout):
            return sequence

    def unget_sequence(self, sequence):
        self._unget_buffer.append(sequence)

    # Output handling

    def write(self, text):
        self.output.write(text)

    def flush(self, text=None):
        if text:
            self.output.write(text)
        self.output.flush()

    # Modes manipulation

    def enter_mode(self, mode, enter_seq, exit_seq):
        if exit_seq:
            self._exit_modes[mode] = exit_seq
        if enter_seq:
            self.flush(enter_seq)

    def exit_mode(self, mode, exit_seq):
        self._exit_modes.pop(mode, None)
        if exit_seq:
            self.flush(exit_seq)

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
            # Mode.X10_MOUSE,
            Mode.VT200_MOUSE,
            Mode.BTN_EVENT_MOUSE,
            Mode.ANY_EVENT_MOUSE,

            # NOTE: Do NOT use Mode.EXT_MOUSE_REPORT
            Mode.URXVT_EXT_MODE_MOUSE,
            Mode.SGR_EXT_MODE_MOUSE,
        ]

        enter_seq = ''.join(term_seq.set_private_mode(mouse_mode) for mouse_mode in mouse_modes)
        exit_seq = ''.join(term_seq.reset_private_mode(mouse_mode) for mouse_mode in mouse_modes)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def report_focus(self, enable=True):
        mode = 'report_focus'
        enter_seq = term_seq.set_private_mode(Mode.FOCUS_EVENT)
        exit_seq = term_seq.reset_private_mode(Mode.FOCUS_EVENT)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def bracketed_paste(self, enable=True):
        mode = 'bracketed_paste'
        enter_seq = term_seq.set_private_mode(Mode.BRACKETED_PASTE)
        exit_seq = term_seq.reset_private_mode(Mode.BRACKETED_PASTE)
        self.change_mode(mode, enable, enter_seq, exit_seq)

    def save_title(self):
        sequence = term_seq.save_title()
        self.flush(sequence)

    def set_title(self, title):
        self._exit_modes['set_title'] = term_seq.restore_title()

        # TODO: first check if status line is available? self.terminfo.get(Capability.has_status_line)
        sequence = self.tput(Capability.TS)
        if not sequence:
            sequence = self.tput(Capability.to_status_line)
        if sequence:
            sequence += title
            sequence += self.tput(Capability.from_status_line)
        else:
            sequence = term_seq.set_title(title)
        self.flush(sequence)

    def restore_title(self):
        self.output.write(term_seq.restore_title())
        self.output.flush()

    # Cursor manipulation

    def request_cursor(self):
        # self.output.write(term_seq.csi(term_seq.CSI.CPR))
        sequence = self.tput(Capability.cursor_request)
        self.flush(sequence) # Answer with Capability.u6 format

    def cursor_position(self):
        self.request_cursor()
        # NOTE: This assumes we are in cbreak or raw TTY mode!
        while self.is_readable(None):
            # Just keep trying until cursor_report shows up
            for sequence in self.read_sequences():
                if sequence.key != Capability.cursor_report:
                    self._sequence_buffer.append(sequence)
                else:
                    return sequence.position

    def cursor_move(self, x=None, y=None):
        if x is not None and y is not None:
            sequence = self.tput(Capability.cursor_address, y, x)
        elif x is not None:
            sequence = self.tput(Capability.column_address, x)
        elif y is not None:
            sequence = self.tput(Capability.row_address, y)
        return sequence

    def cursor_up(self, y=None):
        if y == None:
            sequence = self.tput(Capability.cursor_up)
        else:
            sequence = self.tput(Capability.parm_up_cursor, y)
        return sequence

    def cursor_down(self, y=None):
        if y == None:
            sequence = self.tput(Capability.cursor_down)
        else:
            sequence = self.tput(Capability.parm_down_cursor, y)
        return sequence

    def cursor_left(self, x=None):
        if x == None:
            sequence = self.tput(Capability.cursor_left)
        else:
            sequence = self.tput(Capability.parm_left_cursor, x)
        return sequence

    def cursor_right(self, x=None):
        if x == None:
            sequence = self.tput(Capability.cursor_right)
        else:
            sequence = self.tput(Capability.parm_right_cursor, x)
        return sequence

    def cursor_home(self):
        sequence = self.tput(Capability.cursor_home)
        if not sequence:
            sequence = self.cursor_move(0, 0)
        return sequence

    # Screen

    def clear(self):
        sequence = self.tput(Capability.clear_screen)
        # if not sequence:
        #     sequence = self.cursor_home() + self.tput(Capability.clr_eos)
        return sequence

    # Colors

    def init_color(self, index, color):
        sequence = self.tput(Capability.init_color, *color.rgb)
        return sequence

    def bg_rgb(self, r, g, b):
        sequence = ansi.bg_rgb(r, g, b)
        return sequence

    def fg_rgb(self, r, g, b):
        sequence = ansi.fg_rgb(r, g, b)
        return sequence

    def fg(self, color):
        sequence = self.tput(Capability.set_a_foreground, color)
        if not sequence:
            sequence = self.tput(Capability.set_foreground, color)
        return sequence

    def bg(self, color):
        sequence = self.tput(Capability.set_a_background, color)
        if not sequence:
            sequence = self.tput(Capability.set_background, color)
        return sequence

    # SGR Attributes

    def bold(self):
        sequence = self.tput(Capability.enter_bold_mode)
        return sequence

    def dim(self):
        sequence = self.tput(Capability.enter_dim_mode)
        return sequence

    def italics(self):
        sequence = self.tput(Capability.enter_italics_mode)
        return sequence

    def strikethrough(self):
        sequence = self.tput(Capability.enter_strikethrough_mode)
        return sequence

    def standout(self):
        sequence = self.tput(Capability.enter_standout_mode)
        return sequence

    def reverse(self):
        sequence = self.tput(Capability.enter_reverse_mode)
        return sequence

    def underline(self):
        sequence = self.tput(Capability.enter_underline_mode)
        return sequence

    def invisible(self):
        sequence = self.tput(Capability.enter_secure_mode)
        return sequence

    def blink(self):
        sequence = self.tput(Capability.enter_blink_mode)
        return sequence

    # Reset colors and attributes

    def normal(self):
        sequence = self.tput(Capability.exit_attribute_mode)
        return sequence

