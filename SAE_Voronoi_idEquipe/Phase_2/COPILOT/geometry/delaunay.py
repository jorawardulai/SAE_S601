"""
Triangulation de Delaunay 2D via l'algorithme de Watson (insertion incrémentale).

Étapes principales :
- Construction d'un super-triangle englobant tous les points.
- Insertion des points un par un :
    - Recherche des triangles dont le cercle circonscrit contient le point (cavity).
    - Suppression de ces triangles.
    - Construction du polygone frontière de la cavité (edges uniques).
    - Création de nouveaux triangles reliant le point aux arêtes de la cavité.
- Suppression des triangles qui utilisent les sommets du super-triangle.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Set

from .utils import compute_bounding_box, circumcircle, point_in_circumcircle

Point = Tuple[float, float]


@dataclass
class Triangle:
    vertices: Tuple[int, int, int]
    circumcenter: Point
    radius_sq: float


def _build_super_triangle(points: List[Point]) -> Tuple[Point, Point, Point]:
    """
    Construit un super-triangle englobant tous les points.
    On prend un grand triangle équilatéral couvrant la bounding box.
    """
    min_x, min_y, max_x, max_y = compute_bounding_box(points)
    dx = max_x - min_x
    dy = max_y - min_y
    delta = max(dx, dy)
    if delta == 0:
        delta = 1.0

    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0

    # Triangle très grand autour du centre
    p1 = (cx - 2 * delta, cy - delta)
    p2 = (cx, cy + 2 * delta)
    p3 = (cx + 2 * delta, cy - delta)
    return p1, p2, p3


def compute_delaunay_triangulation(points: List[Point]) -> List[Triangle]:
    """
    Calcule la triangulation de Delaunay d'une liste de points 2D
    en utilisant l'algorithme de Watson (insertion incrémentale).
    Retourne une liste de Triangle (indices par rapport à la liste de points d'origine).
    """
    if len(points) < 3:
        return []

    # Copie des points pour pouvoir ajouter les sommets du super-triangle
    pts = list(points)

    # Construction du super-triangle
    st_p1, st_p2, st_p3 = _build_super_triangle(pts)
    idx_st1 = len(pts)
    idx_st2 = len(pts) + 1
    idx_st3 = len(pts) + 2
    pts.extend([st_p1, st_p2, st_p3])

    # Triangles initiaux : le super-triangle
    cx, cy, r2 = circumcircle(st_p1, st_p2, st_p3)
    triangles: List[Triangle] = [
        Triangle(vertices=(idx_st1, idx_st2, idx_st3),
                 circumcenter=(cx, cy),
                 radius_sq=r2)
    ]

    # Insertion incrémentale des points originaux
    for idx_p, p in enumerate(points):
        bad_triangles: List[int] = []

        # 1. Trouver les triangles dont le cercle circonscrit contient le point
        for t_idx, tri in enumerate(triangles):
            if point_in_circumcircle(p, tri.circumcenter, tri.radius_sq):
                bad_triangles.append(t_idx)

        if not bad_triangles:
            # Aucun triangle ne contient ce point (cas rare), on ignore
            continue

        # 2. Récupérer les arêtes de la cavité
        # Chaque arête est un tuple (i, j) avec i < j pour normaliser
        edge_count: Dict[Tuple[int, int], int] = {}

        for t_idx in bad_triangles:
            tri = triangles[t_idx]
            v = tri.vertices
            edges = [(v[0], v[1]), (v[1], v[2]), (v[2], v[0])]
            for (a, b) in edges:
                if a > b:
                    a, b = b, a
                edge = (a, b)
                edge_count[edge] = edge_count.get(edge, 0) + 1

        # Les arêtes frontières sont celles qui apparaissent exactement une fois
        boundary_edges = [e for e, c in edge_count.items() if c == 1]

        # 3. Supprimer les triangles "mauvais"
        bad_triangles_set: Set[int] = set(bad_triangles)
        triangles = [tri for i, tri in enumerate(triangles) if i not in bad_triangles_set]

        # 4. Créer de nouveaux triangles reliant le point aux arêtes frontières
        for (a, b) in boundary_edges:
            cx, cy, r2 = circumcircle(pts[a], pts[b], p)
            new_tri = Triangle(
                vertices=(a, b, idx_p),
                circumcenter=(cx, cy),
                radius_sq=r2,
            )
            triangles.append(new_tri)

    # 5. Supprimer les triangles qui contiennent un sommet du super-triangle
    super_indices = {idx_st1, idx_st2, idx_st3}
    final_triangles: List[Triangle] = []
    for tri in triangles:
        if any(v in super_indices for v in tri.vertices):
            continue
        final_triangles.append(tri)

    return final_triangles
