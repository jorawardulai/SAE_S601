from typing import Tuple, List

Point = Tuple[float, float]


def compute_bounding_box(points: List[Point]) -> Tuple[float, float, float, float]:
    """Retourne (min_x, min_y, max_x, max_y) pour une liste de points."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def circumcircle(p1: Point, p2: Point, p3: Point):
    """
    Calcule le cercle circonscrit au triangle (p1, p2, p3).
    Retourne (centre_x, centre_y, rayon_carré).

    Si les points sont colinéaires, retourne un cercle très grand
    (centre moyen, rayon énorme) pour éviter les problèmes numériques.
    """
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3

    # Formule classique basée sur les déterminants
    d = 2 * (
        x1 * (y2 - y3)
        + x2 * (y3 - y1)
        + x3 * (y1 - y2)
    )

    if abs(d) < 1e-12:
        # Points quasi colinéaires : on renvoie un cercle "infini"
        cx = (x1 + x2 + x3) / 3.0
        cy = (y1 + y2 + y3) / 3.0
        r2 = 1e30
        return cx, cy, r2

    ux = (
        (x1**2 + y1**2) * (y2 - y3)
        + (x2**2 + y2**2) * (y3 - y1)
        + (x3**2 + y3**2) * (y1 - y2)
    ) / d

    uy = (
        (x1**2 + y1**2) * (x3 - x2)
        + (x2**2 + y2**2) * (x1 - x3)
        + (x3**2 + y3**2) * (x2 - x1)
    ) / d

    r2 = (ux - x1) ** 2 + (uy - y1) ** 2
    return ux, uy, r2


def point_in_circumcircle(point: Point, center: Point, radius_sq: float) -> bool:
    """
    Teste si un point est strictement à l'intérieur du cercle circonscrit.
    On autorise une petite marge pour les erreurs numériques.
    """
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    dist_sq = dx * dx + dy * dy
    return dist_sq <= radius_sq * (1 + 1e-12)
