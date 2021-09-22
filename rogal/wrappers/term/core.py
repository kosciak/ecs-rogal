import logging

from ...term.terminal import Terminal

from ..core import IOWrapper

from .input import TermInputWrapper
from .output import TermOutputWrapper


log = logging.getLogger(__name__)


class TermWrapper(IOWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._term = None

    @property
    def is_initialized(self):
        return self._term is not None

    def initialize_term(self):
        term = Terminal()
        # term.cbreak()
        term.raw()
        term.fullscreen(True)
        term.keypad(True)
        # term.meta(True) # ???
        term.report_focus(True)
        term.bracketed_paste(True)
        term.hide_cursor()
        return term

    @property
    def term(self):
        return self._term

    def initialize(self):
        self._term = self.initialize_term()

        if self.title:
            self.term.set_title(self.title)

        self._input = TermInputWrapper(self.term)
        self._output = TermOutputWrapper(self.term)

    def terminate(self):
        self.term.close()
        self._term = None

