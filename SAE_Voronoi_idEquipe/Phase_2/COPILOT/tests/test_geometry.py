import math

from geometry.utils import circumcenter, is_point_in_circumcircle
from geometry.delaunay import compute_delaunay_triangulation
from geometry.voronoi import build_voronoi_diagram


def test_circumcenter_right_triangle():
    # Triangle rectangle en (0,0), (1,0), (0,1)
    a = (0.0, 0.0)
    b = (1.0, 0.0)
    c = (0.0, 1.0)
    center = circumcenter(a, b, c)
    # Le centre doit être (0.5, 0.5)
    assert math.isclose(center[0], 0.5, rel_tol=1e-6, abs_tol=1e-6)
    assert math.isclose(center[1], 0.5, rel_tol=1e-6, abs_tol=1e-6)


def test_point_in_circumcircle():
    a = (0.0, 0.0)
    b = (1.0, 0.0)
    c = (0.0, 1.0)
    p_inside = (0.2, 0.2)
    p_outside = (2.0, 2.0)

    assert is_point_in_circumcircle(p_inside, a, b, c)
    assert not is_point_in_circumcircle(p_outside, a, b, c)


def test_delaunay_and_voronoi_basic():
    # Carré simple
    points = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]
    triangles, super_indices = compute_delaunay_triangulation(points)
    # On doit avoir au moins 2 triangles pour un carré
    assert len(triangles) >= 2

    voronoi_cells, bbox = build_voronoi_diagram(points + [None, None, None], triangles, super_indices)
    # On doit avoir une cellule pour chaque point réel
    real_indices = [i for i in range(len(points))]
    for idx in real_indices:
        assert idx in voronoi_cells
        assert isinstance(voronoi_cells[idx], list)
