from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from .geometry import EPS, Point


@dataclass(frozen=True, slots=True)
class BBox:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def rect(self) -> List[Point]:
        return [
            Point(self.xmin, self.ymin),
            Point(self.xmax, self.ymin),
            Point(self.xmax, self.ymax),
            Point(self.xmin, self.ymax),
        ]


def sutherland_hodgman_polygon_clip(
    subject_polygon: List[Point],
    inside: Callable[[Point], bool],
    intersect: Callable[[Point, Point], Point],
) -> List[Point]:
    """Generic Sutherland–Hodgman polygon clipping for one clipping boundary."""
    if not subject_polygon:
        return []

    input_list = subject_polygon[:]
    output: List[Point] = []

    s = input_list[-1]
    for e in input_list:
        if inside(e):
            if not inside(s):
                output.append(intersect(s, e))
            output.append(e)
        elif inside(s):
            output.append(intersect(s, e))
        s = e
    return output


def clip_polygon_to_bbox(poly: List[Point], bbox: BBox) -> List[Point]:
    """Clip polygon against axis-aligned rectangle."""
    out = poly[:]
    if not out:
        return []

    # left: x >= xmin
    def inside(p: Point) -> bool:
        return p.x >= bbox.xmin - EPS

    def intersect(s: Point, e: Point) -> Point:
        dx = e.x - s.x
        if abs(dx) <= EPS:
            return Point(bbox.xmin, s.y)
        t = (bbox.xmin - s.x) / dx
        return Point(bbox.xmin, s.y + t * (e.y - s.y))

    out = sutherland_hodgman_polygon_clip(out, inside, intersect)
    if not out:
        return []

    # right: x <= xmax
    def inside(p: Point) -> bool:
        return p.x <= bbox.xmax + EPS

    def intersect(s: Point, e: Point) -> Point:
        dx = e.x - s.x
        if abs(dx) <= EPS:
            return Point(bbox.xmax, s.y)
        t = (bbox.xmax - s.x) / dx
        return Point(bbox.xmax, s.y + t * (e.y - s.y))

    out = sutherland_hodgman_polygon_clip(out, inside, intersect)
    if not out:
        return []

    # bottom: y >= ymin
    def inside(p: Point) -> bool:
        return p.y >= bbox.ymin - EPS

    def intersect(s: Point, e: Point) -> Point:
        dy = e.y - s.y
        if abs(dy) <= EPS:
            return Point(s.x, bbox.ymin)
        t = (bbox.ymin - s.y) / dy
        return Point(s.x + t * (e.x - s.x), bbox.ymin)

    out = sutherland_hodgman_polygon_clip(out, inside, intersect)
    if not out:
        return []

    # top: y <= ymax
    def inside(p: Point) -> bool:
        return p.y <= bbox.ymax + EPS

    def intersect(s: Point, e: Point) -> Point:
        dy = e.y - s.y
        if abs(dy) <= EPS:
            return Point(s.x, bbox.ymax)
        t = (bbox.ymax - s.y) / dy
        return Point(s.x + t * (e.x - s.x), bbox.ymax)

    out = sutherland_hodgman_polygon_clip(out, inside, intersect)
    return out
