import functools
import logging

from . import components


log = logging.getLogger(__name__)


class Prompt:

    WIDGEt_TYPE = None

    def __init__(self, ecs, context, callback, *args, **kwargs):
        self.ecs = ecs

        self.window = None
        self.context = context
        self.callback = functools.partial(callback, *args, **kwargs)
        self.context['callback'] = self.on_event

    def show(self):
        # Show prompt window and set events_handler
        self.window = self.ecs.create(
            components.CreateUIWidget(
                widget_type=self.WIDGEt_TYPE,
                context=self.context,
            ),
        )

    def close(self):
        # Close prompt window
        self.ecs.manage(components.DestroyUIWidget).insert(self.window)

    def on_event(self, entity, value):
        raise NotImplementedError()


class YesNoPrompt(Prompt):

    WIDGEt_TYPE = 'YES_NO_PROMPT'

    def on_event(self, entity, value):
        self.close()
        if value is True:
            self.callback()
        if value is False:
            log.debug('Prompt closed...')


class TextInputPrompt(Prompt):

    WIDGEt_TYPE = 'TEXT_INPUT_PROMPT'

    def on_event(self, entity, value):
        self.close()
        if value is False:
            log.debug('Prompt closed...')
        elif value is not None:
            log.warning(value.txt)
            # self.callback(value.txt)

