"""
Triangulation de Delaunay par l'algorithme incrémental de Bowyer-Watson.

Complexité : O(n²) en moyenne, O(n³) dans le pire cas.
Référence   : Bowyer (1981), Watson (1981).
"""

from geometry.primitives import edge_equal
from geometry.triangle import Triangle


def bowyer_watson(points: list[tuple]) -> list[Triangle]:
    """
    Calcule la triangulation de Delaunay d'un ensemble de points 2D.

    Principe :
      1. Initialiser avec un super-triangle englobant tous les points.
      2. Pour chaque point :
         a. Trouver les triangles dont le cercle circonscrit contient le point.
         b. Identifier le polygone frontalier (arêtes non partagées).
         c. Supprimer les mauvais triangles et retrianguler le trou.
      3. Supprimer les triangles contenant les sommets du super-triangle.

    Args:
        points: liste de tuples (x, y). Doit contenir au moins 3 points.

    Returns:
        Liste de Triangle formant la triangulation de Delaunay.
        Retourne [] si moins de 3 points.
    """
    if len(points) < 3:
        return []

    super_triangle = _build_super_triangle(points)
    triangulation = [super_triangle]
    super_verts = (super_triangle.a, super_triangle.b, super_triangle.c)

    for point in points:
        bad_triangles = _find_bad_triangles(point, triangulation)
        boundary = _find_boundary(bad_triangles)

        for tri in bad_triangles:
            triangulation.remove(tri)

        for edge in boundary:
            triangulation.append(Triangle(edge[0], edge[1], point))

    return [t for t in triangulation if not t.has_supervertex(super_verts)]


# ── Helpers privés ────────────────────────────────────────────────────────────

def _build_super_triangle(points: list[tuple]) -> Triangle:
    """Construit un super-triangle englobant largement tous les points."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    mn_x, mx_x = min(xs), max(xs)
    mn_y, mx_y = min(ys), max(ys)

    dx = mx_x - mn_x or 1.0
    dy = mx_y - mn_y or 1.0
    delta = max(dx, dy) * 20.0

    mid_x = (mn_x + mx_x) / 2.0
    mid_y = (mn_y + mx_y) / 2.0

    S1 = (mid_x - 2.0 * delta, mid_y - delta)
    S2 = (mid_x,                mid_y + 2.0 * delta)
    S3 = (mid_x + 2.0 * delta,  mid_y - delta)

    return Triangle(S1, S2, S3)


def _find_bad_triangles(
    point: tuple,
    triangulation: list[Triangle],
) -> list[Triangle]:
    """Retourne les triangles dont le cercle circonscrit contient le point."""
    return [t for t in triangulation if t.in_circumcircle(point)]


def _find_boundary(bad_triangles: list[Triangle]) -> list[tuple]:
    """
    Retourne les arêtes frontières du trou polygonal formé par les
    mauvais triangles (arêtes n'appartenant qu'à un seul mauvais triangle).
    """
    boundary = []

    for tri in bad_triangles:
        for edge in tri.edges():
            is_shared = any(
                edge_equal(edge, other_edge)
                for other in bad_triangles
                if other is not tri
                for other_edge in other.edges()
            )
            if not is_shared:
                boundary.append(edge)

    return boundary
