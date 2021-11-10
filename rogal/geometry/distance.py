import math


def euclidean_distance(position, other):
    """Return Euclidean distance between points."""
    delta_x = position.x - other.x
    delta_y = position.y - other.y
    return math.hypot(delta_x, delta_y)


def chebyshev_distance(position, other):
    """Return Chebyshev distance between points.

    AKA chessboard distance, both ordinal and diagonal movements has the same cost.

    """
    return max(abs(position.x-other.x), abs(position.y-other.y))


def manhattan_distance(position, other):
    """Return Manhattan distance between points.

    AKA taxicab distance - sum of absolute differences. Diagonal movement has twice the cost.

    """
    return abs(position.x-other.x) + abs(position.y-other.y)

