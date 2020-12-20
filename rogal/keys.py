import tcod.event

from .geometry import Direction


# *_MOVE_KEYS = {key_symbol: (dx, dy), }
ARROW_MOVE_KEYS = {
    tcod.event.K_LEFT: Direction.W,
    tcod.event.K_RIGHT: Direction.E,
    tcod.event.K_UP: Direction.N,
    tcod.event.K_DOWN: Direction.S,
    tcod.event.K_HOME: Direction.NW,
    tcod.event.K_END: Direction.SW,
    tcod.event.K_PAGEUP: Direction.NE,
    tcod.event.K_PAGEDOWN: Direction.SE,
}
NUMPAD_MOVE_KEYS = {
    tcod.event.K_KP_1: Direction.SW,
    tcod.event.K_KP_2: Direction.S,
    tcod.event.K_KP_3: Direction.SE,
    tcod.event.K_KP_4: Direction.W,
    tcod.event.K_KP_6: Direction.E,
    tcod.event.K_KP_7: Direction.NW,
    tcod.event.K_KP_8: Direction.N,
    tcod.event.K_KP_9: Direction.NE,
}
VI_MOVE_KEYS = {
    tcod.event.K_h: Direction.W,
    tcod.event.K_j: Direction.S,
    tcod.event.K_k: Direction.N,
    tcod.event.K_l: Direction.E,
    tcod.event.K_y: Direction.NW,
    tcod.event.K_u: Direction.NE,
    tcod.event.K_b: Direction.SW,
    tcod.event.K_n: Direction.SE,
}

MOVE_KEYS = {}
MOVE_KEYS.update(ARROW_MOVE_KEYS)
MOVE_KEYS.update(NUMPAD_MOVE_KEYS)
MOVE_KEYS.update(VI_MOVE_KEYS)


WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR, # Numpad `clear` key.
}


CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}


ESCAPE_KEY = tcod.event.K_ESCAPE


MODIFIER_SHIFT_KEYS = {
    tcod.event.K_LSHIFT,
    tcod.event.K_RSHIFT,
}
MODIFIER_CTRL_KEYS = {
    tcod.event.K_LCTRL,
    tcod.event.K_RCTRL,
}
MODIFIER_ALT_KEYS = {
    tcod.event.K_LALT,
    tcod.event.K_RALT,
}

MODIFIER_KEYS = MODIFIER_SHIFT_KEYS | MODIFIER_CTRL_KEYS | MODIFIER_ALT_KEYS

