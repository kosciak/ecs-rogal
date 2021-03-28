import functools
import logging


log = logging.getLogger(__name__)


class Prompt:

    WIDGET_TYPE = None

    def __init__(self, ecs, context, callback, *args, **kwargs):
        self.ecs = ecs
        self.ui_manager = self.ecs.resources.ui_manager

        self.window = None
        self.context = context
        self.callback = functools.partial(callback, *args, **kwargs)
        self.context['callback'] = self.on_event

    def show(self):
        self.window = self.ui_manager.create(self.WIDGET_TYPE, context=self.context)

    def close(self):
        self.ui_manager.destroy(self.window)

    def on_event(self, entity, value):
        raise NotImplementedError()


class YesNoPrompt(Prompt):

    WIDGET_TYPE = 'YES_NO_PROMPT'

    def on_event(self, entity, value):
        self.close()
        if value is True:
            self.callback()
        if value is False:
            log.debug('Prompt closed...')


class TextInputPrompt(Prompt):

    WIDGET_TYPE = 'TEXT_INPUT_PROMPT'

    def on_event(self, entity, value):
        self.close()
        if value is False:
            log.debug('Prompt closed...')
        elif value is not None:
            log.warning(f'Text: {value.txt}')
            # self.callback(value.txt)


class AlphabeticSelectPrompt(Prompt):

    WIDGET_TYPE = 'ALPHABETIC_SELECT_PROMPT'

    def on_event(self, entity, value):
        self.close()
        if value is False:
            log.debug('Prompt closed...')
        elif value is not None:
            log.warning(f'Selected: {value}')
            # self.callback(value.txt)

