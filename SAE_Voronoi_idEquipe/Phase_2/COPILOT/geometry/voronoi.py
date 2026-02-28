from typing import Dict, List, Tuple
import math

from .utils import (
    circumcenter,
    bounding_box,
    expand_bbox,
    clip_polygon_to_bbox
)

Point = Tuple[float, float]
TriangleIndices = Tuple[int, int, int]


def build_voronoi_diagram(
    points: List[Point],
    triangles: List[TriangleIndices],
    super_indices: Tuple[int, int, int],
):
    """
    Version B : Voronoï simple et stable.
    - Chaque cellule est construite à partir des centres des triangles incident au point.
    - On ajoute explicitement le point lui-même dans le polygone.
    - On clippe le résultat dans un rectangle englobant élargi.
    - Résultat : chaque point est bien englobé dans sa cellule, rendu propre et lisible.
    """

    n_points = len(points)
    super_set = set(super_indices)

    # --- 1. Calcul des centres des cercles circonscrits ---
    triangle_circumcenters: List[Point] = []
    for (i, j, k) in triangles:
        a, b, c = points[i], points[j], points[k]
        center = circumcenter(a, b, c)
        triangle_circumcenters.append(center)

    # --- 2. Triangles incident à chaque point ---
    point_to_triangles: Dict[int, List[int]] = {i: [] for i in range(n_points)}
    for t_idx, (i, j, k) in enumerate(triangles):
        point_to_triangles[i].append(t_idx)
        point_to_triangles[j].append(t_idx)
        point_to_triangles[k].append(t_idx)

    # --- 3. Bbox réel (sans super-triangle) ---
    real_points = [p for idx, p in enumerate(points) if idx not in super_set]
    bbox = bounding_box(real_points)
    bbox_expanded = expand_bbox(bbox, margin_ratio=0.15)

    voronoi_cells: Dict[int, List[Point]] = {}

    # --- 4. Construction des cellules ---
    for p_idx in range(n_points):
        if p_idx in super_set:
            continue  # pas de cellule pour les sommets du super-triangle

        tri_indices = point_to_triangles[p_idx]
        if not tri_indices:
            voronoi_cells[p_idx] = []
            continue

        px, py = points[p_idx]

        # Centres des triangles incident à ce point
        centers = [triangle_circumcenters[t_idx] for t_idx in tri_indices]

        # --- Ajout du point lui-même ---
        # Cela garantit que la cellule englobe bien le point.
        raw_poly = centers + [points[p_idx]]

        # Tri angulaire autour du point
        centers_sorted = sorted(
            raw_poly,
            key=lambda c: math.atan2(c[1] - py, c[0] - px),
        )

        # Clip du polygone au rectangle englobant
        clipped = clip_polygon_to_bbox(centers_sorted, bbox_expanded)
        voronoi_cells[p_idx] = clipped

    return voronoi_cells, bbox_expanded
