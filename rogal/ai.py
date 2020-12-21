import random


def random_move(level, position):
    """Return random move direction from allowed exits."""
    exits = level.get_exits(position)
    return random.choice(list(exits))

