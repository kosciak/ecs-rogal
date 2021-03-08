import functools

from cffi import FFI

from .sdl_const import (
    SubSystem,
    EventType, Keycode, Keymod, MouseButton, MouseButtonMask, MouseWheelDirection,
    SystemCursor,
)

from .. import events
from ..events.keys import Key, Button


"""Use SDL data directly instead of tcod wrappers."""


ffi = FFI()


SDL_KEYCODE_TO_KEY = {
    Keycode.SDLK_ESCAPE: Key.ESCAPE,

    Keycode.SDLK_F1: Key.F1,
    Keycode.SDLK_F2: Key.F2,
    Keycode.SDLK_F3: Key.F3,
    Keycode.SDLK_F4: Key.F4,
    Keycode.SDLK_F5: Key.F5,
    Keycode.SDLK_F6: Key.F6,
    Keycode.SDLK_F7: Key.F7,
    Keycode.SDLK_F8: Key.F8,
    Keycode.SDLK_F9: Key.F9,
    Keycode.SDLK_F10: Key.F10,
    Keycode.SDLK_F11: Key.F11,
    Keycode.SDLK_F12: Key.F12,

    Keycode.SDLK_BACKSPACE: Key.BACKSPACE,

    Keycode.SDLK_TAB: Key.TAB,

    Keycode.SDLK_RETURN: Key.RETURN,

    Keycode.SDLK_SPACE: Key.SPACE,

    Keycode.SDLK_UP: Key.UP,
    Keycode.SDLK_DOWN: Key.DOWN,
    Keycode.SDLK_LEFT: Key.LEFT,
    Keycode.SDLK_RIGHT: Key.RIGHT,

    Keycode.SDLK_INSERT: Key.INSERT,
    Keycode.SDLK_DELETE: Key.DELETE,
    Keycode.SDLK_HOME: Key.HOME,
    Keycode.SDLK_END: Key.END,
    Keycode.SDLK_PAGEUP: Key.PAGE_UP,
    Keycode.SDLK_PAGEDOWN: Key.PAGE_DOWN,

    Keycode.SDLK_KP_0: Key.KP_0,
    Keycode.SDLK_KP_1: Key.KP_1,
    Keycode.SDLK_KP_2: Key.KP_2,
    Keycode.SDLK_KP_3: Key.KP_3,
    Keycode.SDLK_KP_4: Key.KP_4,
    Keycode.SDLK_KP_5: Key.KP_5,
    Keycode.SDLK_KP_6: Key.KP_6,
    Keycode.SDLK_KP_7: Key.KP_7,
    Keycode.SDLK_KP_8: Key.KP_8,
    Keycode.SDLK_KP_9: Key.KP_9,

    Keycode.SDLK_KP_DIVIDE: Key.KP_DIVIDE,
    Keycode.SDLK_KP_MULTIPLY: Key.KP_MULTIPLY,
    Keycode.SDLK_KP_MINUS: Key.KP_MINUS,
    Keycode.SDLK_KP_PLUS: Key.KP_PLUS,
    Keycode.SDLK_KP_ENTER: Key.KP_ENTER,
    Keycode.SDLK_KP_PERIOD: Key.KP_PERIOD,
    Keycode.SDLK_KP_COMMA: Key.KP_COMMA,
    Keycode.SDLK_KP_CLEAR: Key.CLEAR,
}


SDL_MOUSE_BUTTON_TO_BUTTON = {
    MouseButton.SDL_BUTTON_LEFT: Button.MOUSE_LEFT,
    MouseButton.SDL_BUTTON_MIDDLE: Button.MOUSE_MIDDLE,
    MouseButton.SDL_BUTTON_RIGHT: Button.MOUSE_RIGHT,
    MouseButton.SDL_BUTTON_X1: Button.MOUSE_X1,
    MouseButton.SDL_BUTTON_X2: Button.MOUSE_X2,
}


@functools.lru_cache(maxsize=None)
def get_key(sym, mod):
    if 32 <= sym <= 126:
        key = chr(sym)
    else:
        key = SDL_KEYCODE_TO_KEY.get(sym, str(sym))
    return Key.with_modifiers(
        key,
        ctrl=mod & Keymod.KMOD_CTRL,
        alt=mod & Keymod.KMOD_ALT,
        shift=mod & Keymod.KMOD_SHIFT,
    )


