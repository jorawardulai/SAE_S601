"""
Algorithme de clipping de Sutherland-Hodgman.

Clippe un polygone quelconque sur un rectangle axe-aligné.
"""

from geometry.primitives import EPS


def _clip_half_plane(
    polygon: list[tuple],
    inside_fn,
    intersect_fn,
) -> list[tuple]:
    """Étape générique : garde la partie du polygone du côté 'inside'."""
    if not polygon:
        return []

    output = []
    n = len(polygon)

    for idx in range(n):
        cur = polygon[idx]
        prev = polygon[(idx - 1) % n]

        if inside_fn(cur):
            if not inside_fn(prev):
                output.append(intersect_fn(prev, cur))
            output.append(cur)
        elif inside_fn(prev):
            output.append(intersect_fn(prev, cur))

    return output


def _intersect_vertical(p1: tuple, p2: tuple, x: float) -> tuple:
    """Intersection du segment [p1,p2] avec la droite verticale x=x."""
    dx = p2[0] - p1[0]
    if abs(dx) < EPS:
        return (x, p1[1])
    t = (x - p1[0]) / dx
    return (x, p1[1] + t * (p2[1] - p1[1]))


def _intersect_horizontal(p1: tuple, p2: tuple, y: float) -> tuple:
    """Intersection du segment [p1,p2] avec la droite horizontale y=y."""
    dy = p2[1] - p1[1]
    if abs(dy) < EPS:
        return (p1[0], y)
    t = (y - p1[1]) / dy
    return (p1[0] + t * (p2[0] - p1[0]), y)


def sutherland_hodgman(
    polygon: list[tuple],
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
) -> list[tuple]:
    """
    Clippe un polygone sur un rectangle [xmin, xmax] × [ymin, ymax].

    Args:
        polygon: liste de sommets (x, y).
        xmin, xmax, ymin, ymax: bornes du rectangle de clipping.

    Returns:
        Liste des sommets du polygone clippé (peut être vide).
    """
    poly = polygon[:]

    poly = _clip_half_plane(poly,
                            lambda p: p[0] >= xmin,
                            lambda a, b: _intersect_vertical(a, b, xmin))
    poly = _clip_half_plane(poly,
                            lambda p: p[0] <= xmax,
                            lambda a, b: _intersect_vertical(a, b, xmax))
    poly = _clip_half_plane(poly,
                            lambda p: p[1] >= ymin,
                            lambda a, b: _intersect_horizontal(a, b, ymin))
    poly = _clip_half_plane(poly,
                            lambda p: p[1] <= ymax,
                            lambda a, b: _intersect_horizontal(a, b, ymax))
    return poly
