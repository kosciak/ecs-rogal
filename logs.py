import collections
import logging


class ColorLogger(logging.Logger):

    # TODO: override debug, warning, error, critical providing default color!

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, color=None):
        if color:
            extra = extra or {}
            extra['fg'] = color
        super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)


class HistoryHandler(logging.Handler):

    def __init__(self, capacity=1000):
        logging.Handler.__init__(self)
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
        print(record.args)
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