def parse_quit_event(sdl_event):
    return events.Quit(sdl_event)


def parse_window_event(sdl_event):
    event_id = sdl_event.window.event
    # TODO: WindowEvent subclasses based on event_id?
    return events.WindowEvent(sdl_event, event_id)


def parse_keyboard_event(sdl_event):
    if sdl_event.type == EventType.SDL_KEYDOWN:
        event_cls = events.KeyPress
    elif sdl_event.type == EventType.SDL_KEYUP:
        event_cls = events.KeyUp
    repeat = bool(sdl_event.key.repeat)
    keysym = sdl_event.key.keysym
    key = get_key(keysym.sym, keysym.mod)
    return event_cls(sdl_event, key, repeat)


def parse_text_input_event(sdl_event):
    text = ffi.string(sdl_event.text.text, 32).decode("utf8")
    return events.TextInput(sdl_event, text)


def parse_mouse_motion_event(sdl_event):
    motion = sdl_event.motion
    state = motion.state
    buttons = []
    if state & MouseButtonMask.SDL_BUTTON_LMASK:
        buttons.append(SDL_MOUSE_BUTTON_TO_BUTTON[MouseButton.SDL_BUTTON_LEFT])
    if state & MouseButtonMask.SDL_BUTTON_MMASK:
        buttons.append(SDL_MOUSE_BUTTON_TO_BUTTON[MouseButton.SDL_BUTTON_MIDDLE])
    if state & MouseButtonMask.SDL_BUTTON_RMASK:
        buttons.append(SDL_MOUSE_BUTTON_TO_BUTTON[MouseButton.SDL_BUTTON_RIGHT])
    if state & MouseButtonMask.SDL_BUTTON_X1MASK:
        buttons.append(SDL_MOUSE_BUTTON_TO_BUTTON[MouseButton.SDL_BUTTON_X1])
    if state & MouseButtonMask.SDL_BUTTON_X2MASK:
        buttons.append(SDL_MOUSE_BUTTON_TO_BUTTON[MouseButton.SDL_BUTTON_X2])
    return events.MouseMotion(sdl_event, motion.x, motion.y, motion.xrel, motion.yrel, buttons)


def parse_mouse_button_event(sdl_event):
    if sdl_event.type == EventType.SDL_MOUSEBUTTONDOWN:
        event_cls = events.MouseButtonPress
    elif sdl_event.type == EventType.SDL_MOUSEBUTTONUP:
        event_cls = events.MouseButtonUp
    btn = sdl_event.button
    button = SDL_MOUSE_BUTTON_TO_BUTTON.get(btn.button)
    return event_cls(sdl_event, btn.x, btn.y, button, btn.clicks)


def parse_mouse_wheel_event(sdl_event):
    wheel = sdl_event.wheel
    dx = wheel.x
    dy = wheel.y
    if wheel.direction == MouseWheelDirection.SDL_MOUSEWHEEL_FLIPPED:
        dx *= -1
        dy *= -1
    return events.MouseWheel(sdl_event, dx, dy)


def parse_joy_axis_motion_event(sdl_event):
    axis = sdl_event.jaxis
    return events.JoyAxisMotion(sdl_event, axis.axis, axis.value)


def parse_joy_hat_motion_event(sdl_event):
    hat = sdl_event.jhat
    return events.JoyHatMotion(sdl_event, hat.hat, hat.value)


def parse_joy_button_event(sdl_event):
    if sdl_event.type == EventType.SDL_JOYBUTTONDOWN:
        event_cls = events.JoyButtonPress
    elif sdl_event.type == EventType.SDL_JOYBUTTONUP:
        event_cls = events.JoyButtonUp
    btn = sdl_event.jbutton
    button = btn.button
    return event_cls(sdl_event, button)


