import collections
import logging
import logging.config


LOGS_HISTORY = collections.deque(maxlen=1000)


DEFAULT_LEVEL_COLORS = {
    logging.DEBUG: 8, # GREY (bright black)
    logging.INFO: None, # Use default FG color
    logging.ERROR: 1, # MAROON (base red)
    logging.WARNING: 9, # RED (bright red)
    logging.CRITICAL: 11, # YELLOW (bright yellow)
}

class ColorLogger(logging.Logger):

    """Add color argument to logger methods, and store color as fg."""

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, color=None):
        # NOTE: color value might be 0, so use None for checking if set or not
        if color is None:
            color = DEFAULT_LEVEL_COLORS.get(level)
        extra = extra or {}
        extra['fg'] = color
        super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)


class HistoryHandler(logging.Handler):

    """Handler storing records history."""

    def __init__(self, capacity=1000):
        super().__init__()
        self.history = collections.deque(maxlen=capacity)

    def enqueue(self, record):
        self.history.append(record)

    def prepare(self, record):
        # The format operation gets traceback text into record.exc_text
        # (if there's exception data), and also puts the message into
        # record.message. We can then use this to replace the original
        # msg + args, as these might be unpickleable. We also zap the
        # exc_info attribute, as it's no longer needed and, if not None,
        # will typically not be pickleable.
        self.format(record)
        record.msg = record.message
        record.args = None
        record.exc_info = None
        return record

    def emit(self, record):
        try:
            self.enqueue(self.prepare(record))
        except Exception:
            self.handleError(record)


class GlobalHistoryHandler(HistoryHandler):

    """Handler storing records history in global queue."""

    def __init__(self):
        super().__init__()
        self.history = LOGS_HISTORY


class LevelFilter(object):

    """Filter allowing records only with selected levels."""

    def __init__(self, levels):
        self.allowed_levels = set(levels)

    def filter(self, record):
        return record.levelno in self.allowed_levels


CONFIG = dict(
    version = 1,
    formatters = {
        'default': {
            'format': "[%(asctime)s] %(levelname)s: %(message)s",
        },
        'verbose': {
            'format': "[%(asctime)s %(module)s:%(lineno)d] %(levelname)s: %(message)s",
        },
    },
    filters = {
        'allow_info': {
            '()': LevelFilter,
            'levels': [logging.INFO, ],
        },
        'allow_info_warning': {
            '()': LevelFilter,
            'levels': [logging.INFO, logging.WARNING, ],
        },
    },
    handlers = {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': logging.DEBUG,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'console-verbose': {
            'level': logging.DEBUG,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'history': {
            'level': logging.INFO,
            'class': 'logs.GlobalHistoryHandler',
            'filters': ['allow_info_warning'],
        }
    },
    loggers = {
        'rogal': {
            'level': logging.DEBUG,
            'handlers': ['console', 'history', ],
            'propagate': False,
        },
        '': {
            'level': logging.INFO,
            'handlers': ['console-verbose', ],
        },
    },
)


def setup():
    """Setup logging configuration."""
    logging.setLoggerClass(ColorLogger)
    logging.config.dictConfig(CONFIG)

