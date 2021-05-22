#!/usr/bin/env python3

import argparse

from . import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # parser.add_argument(
    #     'wrapper',
    #     nargs='?',
    #     choices=sorted(main.WRAPPERS.keys()),
    #     default='tcod',
    # )

    for wrapper in sorted(main.WRAPPERS.keys()):
        parser.add_argument(
            f'--{wrapper}', const=wrapper, action='store_const', dest='wrapper',
        )

    args = parser.parse_args()

    wrapper = args.wrapper or 'tcod'
    main.run(wrapper)

