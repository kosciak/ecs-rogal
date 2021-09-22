import cffi
import functools

from ... import events
from ...events.core import EventType
from ...events.keys import Key, Keycode
from ...events.keyboard import ReapetedKeyPressLimiter
from ...events.mouse import MouseButton, MouseMotionFilter, MouseButtonClickProcessor

from ..core import InputWrapper

from .const import (
    SDL_EventType,
    SDL_WindowEventID,
    SDL_Keycode, SDL_Keymod,
    SDL_MouseButton, SDL_MouseButtonMask, SDL_MouseWheelDirection,
)


SDL_KEYCODES = {
    SDL_Keycode.SDLK_ESCAPE: Keycode.ESCAPE,

    SDL_Keycode.SDLK_F1: Keycode.F1,
    SDL_Keycode.SDLK_F2: Keycode.F2,
    SDL_Keycode.SDLK_F3: Keycode.F3,
    SDL_Keycode.SDLK_F4: Keycode.F4,
    SDL_Keycode.SDLK_F5: Keycode.F5,
    SDL_Keycode.SDLK_F6: Keycode.F6,
    SDL_Keycode.SDLK_F7: Keycode.F7,
    SDL_Keycode.SDLK_F8: Keycode.F8,
    SDL_Keycode.SDLK_F9: Keycode.F9,
    SDL_Keycode.SDLK_F10: Keycode.F10,
    SDL_Keycode.SDLK_F11: Keycode.F11,
    SDL_Keycode.SDLK_F12: Keycode.F12,

    SDL_Keycode.SDLK_BACKSPACE: Keycode.BACKSPACE,

    SDL_Keycode.SDLK_TAB: Keycode.TAB,

    SDL_Keycode.SDLK_RETURN: Keycode.RETURN,

    SDL_Keycode.SDLK_SPACE: Keycode.SPACE,

    SDL_Keycode.SDLK_UP: Keycode.UP,
    SDL_Keycode.SDLK_DOWN: Keycode.DOWN,
    SDL_Keycode.SDLK_LEFT: Keycode.LEFT,
    SDL_Keycode.SDLK_RIGHT: Keycode.RIGHT,

    SDL_Keycode.SDLK_INSERT: Keycode.INSERT,
    SDL_Keycode.SDLK_DELETE: Keycode.DELETE,
    SDL_Keycode.SDLK_HOME: Keycode.HOME,
    SDL_Keycode.SDLK_END: Keycode.END,
    SDL_Keycode.SDLK_PAGEUP: Keycode.PAGE_UP,
    SDL_Keycode.SDLK_PAGEDOWN: Keycode.PAGE_DOWN,

    SDL_Keycode.SDLK_KP_0: Keycode.KP_0,
    SDL_Keycode.SDLK_KP_1: Keycode.KP_1,
    SDL_Keycode.SDLK_KP_2: Keycode.KP_2,
    SDL_Keycode.SDLK_KP_3: Keycode.KP_3,
    SDL_Keycode.SDLK_KP_4: Keycode.KP_4,
    SDL_Keycode.SDLK_KP_5: Keycode.KP_5,
    SDL_Keycode.SDLK_KP_6: Keycode.KP_6,
    SDL_Keycode.SDLK_KP_7: Keycode.KP_7,
    SDL_Keycode.SDLK_KP_8: Keycode.KP_8,
    SDL_Keycode.SDLK_KP_9: Keycode.KP_9,

    SDL_Keycode.SDLK_KP_DIVIDE: Keycode.KP_DIVIDE,
    SDL_Keycode.SDLK_KP_MULTIPLY: Keycode.KP_MULTIPLY,
    SDL_Keycode.SDLK_KP_MINUS: Keycode.KP_MINUS,
    SDL_Keycode.SDLK_KP_PLUS: Keycode.KP_PLUS,
    SDL_Keycode.SDLK_KP_ENTER: Keycode.KP_ENTER,
    SDL_Keycode.SDLK_KP_PERIOD: Keycode.KP_PERIOD,
    SDL_Keycode.SDLK_KP_COMMA: Keycode.KP_COMMA,
    SDL_Keycode.SDLK_KP_CLEAR: Keycode.KP_CLEAR,

    SDL_Keycode.SDLK_LSHIFT: Keycode.SHIFT_LEFT,
    SDL_Keycode.SDLK_LCTRL: Keycode.CTRL_LEFT,
    SDL_Keycode.SDLK_LALT: Keycode.ALT_LEFT,
    SDL_Keycode.SDLK_LGUI: Keycode.GUI_LEFT,
    SDL_Keycode.SDLK_RSHIFT: Keycode.SHIFT_RIGHT,
    SDL_Keycode.SDLK_RCTRL: Keycode.CTRL_RIGHT,
    SDL_Keycode.SDLK_RALT: Keycode.ALT_RIGHT,
    SDL_Keycode.SDLK_RGUI: Keycode.GUI_RIGHT,

    SDL_Keycode.SDLK_MENU: Keycode.MENU,
}


