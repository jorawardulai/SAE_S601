from app.domain.delaunay import bowyer_watson
from app.domain.geometry import Point, in_circumcircle


def test_delaunay_three_points_one_triangle():
    pts = [Point(0, 0), Point(1, 0), Point(0, 1)]
    res = bowyer_watson(pts)
    assert len(res.triangles) == 1
    assert len(res.neighbors[pts[0]]) == 2


def test_delaunay_square_four_points_two_triangles():
    pts = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    res = bowyer_watson(pts)
    assert len(res.triangles) == 2
    for t in res.triangles:
        for p in pts:
            if p not in t.vertices():
                assert in_circumcircle(t, p) is False
