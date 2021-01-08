import unittest

from rogal.geometry import euclidean_distance
from rogal.geometry import Direction, Position, Size, Rectangle


class EuclideanDistancecTest(unittest.TestCase):

    def test_distance(self):
        for position, other, expected in [
            (Position(0, 0), Position(1, 0), 1),
            (Position(0, 0), Position(0, 1), 1),
            (Position(0, 0), Position(2, 0), 2),
            (Position(0, 0), Position(0, 2), 2),
            # reverse other, position
            (Position(1, 0), Position(0, 0), 1),
            (Position(0, 1), Position(0, 0), 1),
            (Position(2, 0), Position(0, 0), 2),
            (Position(0, 2), Position(0, 0), 2),

            (Position(0, 0), Position(-1, 0), 1),
            (Position(0, 0), Position(0, -1), 1),
            (Position(0, 0), Position(-2, 0), 2),
            (Position(0, 0), Position(0, -2), 2),

            (Position(1, 1), Position(2, 1), 1),
            (Position(1, 1), Position(1, 2), 1),

            (Position(0, 0), Position(1, 1), 1.4142135623730951),
            (Position(0, 0), Position(-1, 1), 1.4142135623730951),
            (Position(0, 0), Position(1, -1), 1.4142135623730951),
            (Position(0, 0), Position(-1, -1), 1.4142135623730951),
            (Position(0, 0), Position(1, 2), 2.23606797749979),
            (Position(0, 0), Position(2, 1), 2.23606797749979),
        ]:
            distance = euclidean_distance(position, other)
            self.assertEqual(distance, expected)


class PositionTests(unittest.TestCase):

    def test_new(self):
        for x, y, expected in [
            (0, 0, Position(0, 0)),
            (1, 1, Position(1, 1)),
            (-1, -1, Position(-1, -1)),
            (.1, .1, Position(0, 0)),
            (.5, .5, Position(0, 0)),
            (.9, .9, Position(0, 0)),
        ]:
            position = Position(x, y)
            self.assertEqual(position, expected)

    def test_move(self):
        position = Position(1, 1)
        for direction, expected in [
            (Direction.N, Position(1, 0)),
            (Direction.E, Position(2, 1)),
            (Direction.S, Position(1, 2)),
            (Direction.W, Position(0, 1)),
            (Direction.NE, Position(2, 0)),
            (Direction.SE, Position(2, 2)),
            (Direction.SW, Position(0, 2)),
            (Direction.NW, Position(0, 0)),
            (None, position),
        ]:
            moved = position.move(direction)
            self.assertEqual(moved, expected)

    def test_add(self):
        for position, other, expected in [
            (Position(0, 0), None, None),
            (Position(0, 0), Position(0, 0), Position(0, 0)),
            (Position(1, 1), Position(0, 0), Position(1, 1)),
            (Position(-1, -1), Position(0, 0), Position(-1, -1)),
            (Position(1, 1), Position(1, 1), Position(2, 2)),
            (Position(3, 2), Position(1, 1), Position(4, 3)),
            (Position(1, 1), Position(3, 2), Position(4, 3)),
            (Position(1, 1), Position(-1, -1), Position(0, 0)),
        ]:
            added = position + other
            self.assertEqual(added, expected)

    def test_sub(self):
        for position, other, expected in [
            (Position(0, 0), None, None),
            (Position(0, 0), Position(0, 0), Position(0, 0)),
            (Position(1, 1), Position(0, 0), Position(1, 1)),
            (Position(-1, -1), Position(0, 0), Position(-1, -1)),
            (Position(1, 1), Position(1, 1), Position(0, 0)),
            (Position(3, 2), Position(1, 1), Position(2, 1)),
            (Position(1, 1), Position(3, 2), Position(-2, -1)),
            (Position(1, 1), Position(-1, -1), Position(2, 2)),
        ]:
            added = position - other
            self.assertEqual(added, expected)


