"""
Tests unitaires simples pour les fonctions géométriques critiques.

Pour exécuter les tests :
    python -m pytest tests/test_geometry.py
"""

import math

from geometry.utils import circumcircle, point_in_circumcircle
from geometry.delaunay import compute_delaunay_triangulation


def test_circumcircle_equilateral():
    # Triangle équilatéral de côté 2, centré approximativement
    p1 = (0.0, 0.0)
    p2 = (2.0, 0.0)
    p3 = (1.0, math.sqrt(3.0))
    cx, cy, r2 = circumcircle(p1, p2, p3)

    # Centre attendu : (1, sqrt(3)/3)
    assert abs(cx - 1.0) < 1e-6
    assert abs(cy - (math.sqrt(3.0) / 3.0)) < 1e-6

    # Rayon attendu : 2 / sqrt(3)
    r_expected = 2.0 / math.sqrt(3.0)
    assert abs(math.sqrt(r2) - r_expected) < 1e-6


def test_point_in_circumcircle():
    p1 = (0.0, 0.0)
    p2 = (2.0, 0.0)
    p3 = (1.0, math.sqrt(3.0))
    cx, cy, r2 = circumcircle(p1, p2, p3)

    inside_point = (1.0, 0.5)
    outside_point = (3.0, 3.0)

    assert point_in_circumcircle(inside_point, (cx, cy), r2)
    assert not point_in_circumcircle(outside_point, (cx, cy), r2)


def test_delaunay_simple_square():
    # Carré : 4 points
    points = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]
    tris = compute_delaunay_triangulation(points)
    # On s'attend à 2 triangles
    assert len(tris) == 2
    # Les triangles doivent couvrir les 4 points
    used_vertices = set()
    for t in tris:
        used_vertices.update(t.vertices)
    assert used_vertices == {0, 1, 2, 3}
