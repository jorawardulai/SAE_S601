"""
Construction du diagramme de Voronoï à partir de la triangulation de Delaunay.

Stratégie :
  - Points intérieurs  : cellule = polygone des circumcentres adjacents.
  - Points sur le hull : cellule non-bornée → rayons infinis clippés sur la bbox.
"""

import math

from geometry.primitives import EPS, pts_equal, edge_equal
from geometry.triangle import Triangle
from algorithms.clipping import sutherland_hodgman


def compute_voronoi(
    points: list[tuple],
    triangles: list[Triangle],
    bbox: tuple,
) -> dict[int, list[tuple]]:
    """
    Calcule les cellules de Voronoï clippées sur une bounding-box.

    Args:
        points   : liste des sites générateurs (x, y).
        triangles: triangulation de Delaunay des points.
        bbox     : (xmin, xmax, ymin, ymax) — rectangle de clipping.

    Returns:
        Dictionnaire {index_point: [sommets du polygone de cellule]}.
        Chaque polygone est ordonné angulairement autour du site.
    """
    xmin, xmax, ymin, ymax = bbox
    far = math.sqrt((xmax - xmin) ** 2 + (ymax - ymin) ** 2) * 10.0

    adj = _build_adjacency(points, triangles)
    hull_edges = _find_hull_edges(triangles)
    centroid = _centroid(points)

    cells: dict[int, list[tuple]] = {}

    for i, site in enumerate(points):
        cell = _build_cell(
            site, adj[i], hull_edges, centroid, far,
            xmin, xmax, ymin, ymax,
        )
        if cell is not None:
            cells[i] = cell

    return cells


# ── Helpers privés ────────────────────────────────────────────────────────────

def _build_adjacency(
    points: list[tuple],
    triangles: list[Triangle],
) -> dict[int, list[Triangle]]:
    """Construit le mapping index_point → liste des triangles adjacents."""
    adj: dict[int, list[Triangle]] = {i: [] for i in range(len(points))}

    for tri in triangles:
        for i, p in enumerate(points):
            for v in (tri.a, tri.b, tri.c):
                if pts_equal(v, p):
                    adj[i].append(tri)
                    break

    return adj


def _find_hull_edges(triangles: list[Triangle]) -> list[tuple]:
    """
    Retourne les arêtes de l'enveloppe convexe : arêtes qui n'appartiennent
    qu'à un seul triangle dans la triangulation.
    """
    all_edges = [(e, tri) for tri in triangles for e in tri.edges()]

    hull = []
    for idx, (e1, t1) in enumerate(all_edges):
        is_hull = not any(
            j != idx and edge_equal(e1, e2)
            for j, (e2, _) in enumerate(all_edges)
        )
        if is_hull:
            hull.append((e1, t1))

    return hull


def _centroid(points: list[tuple]) -> tuple:
    """Retourne le centroïde du nuage de points."""
    n = len(points)
    return (
        sum(p[0] for p in points) / n,
        sum(p[1] for p in points) / n,
    )


def _outward_normal(edge: tuple, centroid: tuple) -> tuple:
    """
    Calcule la normale unitaire à une arête, orientée vers l'extérieur
    du nuage (opposée au centroïde).
    """
    ex = edge[1][0] - edge[0][0]
    ey = edge[1][1] - edge[0][1]

    n1 = (-ey,  ex)
    n2 = ( ey, -ex)

    mid_x = (edge[0][0] + edge[1][0]) / 2.0
    mid_y = (edge[0][1] + edge[1][1]) / 2.0

    cx, cy = centroid
    d1 = (mid_x + n1[0] - cx) ** 2 + (mid_y + n1[1] - cy) ** 2
    d2 = (mid_x + n2[0] - cx) ** 2 + (mid_y + n2[1] - cy) ** 2

    nx, ny = n1 if d1 > d2 else n2
    length = math.sqrt(nx * nx + ny * ny)

    if length < EPS:
        return (0.0, 0.0)
    return (nx / length, ny / length)


def _build_cell(
    site: tuple,
    adj_triangles: list[Triangle],
    hull_edges: list[tuple],
    centroid: tuple,
    far: float,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
) -> list[tuple] | None:
    """
    Construit et clippe la cellule de Voronoï d'un site.

    Retourne None si la cellule est invalide (moins de 3 sommets après clipping).
    """
    px, py = site

    # Circumcentres finis des triangles adjacents → sommets Voronoï
    finite_verts = [
        tri.circumcenter
        for tri in adj_triangles
        if not math.isinf(tri.circumcenter[0])
    ]

    if not finite_verts:
        return None

    # Rayons infinis pour les arêtes de bord adjacentes au site
    far_verts = _compute_far_vertices(site, hull_edges, centroid, far)

    # Trier tous les sommets par angle autour du site
    all_verts = finite_verts + far_verts
    all_verts.sort(key=lambda v: math.atan2(v[1] - py, v[0] - px))

    # Clipper sur la bbox
    clipped = sutherland_hodgman(all_verts, xmin, xmax, ymin, ymax)

    return clipped if len(clipped) >= 3 else None


def _compute_far_vertices(
    site: tuple,
    hull_edges: list[tuple],
    centroid: tuple,
    far: float,
) -> list[tuple]:
    """
    Pour un site sur l'enveloppe convexe, calcule les points lointains
    le long des rayons de Voronoï non-bornés.
    """
    far_verts = []

    for edge, tri in hull_edges:
        if not (pts_equal(edge[0], site) or pts_equal(edge[1], site)):
            continue

        cc = tri.circumcenter
        if math.isinf(cc[0]) or math.isinf(cc[1]):
            continue

        nx, ny = _outward_normal(edge, centroid)
        far_verts.append((cc[0] + nx * far, cc[1] + ny * far))

    return far_verts