class SizeTests(unittest.TestCase):

    def test_new(self):
        for x, y, expected in [
            (0, 0, Size(0, 0)),
            (1, 1, Size(1, 1)),
            (.1, .1, Size(0, 0)),
            (.5, .5, Size(0, 0)),
            (.9, .9, Size(0, 0)),
        ]:
            size = Size(x, y)
            self.assertEqual(size, expected)

    def test_area(self):
        for size, expected in [
            (Size(1, 1), 1),
            (Size(2, 1), 2),
            (Size(1, 2), 2),
            (Size(2, 2), 4),
            (Size(3, 4), 12),
        ]:
            area = size.area
            self.assertEqual(area, expected)

    def test_mul(self):
        for size, factor, expected in [
            (Size(2, 2), 1, Size(2, 2)),
            (Size(2, 2), 2, Size(4, 4)),
            (Size(4, 2), 2, Size(8, 4)),
            (Size(2, 2), .5, Size(1, 1)),
            (Size(8, 4), .25, Size(2, 1)),
        ]:
            resized = size * factor
            self.assertEqual(resized, expected)


class RectangleTest(unittest.TestCase):

    def test_center(self):
        for rectangle, expected in [
            (Rectangle(Position.ZERO, Size(1, 1)), Position(0, 0)),
            (Rectangle(Position.ZERO, Size(2, 2)), Position(1, 1)),
            (Rectangle(Position.ZERO, Size(4, 4)), Position(2, 2)),
            (Rectangle(Position.ZERO, Size(4, 2)), Position(2, 1)),
            (Rectangle(Position.ZERO, Size(2, 4)), Position(1, 2)),
            (Rectangle(Position.ZERO, Size(3, 3)), Position(1, 1)),
            (Rectangle(Position.ZERO, Size(5, 5)), Position(2, 2)),
            (Rectangle(Position(1, 1), Size(3, 3)), Position(2, 2)),
        ]:
            center = rectangle.center
            self.assertEqual(center, expected)

    def test_positions(self):
        for rectangle in [
            Rectangle(Position.ZERO, Size(1,1)),
            Rectangle(Position.ZERO, Size(5,3)),
            Rectangle(Position.ZERO, Size(10,10)),
            Rectangle(Position(-2, -2), Size(5,3)),
            Rectangle(Position(2, 2), Size(5,3)),
        ]:
            count = 0
            for position in rectangle.positions:
                self.assertTrue(position in rectangle)
                count += 1
            self.assertEqual(count, rectangle.area)

    def test_is_inside(self):
        rectangle = Rectangle(Position.ZERO, Size(3, 3))
        # is_inside == True
        for position in [
            rectangle.position,
            rectangle.center,
        ]:
            self.assertTrue(position in rectangle)
        # is_inside == False
        for position in [
            Position(rectangle.x2, rectangle.y2),
            Position(rectangle.x2, rectangle.y),
            Position(rectangle.x, rectangle.y2),

            Position(-1, -1),
            Position(100, 100),
        ]:
            self.assertFalse(position in rectangle)

    def test_intersection(self):
        rectangle = Rectangle(Position(10, 10), Size(10, 10))
        for other, expected in [
            (Rectangle(Position.ZERO, Size(5, 5)), None),
            (Rectangle(Position.ZERO, Size(10, 10)), None),
            (Rectangle(Position.ZERO, Size(15, 15)), Rectangle(Position(10, 10), Size(5, 5))),
            (Rectangle(Position.ZERO, Size(15, 25)), Rectangle(Position(10, 10), Size(5, 10))),

            (rectangle, rectangle),

            (Rectangle(Position(15, 15), Size(5, 5)), Rectangle(Position(15, 15), Size(5, 5))),

            (Rectangle(Position(rectangle.x2, rectangle.y2), Size(1,1)), None),
            (Rectangle(Position(rectangle.x2, rectangle.y), Size(1,1)), None),
            (Rectangle(Position(rectangle.x, rectangle.y2), Size(1,1)), None),
        ]:
            intersection = rectangle & other
            self.assertEqual(intersection, expected)

