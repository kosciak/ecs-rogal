import tcod.event


# *_MOVE_KEYS = {key_symbol: (dx, dy), }
ARROW_MOVE_KEYS = {
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
}
NUMPAD_MOVE_KEYS = {
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
}
VI_MOVE_KEYS = {
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

MOVE_KEYS = {
    **ARROW_MOVE_KEYS, 
    **NUMPAD_MOVE_KEYS, 
    **VI_MOVE_KEYS,
}


WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR, # Numpad `clear` key.
}


CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}


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

