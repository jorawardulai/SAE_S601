from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Iterable, Tuple

EPS = 1e-10


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        return (float(self.x), float(self.y))


@dataclass(frozen=True, slots=True)
class Edge:
    a: Point
    b: Point

    def normalized(self) -> "Edge":
        # order-independent identity for boundary detection
        return (
            self
            if (self.a.x, self.a.y, self.b.x, self.b.y)
            <= (self.b.x, self.b.y, self.a.x, self.a.y)
            else Edge(self.b, self.a)
        )


@dataclass(frozen=True, slots=True)
class Triangle:
    a: Point
    b: Point
    c: Point

    def vertices(self) -> Tuple[Point, Point, Point]:
        return (self.a, self.b, self.c)

    def edges(self) -> Tuple[Edge, Edge, Edge]:
        return (Edge(self.a, self.b), Edge(self.b, self.c), Edge(self.c, self.a))


def orientation(a: Point, b: Point, c: Point) -> float:
    """Positive if a->b->c is counter-clockwise, negative if clockwise, 0 if colinear."""
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def circumcenter(t: Triangle) -> Point:
    """
    Circumcenter of triangle.
    Raises ValueError if points are colinear (degenerate).
    """
    ax, ay = t.a.x, t.a.y
    bx, by = t.b.x, t.b.y
    cx, cy = t.c.x, t.c.y

    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) <= EPS:
        raise ValueError("Degenerate triangle: circumcenter undefined (colinear points).")

    ax2ay2 = ax * ax + ay * ay
    bx2by2 = bx * bx + by * by
    cx2cy2 = cx * cx + cy * cy

    ux = (ax2ay2 * (by - cy) + bx2by2 * (cy - ay) + cx2cy2 * (ay - by)) / d
    uy = (ax2ay2 * (cx - bx) + bx2by2 * (ax - cx) + cx2cy2 * (bx - ax)) / d
    return Point(ux, uy)


def in_circumcircle(t: Triangle, p: Point) -> bool:
    """
    True if p lies inside circumcircle of t.
    Uses orientation-aware determinant (robust enough for typical student projects).
    """
    ax, ay = t.a.x - p.x, t.a.y - p.y
    bx, by = t.b.x - p.x, t.b.y - p.y
    cx, cy = t.c.x - p.x, t.c.y - p.y

    det = (
        (ax * ax + ay * ay) * (bx * cy - by * cx)
        - (bx * bx + by * by) * (ax * cy - ay * cx)
        + (cx * cx + cy * cy) * (ax * by - ay * bx)
    )

    # If triangle is CCW, det > 0 means inside. If CW, det < 0 means inside.
    ori = orientation(t.a, t.b, t.c)
    if abs(ori) <= EPS:
        return False
    return det > EPS if ori > 0 else det < -EPS


def unique_points(points: Iterable[Point], eps: float = 1e-12) -> list[Point]:
    """Remove duplicates with small tolerance (stable order)."""
    out: list[Point] = []
    for p in points:
        if not any(isclose(p.x, q.x, abs_tol=eps) and isclose(p.y, q.y, abs_tol=eps) for q in out):
            out.append(p)
    return out
