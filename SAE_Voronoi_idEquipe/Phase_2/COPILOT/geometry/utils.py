from typing import Tuple
import math

Point = Tuple[float, float]


def orientation(a: Point, b: Point, c: Point) -> float:
    """
    Orientation signée du triplet (a, b, c).
    > 0 : orientation anti-horaire
    < 0 : orientation horaire
    = 0 : colinéaire
    """
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def circumcenter(a: Point, b: Point, c: Point) -> Point:
    """
    Calcule le centre du cercle circonscrit au triangle (a, b, c).

    Formule basée sur l'intersection des médiatrices.
    On suppose que les points ne sont pas colinéaires.
    """
    d = 2 * (a[0] * (b[1] - c[1]) +
             b[0] * (c[1] - a[1]) +
             c[0] * (a[1] - b[1]))
    if abs(d) < 1e-12:
        # Triangle quasi-dégénéré : on renvoie un centre approximatif (moyenne)
        return ((a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0)

    ux = (
        (a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) +
        (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) +
        (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])
    ) / d

    uy = (
        (a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) +
        (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) +
        (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])
    ) / d

    return (ux, uy)


def squared_distance(p: Point, q: Point) -> float:
    """Distance au carré entre deux points."""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def is_point_in_circumcircle(p: Point, a: Point, b: Point, c: Point) -> bool:
    """
    Teste si le point p est strictement à l'intérieur du cercle circonscrit
    au triangle (a, b, c).

    Utilise le déterminant orienté classique pour Delaunay.
    """
    # On s'assure que (a, b, c) est en orientation anti-horaire
    if orientation(a, b, c) < 0:
        b, c = c, b

    ax, ay = a[0] - p[0], a[1] - p[1]
    bx, by = b[0] - p[0], b[1] - p[1]
    cx, cy = c[0] - p[0], c[1] - p[1]

    det = (
        (ax * ax + ay * ay) * (bx * cy - cx * by)
        - (bx * bx + by * by) * (ax * cy - cx * ay)
        + (cx * cx + cy * cy) * (ax * by - bx * ay)
    )

    return det > 1e-12


def bounding_box(points):
    """Retourne (min_x, max_x, min_y, max_y) pour une liste de points."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def expand_bbox(bbox, margin_ratio=0.1):
    """
    Agrandit un rectangle englobant de margin_ratio (10% par défaut)
    pour gérer les bords du Voronoï.
    """
    min_x, max_x, min_y, max_y = bbox
    width = max_x - min_x
    height = max_y - min_y
    if width == 0:
        width = 1.0
    if height == 0:
        height = 1.0
    dx = width * margin_ratio
    dy = height * margin_ratio
    return min_x - dx, max_x + dx, min_y - dy, max_y + dy


def clip_polygon_to_bbox(polygon, bbox):
    """
    Clippe un polygone convexe à un rectangle englobant via Sutherland-Hodgman.

    polygon : liste de points (x, y)
    bbox    : (min_x, max_x, min_y, max_y)
    """
    min_x, max_x, min_y, max_y = bbox

    def clip_edge(points, inside, intersect):
        if not points:
            return []
        output = []
        prev = points[-1]
        prev_inside = inside(prev)
        for curr in points:
            curr_inside = inside(curr)
            if curr_inside:
                if not prev_inside:
                    output.append(intersect(prev, curr))
                output.append(curr)
            elif prev_inside:
                output.append(intersect(prev, curr))
            prev, prev_inside = curr, curr_inside
        return output

    # Clip gauche
    polygon = clip_edge(
        polygon,
        inside=lambda p: p[0] >= min_x,
        intersect=lambda p1, p2: (
            min_x,
            p1[1] + (p2[1] - p1[1]) * (min_x - p1[0]) / (p2[0] - p1[0]),
        ),
    )
    # Clip droite
    polygon = clip_edge(
        polygon,
        inside=lambda p: p[0] <= max_x,
        intersect=lambda p1, p2: (
            max_x,
            p1[1] + (p2[1] - p1[1]) * (max_x - p1[0]) / (p2[0] - p1[0]),
        ),
    )
    # Clip bas
    polygon = clip_edge(
        polygon,
        inside=lambda p: p[1] >= min_y,
        intersect=lambda p1, p2: (
            p1[0] + (p2[0] - p1[0]) * (min_y - p1[1]) / (p2[1] - p1[1]),
            min_y,
        ),
    )
    # Clip haut
    polygon = clip_edge(
        polygon,
        inside=lambda p: p[1] <= max_y,
        intersect=lambda p1, p2: (
            p1[0] + (p2[0] - p1[0]) * (max_y - p1[1]) / (p2[1] - p1[1]),
            max_y,
        ),
    )

    return polygon
