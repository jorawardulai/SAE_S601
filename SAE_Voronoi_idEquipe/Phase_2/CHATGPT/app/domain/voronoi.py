from __future__ import annotations

from dataclasses import dataclass
from math import atan2
from typing import Dict, List, Set

from .clipping import BBox, clip_polygon_to_bbox
from .geometry import EPS, Point, Triangle, circumcenter


@dataclass(frozen=True, slots=True)
class VoronoiDiagram:
    cells: Dict[Point, List[Point]]          # site -> polygon (clipped, CCW)
    circumcenters: List[Point]               # optional debug points
    delaunay_triangles: List[Triangle]


def _clip_polygon_by_halfplane(poly: List[Point], a: float, b: float, c: float) -> List[Point]:
    """Keep points where a*x + b*y <= c (half-plane)."""
    if not poly:
        return []

    def inside(p: Point) -> bool:
        return a * p.x + b * p.y <= c + EPS

    def intersection(s: Point, e: Point) -> Point:
        dx = e.x - s.x
        dy = e.y - s.y
        denom = a * dx + b * dy
        if abs(denom) <= EPS:
            return e
        t = (c - a * s.x - b * s.y) / denom
        return Point(s.x + t * dx, s.y + t * dy)

    out: List[Point] = []
    s = poly[-1]
    for e in poly:
        if inside(e):
            if not inside(s):
                out.append(intersection(s, e))
            out.append(e)
        elif inside(s):
            out.append(intersection(s, e))
        s = e
    return out


def _cell_from_neighbors(site: Point, neighbors: Set[Point], bbox: BBox) -> List[Point]:
    """
    Build bounded Voronoi cell by intersecting bbox with half-planes
    defined by perpendicular bisectors between site and each neighbor.
    Uses Delaunay neighbors (dual graph) and yields bounded cells.
    """
    poly = bbox.rect()

    for q in neighbors:
        # closer to site than q:
        # 2*(q-s)·x <= |q|^2 - |s|^2
        a = 2.0 * (q.x - site.x)
        b = 2.0 * (q.y - site.y)
        c = (q.x * q.x + q.y * q.y) - (site.x * site.x + site.y * site.y)
        poly = _clip_polygon_by_halfplane(poly, a, b, c)
        if not poly:
            return []

    poly = clip_polygon_to_bbox(poly, bbox)

    if len(poly) >= 3:
        cx = sum(p.x for p in poly) / len(poly)
        cy = sum(p.y for p in poly) / len(poly)
        poly = sorted(poly, key=lambda p: atan2(p.y - cy, p.x - cx))
    return poly


def build_voronoi_from_delaunay(
    points: List[Point],
    delaunay_triangles: List[Triangle],
    neighbors: Dict[Point, Set[Point]],
    bbox: BBox,
) -> VoronoiDiagram:
    circumcenters: List[Point] = []
    for t in delaunay_triangles:
        try:
            circumcenters.append(circumcenter(t))
        except ValueError:
            continue

    cells: Dict[Point, List[Point]] = {}
    for p in points:
        cells[p] = _cell_from_neighbors(p, neighbors.get(p, set()), bbox)

    return VoronoiDiagram(cells=cells, circumcenters=circumcenters, delaunay_triangles=delaunay_triangles)
