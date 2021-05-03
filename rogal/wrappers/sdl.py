import functools

from .. import events
from ..events.keys import Key, Keycode
from ..events.mouse import MouseButton

from .sdl_const import (
    SDL_SubSystem,
    SDL_EventType,
    SDL_WindowEventID,
    SDL_Keycode, SDL_Keymod,
    SDL_MouseButton, SDL_MouseButtonMask, SDL_MouseWheelDirection,
    SDL_SystemCursor,
)


"""Use SDL data directly instead of tcod wrappers."""


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


def parse_quit_event(ffi, sdl_event):
    return events.Quit(sdl_event)


def parse_window_event(ffi, sdl_event):
    event_id = sdl_event.window.event
    # TODO: WindowEvent subclasses based on event_id?
    return events.WindowEvent(sdl_event, event_id)


def parse_keyboard_event(ffi, sdl_event):
    if sdl_event.type == SDL_EventType.SDL_KEYDOWN:
        event_cls = events.KeyPress
    elif sdl_event.type == SDL_EventType.SDL_KEYUP:
        event_cls = events.KeyUp
    repeat = bool(sdl_event.key.repeat)
    keysym = sdl_event.key.keysym
    key = get_key(keysym.sym, keysym.mod)
    return event_cls(sdl_event, key, repeat)


def parse_text_input_event(ffi, sdl_event):
    text = ffi.string(sdl_event.text.text, 32).decode("utf8")
    return events.TextInput(sdl_event, text)


def parse_mouse_motion_event(ffi, sdl_event):
    motion = sdl_event.motion
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

    return events.MouseMotion(sdl_event, motion.x, motion.y, motion.xrel, motion.yrel, buttons)


def parse_mouse_button_event(ffi, sdl_event):
    if sdl_event.type == SDL_EventType.SDL_MOUSEBUTTONDOWN:
        event_cls = events.MouseButtonPress
    elif sdl_event.type == SDL_EventType.SDL_MOUSEBUTTONUP:
        event_cls = events.MouseButtonUp
    btn = sdl_event.button
    button = SDL_MOUSE_BUTTONS.get(btn.button)
    return event_cls(sdl_event, btn.x, btn.y, button, btn.clicks)


def parse_mouse_wheel_event(ffi, sdl_event):
    wheel = sdl_event.wheel
    dx = wheel.x
    dy = wheel.y
    if wheel.direction == SDL_MouseWheelDirection.SDL_MOUSEWHEEL_FLIPPED:
        dx *= -1
        dy *= -1
    return events.MouseWheel(sdl_event, dx, dy)


def parse_joy_axis_motion_event(ffi, sdl_event):
    axis = sdl_event.jaxis
    return events.JoyAxisMotion(sdl_event, axis.axis, axis.value)


def parse_joy_hat_motion_event(ffi, sdl_event):
    hat = sdl_event.jhat
    return events.JoyHatMotion(sdl_event, hat.hat, hat.value)


def parse_joy_button_event(ffi, sdl_event):
    if sdl_event.type == SDL_EventType.SDL_JOYBUTTONDOWN:
        event_cls = events.JoyButtonPress
    elif sdl_event.type == SDL_EventType.SDL_JOYBUTTONUP:
        event_cls = events.JoyButtonUp
    btn = sdl_event.jbutton
    button = btn.button
    return event_cls(sdl_event, button)


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


def parse_sdl_event(ffi, sdl_event):
    parse_fn = SDL_EVENT_PARSERS.get(sdl_event.type)
    if parse_fn:
        return parse_fn(ffi, sdl_event)
    else:
        return events.UnknownEvent(sdl_event)


class SDL2:

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


    # https://wiki.libsdl.org/CategoryMouse

    # def SDL_CreateSystemCursor(cursor_id)
    # def SDL_SetCursor(cursor)

    def SDL_ShowCursor(self, toggle=None):
        # https://wiki.libsdl.org/SDL_ShowCursor
        if toggle is None:
            is_set = self.SDL_ShowCursor(-1)
            if is_set:
                return self.SDL_ShowCursor(0)
            else:
                return self.SDL_ShowCursor(1)
        if toggle:
            return self.SDL_ShowCursor(1)
        else:
            return self.SDL_ShowCursor(0)


    # https://wiki.libsdl.org/CategoryEvents

    def SDL_Event(self):
        sdl_event = self.ffi.new("SDL_Event*")
        return sdl_event

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
        sdl_event = self.SDL_Event()
        while self.lib.SDL_PollEvent(sdl_event):
            yield parse_sdl_event(self.ffi, sdl_event)

    def wait_for_events(self, timeout=None):
        if timeout is not None:
            self.SDL_WaitEventTimeout(None, timeout)
        else:
            self.SDL_WaitEvent(None)
        return self.get_events()

