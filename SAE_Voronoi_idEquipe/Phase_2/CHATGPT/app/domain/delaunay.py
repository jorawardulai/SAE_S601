from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from .geometry import EPS, Edge, Point, Triangle, in_circumcircle, orientation, unique_points


@dataclass(frozen=True, slots=True)
class DelaunayResult:
    triangles: List[Triangle]
    neighbors: Dict[Point, Set[Point]]  # adjacency graph (Delaunay neighbors)


def _super_triangle(points: list[Point]) -> Triangle:
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    dx = maxx - minx
    dy = maxy - miny
    d = max(dx, dy)
    if d <= EPS:
        d = 1.0

    midx = (minx + maxx) / 2.0
    midy = (miny + maxy) / 2.0

    # Very large triangle around all points
    a = Point(midx - 20 * d, midy - 20 * d)
    b = Point(midx, midy + 20 * d)
    c = Point(midx + 20 * d, midy - 20 * d)
    return Triangle(a, b, c)


def bowyer_watson(points_in: Iterable[Point]) -> DelaunayResult:
    points = unique_points(list(points_in))
    if len(points) < 3:
        return DelaunayResult(triangles=[], neighbors={p: set() for p in points})

    st = _super_triangle(points)
    triangles: list[Triangle] = [st]

    for p in points:
        bad: list[Triangle] = [t for t in triangles if in_circumcircle(t, p)]

        # boundary edges = edges that appear only once among bad triangles
        edge_count: dict[Edge, int] = {}
        for t in bad:
            for e in t.edges():
                en = e.normalized()
                edge_count[en] = edge_count.get(en, 0) + 1

        boundary_edges = [e for e, c in edge_count.items() if c == 1]

        # remove bad triangles
        bad_set = set(bad)
        triangles = [t for t in triangles if t not in bad_set]

        # re-triangulate cavity
        for e in boundary_edges:
            if abs(orientation(e.a, e.b, p)) <= EPS:
                continue
            triangles.append(Triangle(e.a, e.b, p))

    # remove triangles touching super triangle vertices
    st_vertices = set(st.vertices())
    triangles = [t for t in triangles if not any(v in st_vertices for v in t.vertices())]

    # Build adjacency (neighbors) from triangles
    neighbors: Dict[Point, Set[Point]] = {p: set() for p in points}
    for t in triangles:
        a, b, c = t.vertices()
        if a in neighbors and b in neighbors:
            neighbors[a].add(b)
            neighbors[b].add(a)
        if b in neighbors and c in neighbors:
            neighbors[b].add(c)
            neighbors[c].add(b)
        if c in neighbors and a in neighbors:
            neighbors[c].add(a)
            neighbors[a].add(c)

    return DelaunayResult(triangles=triangles, neighbors=neighbors)
