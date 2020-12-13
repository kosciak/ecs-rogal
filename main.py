#!/usr/bin/env python3

from geometry import Size
from colors.x11 import TANGO_DARK, Color
from tilesets import TERMINAL_12x12_CP
from wrappers import TcodWrapper
import keys

import tcod


CONSOLE_SIZE = Size(80, 50)


def main():
    wrapper = TcodWrapper(
        console_size=CONSOLE_SIZE,
        palette=TANGO_DARK,
        tileset=TERMINAL_12x12_CP,
        resizable=False,
        title='Rogal test'
    )

    with wrapper as wrapper:
        root_panel = wrapper.create_root_panel()
        position = root_panel.center
        while True:
            root_panel.clear()
            root_panel.print('@', position)
            wrapper.flush(root_panel.console)
            for event in wrapper.events():
                # Just print all events, and gracefully quit on closing window
                print(event)
                if event.type == 'KEYDOWN':
                    key = event.sym
                    if key == keys.ESCAPE_KEY:
                        raise SystemExit()

                    direction = keys.MOVE_KEYS.get(key)
                    if direction:
                        position = position.move(direction)

                if event.type == 'QUIT':
                    raise SystemExit()


if __name__ == "__main__":
    main()
