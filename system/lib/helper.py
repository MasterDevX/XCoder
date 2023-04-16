from typing import List, Tuple, TypeAlias

from system.lib.objects.point import Point

PointType: TypeAlias = Tuple[float, float] | Tuple[int, int] | Point


def get_size(left: float, top: float, right: float, bottom: float) -> Tuple[int, int]:
    """Returns width and height of given rect.

    :param left: left side of polygon
    :param top: top side of polygon
    :param right: right side of polygon
    :param bottom: bottom side of polygon
    :return: width, height
    """
    return int(right - left), int(bottom - top)


def get_sides(
    points: List[Tuple[float, float]] | List[Tuple[int, int]] | List[Point]
) -> Tuple[float, float, float, float]:
    """Calculates and returns rect sides.

    :param points: polygon points
    :return: left, top, right, bottom
    """

    if len(points) > 0:
        point: PointType = points[0]
        if isinstance(point, Point):
            left = min(point.x for point in points)  # type: ignore
            top = min(point.y for point in points)  # type: ignore
            right = max(point.x for point in points)  # type: ignore
            bottom = max(point.y for point in points)  # type: ignore
        elif isinstance(point, tuple):
            left = min(x for x, _ in points)  # type: ignore
            top = min(y for _, y in points)  # type: ignore
            right = max(x for x, _ in points)  # type: ignore
            bottom = max(y for _, y in points)  # type: ignore
        else:
            raise TypeError("Unknown point type.")

        return left, top, right, bottom
    raise ValueError("Empty points list.")