SDL_MOUSE_BUTTONS = {
    SDL_MouseButton.SDL_BUTTON_LEFT: MouseButton.LEFT,
    SDL_MouseButton.SDL_BUTTON_MIDDLE: MouseButton.MIDDLE,
    SDL_MouseButton.SDL_BUTTON_RIGHT: MouseButton.RIGHT,
    SDL_MouseButton.SDL_BUTTON_X1: MouseButton.X1,
    SDL_MouseButton.SDL_BUTTON_X2: MouseButton.X2,
}


@functools.lru_cache(maxsize=None)
def get_key(sym, mod):
    if 32 < sym < 127:
        keycode = sym
    else:
        keycode = SDL_KEYCODES.get(sym, sym)
    return Key(
        keycode,
        ctrl=mod & SDL_Keymod.KMOD_CTRL,
        alt=mod & SDL_Keymod.KMOD_ALT,
        shift=mod & SDL_Keymod.KMOD_SHIFT,
        gui=mod & SDL_Keymod.KMOD_GUI,
    )


def parse_quit_event(ffi, event):
    yield events.Quit(event)


def parse_window_event(ffi, event):
    event_id = event.window.event
    # TODO: WindowEvent subclasses based on event_id?
    if event_id == SDL_WindowEventID.SDL_WINDOWEVENT_TAKE_FOCUS:
        yield events.FocusIn(event)
    elif event_id == SDL_WindowEventID.SDL_WINDOWEVENT_FOCUS_LOST:
        yield events.FocusOut(event)
    else:
        yield events.WindowEvent(event, event_id)


def parse_keyboard_event(ffi, event):
    if event.type == SDL_EventType.SDL_KEYDOWN:
        event_cls = events.KeyPress
    elif event.type == SDL_EventType.SDL_KEYUP:
        event_cls = events.KeyUp
    repeat = bool(event.key.repeat)
    keysym = event.key.keysym
    key = get_key(keysym.sym, keysym.mod)
    yield event_cls(event, key, repeat)


def parse_text_input_event(ffi, event):
    text = ffi.string(event.text.text, 32).decode("utf8")
    yield events.TextInput(event, text)


def parse_mouse_motion_event(ffi, event):
    motion = event.motion
    state = motion.state
    buttons = []

    if state & SDL_MouseButtonMask.SDL_BUTTON_LMASK:
        buttons.append(SDL_MOUSE_BUTTONS[SDL_MouseButton.SDL_BUTTON_LEFT])
    if state & SDL_MouseButtonMask.SDL_BUTTON_MMASK:
        buttons.append(SDL_MOUSE_BUTTONS[SDL_MouseButton.SDL_BUTTON_MIDDLE])
    if state & SDL_MouseButtonMask.SDL_BUTTON_RMASK:
        buttons.append(SDL_MOUSE_BUTTONS[SDL_MouseButton.SDL_BUTTON_RIGHT])
    if state & SDL_MouseButtonMask.SDL_BUTTON_X1MASK:
        buttons.append(SDL_MOUSE_BUTTONS[SDL_MouseButton.SDL_BUTTON_X1])
    if state & SDL_MouseButtonMask.SDL_BUTTON_X2MASK:
        buttons.append(SDL_MOUSE_BUTTONS[SDL_MouseButton.SDL_BUTTON_X2])

    yield events.MouseMotion(event, motion.x, motion.y, motion.xrel, motion.yrel, buttons)


def parse_mouse_button_event(ffi, event):
    if event.type == SDL_EventType.SDL_MOUSEBUTTONDOWN:
        event_cls = events.MouseButtonPress
    elif event.type == SDL_EventType.SDL_MOUSEBUTTONUP:
        event_cls = events.MouseButtonUp
    btn = event.button
    button = SDL_MOUSE_BUTTONS.get(btn.button)
    yield event_cls(event, btn.x, btn.y, button, btn.clicks)