SDL_EVENT_PARSERS = {
    EventType.SDL_QUIT: parse_quit_event,

    # Window events
    EventType.SDL_WINDOWEVENT: parse_window_event,

    # Keyboard events
    EventType.SDL_KEYDOWN: parse_keyboard_event,
    EventType.SDL_KEYUP: parse_keyboard_event,
    EventType.SDL_TEXTINPUT: parse_text_input_event,

    # Mouse events
    EventType.SDL_MOUSEMOTION: parse_mouse_motion_event,
    EventType.SDL_MOUSEBUTTONDOWN: parse_mouse_button_event,
    EventType.SDL_MOUSEBUTTONUP: parse_mouse_button_event,
    EventType.SDL_MOUSEWHEEL: parse_mouse_wheel_event,

    # Joystick events
    EventType.SDL_JOYAXISMOTION: parse_joy_axis_motion_event,
    # EventType.SDL_JOYBALLMOTION = 1537
    EventType.SDL_JOYHATMOTION: parse_joy_hat_motion_event,
    EventType.SDL_JOYBUTTONDOWN: parse_joy_button_event,
    EventType.SDL_JOYBUTTONUP: parse_joy_button_event,

    # Controller events
    # EventType.SDL_CONTROLLERAXISMOTION = 1616
    # EventType.SDL_CONTROLLERBUTTONDOWN = 1617
    # EventType.SDL_CONTROLLERBUTTONUP = 1618
}


def parse_sdl_event(sdl_event):
    parse_fn = SDL_EVENT_PARSERS.get(sdl_event.type)
    if parse_fn:
        return parse_fn(sdl_event)
    else:
        return events.UnknownEvent(sdl_event)


class SDL2Wrapper:

    def __init__(self, ffi, lib):
        self.ffi = ffi
        self.lib = lib

    def _parse_string(self, txt):
        txt = self.ffi.string(txt).decode('utf-8')
        return txt

    def SDL_GetError(self):
        # See: https://wiki.libsdl.org/SDL_GetError
        txt = self.lib.SDL_GetError()
        return self._parse_string(txt)


    # https://wiki.libsdl.org/CategoryClipboard
    def SDL_GetClipboardText(self):
        # See: https://wiki.libsdl.org/SDL_GetClipboardText
        txt = self.lib.SDL_GetClipboardText()
        return self._parse_string(txt)

    # def SDL_HasClipboardText()


    # https://wiki.libsdl.org/CategoryJoystick

    # def SDL_JoystickOpen(joystick_id)

    # def SDL_JoystickNumAxes(joystick)
    # def SDL_JoystickNumButtons(joystick)
    # def SDL_JoystickNumBalls(joystick)
    # def SDL_JoystickNumHats(joystick)

    def SDL_JoystickName(self, joystick):
        # See: https://wiki.libsdl.org/SDL_JoystickName
        txt = self.lib.SDL_JoystickName(joystick)
        return self._parse_string(txt)

    def SDL_JoystickNameForIndex(self, joystick_id):
        # See: https://wiki.libsdl.org/SDL_JoystickNameForIndex
        txt = self.lib.SDL_JoystickNameForIndex(joystick_id)
        return self._parse_string(txt)


    # https://wiki.libsdl.org/CategoryEvents

    def SDL_WaitEvent(self, sdl_event):
        # See: https://wiki.libsdl.org/SDL_WaitEvent
        if sdl_event is None:
            sdl_event = self.ffi.NULL
        return self.lib.SDL_WaitEvent(sdl_event)

    def SDL_WaitEventTimeout(self, sdl_event, timeout):
        # See: https://wiki.libsdl.org/SDL_WaitEventTimeout
        if sdl_event is None:
            sdl_event = self.ffi.NULL
        timeout = int(timeout*1000)
        return self.lib.SDL_WaitEventTimeout(sdl_event, timeout)

    def __getattr__(self, name):
        return getattr(self.lib, name)


    def get_events(self):
        sdl_event = self.ffi.new("SDL_Event*")
        while self.lib.SDL_PollEvent(sdl_event):
            yield parse_sdl_event(sdl_event)

    def wait_for_events(self, timeout=None):
        if timeout is not None:
            self.SDL_WaitEventTimeout(None, timeout)
        else:
            self.SDL_WaitEvent(None)
        return self.get_events()

