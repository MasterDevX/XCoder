from typing import List, Tuple

from system.lib.objects.point import Point


def get_size(left: float, top: float, right: float, bottom: float) -> (int, int):
    """Returns width and height of given rect.

    :param left: left side of polygon
    :param top: top side of polygon
    :param right: right side of polygon
    :param bottom: bottom side of polygon
    :return: width, height
    """
    return int(right - left), int(bottom - top)


def get_sides(
    points: List[Tuple[float, float]] or List[Point]
) -> (float, float, float, float):
    """Calculates and returns rect sides.

    :param points: polygon points
    :return: left, top, right, bottom
    """
    if len(points) > 0:
        point = points[0]
        if isinstance(point, Point):
            left = min(point.x for point in points)
            top = min(point.y for point in points)
            right = max(point.x for point in points)
            bottom = max(point.y for point in points)
        elif isinstance(point, tuple):
            left = min(x for x, _ in points)
            top = min(y for _, y in points)
            right = max(x for x, _ in points)
            bottom = max(y for _, y in points)
        else:
            raise TypeError("Unknown point type.")

        return left, top, right, bottom
    raise ValueError("Empty points list.")
