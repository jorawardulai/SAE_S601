"""
Construction du diagramme de Voronoï à partir d'une triangulation de Delaunay.

Version simple et robuste :
- On utilise la triangulation de Delaunay pour obtenir, pour chaque point,
  la liste de ses voisins (points reliés par une arête de Delaunay).
- Pour chaque point P, on construit sa cellule de Voronoï comme
  l'intersection de demi-plans :
      { x | dist(x, P) <= dist(x, Q) } pour chaque voisin Q
  le tout intersecté avec un grand rectangle englobant (bounding box élargie).

Cela produit des cellules fermées (même pour les points sur le bord),
clippées dans un rectangle, ce qui donne un rendu propre et stable.
"""

from typing import List, Tuple, Dict, Set
from collections import defaultdict

from .delaunay import Triangle, Point
from .utils import compute_bounding_box


def _build_point_neighbors(triangles: List[Triangle]) -> Dict[int, Set[int]]:
    """
    Construit, pour chaque point, l'ensemble de ses voisins dans la triangulation
    de Delaunay (points reliés par une arête).
    """
    neighbors: Dict[int, Set[int]] = defaultdict(set)
    for tri in triangles:
        a, b, c = tri.vertices
        neighbors[a].add(b)
        neighbors[a].add(c)
        neighbors[b].add(a)
        neighbors[b].add(c)
        neighbors[c].add(a)
        neighbors[c].add(b)
    return neighbors


def _clip_polygon_with_halfplane(
    polygon: List[Point],
    p: Point,
    q: Point,
) -> List[Point]:
    """
    Clippe un polygone convexe par le demi-plan :
        { x | dist(x, p) <= dist(x, q) }

    En pratique, on utilise la forme linéaire :
        x · (q - p) <= (||q||² - ||p||²) / 2

    On applique un algorithme de type Sutherland–Hodgman pour ce demi-plan.
    """
    if not polygon:
        return []

    px, py = p
    qx, qy = q
    vx = qx - px
    vy = qy - py
    c = (qx * qx + qy * qy - px * px - py * py) / 2.0

    def inside(pt: Point) -> bool:
        x, y = pt
        return x * vx + y * vy <= c + 1e-12

    def intersect(p1: Point, p2: Point) -> Point:
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        denom = dx * vx + dy * vy
        if abs(denom) < 1e-18:
            # Segment presque parallèle à la frontière : on renvoie un point arbitraire
            return p1
        t = (c - (x1 * vx + y1 * vy)) / denom
        return (x1 + t * dx, y1 + t * dy)

    res: List[Point] = []
    prev = polygon[-1]
    prev_inside = inside(prev)

    for curr in polygon:
        curr_inside = inside(curr)
        if curr_inside:
            if not prev_inside:
                res.append(intersect(prev, curr))
            res.append(curr)
        elif prev_inside:
            res.append(intersect(prev, curr))
        prev, prev_inside = curr, curr_inside

    return res


def build_voronoi_cells(
    points: List[Point],
    triangles: List[Triangle],
) -> Dict[int, List[Point]]:
    """
    Construit les cellules de Voronoï à partir d'une triangulation de Delaunay.

    Pour chaque point i :
        - On part d'un grand rectangle englobant (bounding box élargie).
        - On intersecte ce rectangle avec les demi-plans "plus proche de i que de j"
          pour tous les voisins j de i dans la triangulation.
        - Le résultat est un polygone convexe : la cellule de Voronoï de i,
          clippée dans la bounding box.

    Retourne :
        dict : point_index -> liste de sommets (points 2D) de la cellule.
    """
    if not triangles or not points:
        return {}

    # Bounding box élargie pour fermer les cellules infinies
    min_x, min_y, max_x, max_y = compute_bounding_box(points)
    dx = max_x - min_x
    dy = max_y - min_y
    delta = max(dx, dy)
    if delta == 0:
        delta = 1.0
    margin = delta * 0.5

    bbox_min_x = min_x - margin
    bbox_min_y = min_y - margin
    bbox_max_x = max_x + margin
    bbox_max_y = max_y + margin

    # Polygone initial : le rectangle englobant
    bbox_polygon: List[Point] = [
        (bbox_min_x, bbox_min_y),
        (bbox_max_x, bbox_min_y),
        (bbox_max_x, bbox_max_y),
        (bbox_min_x, bbox_max_y),
    ]

    # Voisins par point via la triangulation
    neighbors = _build_point_neighbors(triangles)

    voronoi_cells: Dict[int, List[Point]] = {}

    for i, p in enumerate(points):
        if i not in neighbors or not neighbors[i]:
            # Pas de voisins (cas très pathologique) : on ignore
            continue

        poly = bbox_polygon[:]
        for j in neighbors[i]:
            q = points[j]
            poly = _clip_polygon_with_halfplane(poly, p, q)
            if len(poly) < 3:
                # Cellule dégénérée : on arrête
                poly = []
                break

        if len(poly) >= 3:
            voronoi_cells[i] = poly

    return voronoi_cells