def parse_mouse_wheel_event(ffi, event):
    wheel = event.wheel
    dx = wheel.x
    dy = wheel.y
    if wheel.direction == SDL_MouseWheelDirection.SDL_MOUSEWHEEL_FLIPPED:
        dx *= -1
        dy *= -1
    yield events.MouseWheel(event, dx, dy)


def parse_joy_axis_motion_event(ffi, event):
    axis = event.jaxis
    yield events.JoyAxisMotion(event, axis.axis, axis.value)


def parse_joy_hat_motion_event(ffi, event):
    hat = event.jhat
    yield events.JoyHatMotion(event, hat.hat, hat.value)


def parse_joy_button_event(ffi, event):
    if event.type == SDL_EventType.SDL_JOYBUTTONDOWN:
        event_cls = events.JoyButtonPress
    elif event.type == SDL_EventType.SDL_JOYBUTTONUP:
        event_cls = events.JoyButtonUp
    btn = event.jbutton
    button = btn.button
    yield event_cls(event, button)


SDL_EVENT_PARSERS = {
    SDL_EventType.SDL_QUIT: parse_quit_event,

    # Window events
    SDL_EventType.SDL_WINDOWEVENT: parse_window_event,

    # Keyboard events
    SDL_EventType.SDL_KEYDOWN: parse_keyboard_event,
    SDL_EventType.SDL_KEYUP: parse_keyboard_event,
    SDL_EventType.SDL_TEXTINPUT: parse_text_input_event,

    # Mouse events
    SDL_EventType.SDL_MOUSEMOTION: parse_mouse_motion_event,
    SDL_EventType.SDL_MOUSEBUTTONDOWN: parse_mouse_button_event,
    SDL_EventType.SDL_MOUSEBUTTONUP: parse_mouse_button_event,
    SDL_EventType.SDL_MOUSEWHEEL: parse_mouse_wheel_event,

    # Joystick events
    SDL_EventType.SDL_JOYAXISMOTION: parse_joy_axis_motion_event,
    # SDL_EventType.SDL_JOYBALLMOTION = 1537
    SDL_EventType.SDL_JOYHATMOTION: parse_joy_hat_motion_event,
    SDL_EventType.SDL_JOYBUTTONDOWN: parse_joy_button_event,
    SDL_EventType.SDL_JOYBUTTONUP: parse_joy_button_event,

    # Controller events
    # SDL_EventType.SDL_CONTROLLERAXISMOTION = 1616
    # SDL_EventType.SDL_CONTROLLERBUTTONDOWN = 1617
    # SDL_EventType.SDL_CONTROLLERBUTTONUP = 1618
}


def parse_event(ffi, event):
    parse_fn = SDL_EVENT_PARSERS.get(event.type)
    if parse_fn:
        yield from parse_fn(ffi, event)
    else:
        yield events.UnknownEvent(event)


class SDLInputWrapper(InputWrapper):

    def __init__(self, sdl2):
        super().__init__()
        self.sdl2 = sdl2
        self.ffi = cffi.FFI()

        self.events_processors.extend([
            self.process_key_press_update,
            self.process_modifier_keys,
            ReapetedKeyPressLimiter(
                clear_on_key_up=True,
            ),

            self.process_mouse_position,
            MouseMotionFilter(),
            MouseButtonClickProcessor(),
        ])

    def process_mouse_position(self, events_gen):
        yield from events_gen

    def process_modifier_keys(self, events_gen):
        # Clear modifiers value for Shift, Ctrl, Alt, GUI keys
        for event in events_gen:
            if event.type == EventType.KEY_PRESS:
                if event.key.is_modifier:
                    event.key = Key(event.key.keycode)
            yield event

    def process_key_press_update(self, events_gen):
        events = list(events_gen)
        for i, event in enumerate(events):
            if event.type == EventType.KEY_PRESS:
                # Instead of Shift-a we want to use A, instead of Shift-; -> :
                # It is easy with letters, but not so with punctuations in different places on 
                # different keyboard layouts. But TextInput will always return correct text value
                if i+1 < len(events):
                    next_event = events[i+1]
                    if not next_event.type == EventType.TEXT_INPUT:
                        continue
                    if not event.key.is_keypad:
                        event.key = event.key.replace(next_event.text)
            yield event

    def get_events_gen(self, timeout=None):
        """Get all pending events."""
        if timeout is not None:
            timeout = int(timeout*1000)

        events_gen = self.sdl2.wait_for_events(timeout)
        for event in events_gen:
            yield from parse_event(self.ffi, event)

