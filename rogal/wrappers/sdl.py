
from .sdl_const import (
    SDL_SubSystem,
    SDL_EventType,
    SDL_WindowEventID,
    SDL_Keycode, SDL_Keymod,
    SDL_MouseButton, SDL_MouseButtonMask, SDL_MouseWheelDirection,
    SDL_SystemCursor,
)


"""Use SDL data directly instead of tcod wrappers."""


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
        event = self.ffi.new("SDL_Event*")
        return event

    def SDL_WaitEvent(self, event):
        # See: https://wiki.libsdl.org/SDL_WaitEvent
        if event is None:
            event = self.ffi.NULL
        return self.lib.SDL_WaitEvent(event)

    def SDL_WaitEventTimeout(self, event, timeout):
        # See: https://wiki.libsdl.org/SDL_WaitEventTimeout
        if event is None:
            event = self.ffi.NULL
        timeout = int(timeout*1000)
        return self.lib.SDL_WaitEventTimeout(event, timeout)

    def __getattr__(self, name):
        return getattr(self.lib, name)


    def get_events(self):
        event = self.SDL_Event()
        while self.lib.SDL_PollEvent(event):
            yield event

    def wait_for_events(self, timeout=None):
        if timeout is not None:
            self.SDL_WaitEventTimeout(None, timeout)
        else:
            self.SDL_WaitEvent(None)
        return self.get_events()

