"""
Primitives géométriques de base.
"""

EPS = 1e-9


def pts_equal(a: tuple, b: tuple) -> bool:
    """Retourne True si deux points sont égaux à EPS près."""
    return abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) < EPS


def edge_equal(e1: tuple, e2: tuple) -> bool:
    """Retourne True si deux arêtes non-orientées sont identiques."""
    return (
        (pts_equal(e1[0], e2[0]) and pts_equal(e1[1], e2[1])) or
        (pts_equal(e1[0], e2[1]) and pts_equal(e1[1], e2[0]))
    )
