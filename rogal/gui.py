import functools
import logging


log = logging.getLogger(__name__)


class Prompt:

    WIDGET_TYPE = None

    def __init__(self, ecs, context, callback, *args, **kwargs):
        self.ecs = ecs
        self.ui = self.ecs.resources.ui_manager
        self.signals = self.ecs.resources.signals_manager

        self.window = None
        self.context = context
        self.callback = functools.partial(callback, *args, **kwargs)

    def show(self):
        self.window = self.ui.create(self.WIDGET_TYPE, context=self.context)
        self.signals.on(self.window, 'close', self.on_response, False)
        self.signals.on(self.window, 'response', self.on_response)

    def close(self):
        self.ui.destroy(self.window)

    def on_response(self, entity, value):
        raise NotImplementedError()


class YesNoPrompt(Prompt):

    WIDGET_TYPE = 'YES_NO_PROMPT'

    def on_response(self, entity, value):
        if value is True:
            self.callback()
        if value is False:
            log.debug('Prompt closed...')


# TODO: Rework with signals
class TextInputPrompt(Prompt):

    WIDGET_TYPE = 'TEXT_INPUT_PROMPT'

    def on_response(self, entity, value):
        self.close()
        if value is False:
            log.debug('Prompt closed...')
        elif value is not None:
            log.warning(f'Text: {value.txt}')
            # self.callback(value.txt)


# TODO: Rework with signals
class AlphabeticSelectPrompt(Prompt):

    WIDGET_TYPE = 'ALPHABETIC_SELECT_PROMPT'

    def on_response(self, entity, value):
        self.close()
        if value is False:
            log.debug('Prompt closed...')
        elif value is not None:
            log.warning(f'Selected: {value}')
            # self.callback(value.txt)

