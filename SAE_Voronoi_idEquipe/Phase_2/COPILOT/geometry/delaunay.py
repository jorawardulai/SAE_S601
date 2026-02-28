from dataclasses import dataclass
from typing import List, Tuple

from .utils import is_point_in_circumcircle, circumcenter, bounding_box

Point = Tuple[float, float]


@dataclass
class Triangle:
    """Triangle défini par les indices de trois points dans la liste globale."""
    i: int
    j: int
    k: int


def create_super_triangle(points: List[Point]) -> Tuple[Point, Point, Point]:
    """
    Crée un super-triangle englobant tous les points.

    On prend un grand triangle équilatéral couvrant largement le bounding box.
    """
    min_x, max_x, min_y, max_y = bounding_box(points)
    dx = max_x - min_x
    dy = max_y - min_y
    delta_max = max(dx, dy)
    if delta_max == 0:
        delta_max = 1.0

    mid_x = (min_x + max_x) / 2.0
    mid_y = (min_y + max_y) / 2.0

    # Triangle très large
    p1 = (mid_x - 20 * delta_max, mid_y - delta_max)
    p2 = (mid_x, mid_y + 20 * delta_max)
    p3 = (mid_x + 20 * delta_max, mid_y - delta_max)

    return p1, p2, p3


def compute_delaunay_triangulation(points: List[Point]):
    """
    Implémente l'algorithme de Watson (insertion incrémentale) pour la
    triangulation de Delaunay.

    Étapes :
    - Construire un super-triangle englobant tous les points.
    - Ajouter ce triangle à la triangulation.
    - Insérer les points un par un :
        * Trouver les triangles dont le cercle circonscrit contient le point.
        * Supprimer ces triangles (cavity).
        * Construire le polygone frontière de la cavité.
        * Relier le nouveau point à chaque arête de la frontière.
    - Retirer les triangles qui utilisent les sommets du super-triangle.
    """
    if len(points) < 3:
        raise ValueError("Au moins 3 points sont nécessaires pour Delaunay.")

    # Copie locale des points
    pts = list(points)

    # Ajout des sommets du super-triangle à la fin
    super_a, super_b, super_c = create_super_triangle(pts)
    idx_a = len(pts)
    idx_b = len(pts) + 1
    idx_c = len(pts) + 2
    pts.extend([super_a, super_b, super_c])

    triangles: List[Triangle] = [Triangle(idx_a, idx_b, idx_c)]

    # Insertion incrémentale des points originaux
    for p_idx in range(len(points)):
        p = pts[p_idx]

        bad_triangles = []
        for t in triangles:
            a, b, c = pts[t.i], pts[t.j], pts[t.k]
            if is_point_in_circumcircle(p, a, b, c):
                bad_triangles.append(t)

        # Construction de la frontière (liste d'arêtes)
        # Une arête est frontière si elle n'est partagée que par un seul triangle "bad".
        edges = []
        for t in bad_triangles:
            tri_edges = [(t.i, t.j), (t.j, t.k), (t.k, t.i)]
            for e in tri_edges:
                if (e[1], e[0]) in edges:
                    edges.remove((e[1], e[0]))
                else:
                    edges.append(e)

        # Retirer les triangles "bad"
        triangles = [t for t in triangles if t not in bad_triangles]

        # Créer de nouveaux triangles en reliant p_idx à chaque arête de la frontière
        for (i, j) in edges:
            triangles.append(Triangle(i, j, p_idx))

    # Retirer les triangles qui contiennent un sommet du super-triangle
    def uses_super_vertex(t: Triangle) -> bool:
        return (
            t.i in (idx_a, idx_b, idx_c)
            or t.j in (idx_a, idx_b, idx_c)
            or t.k in (idx_a, idx_b, idx_c)
        )

    triangles = [t for t in triangles if not uses_super_vertex(t)]

    # On renvoie les triangles sous forme de tuples d'indices, et les indices du super-triangle
    triangle_indices = [(t.i, t.j, t.k) for t in triangles]
    super_indices = (idx_a, idx_b, idx_c)

    return triangle_indices, super_indices
