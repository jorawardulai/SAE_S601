import pytest

from app.domain.geometry import Point, Triangle, circumcenter, in_circumcircle, orientation, unique_points


def test_orientation_sign():
    a = Point(0, 0)
    b = Point(1, 0)
    c = Point(0, 1)
    assert orientation(a, b, c) > 0
    assert orientation(a, c, b) < 0


def test_circumcenter_right_triangle():
    t = Triangle(Point(0, 0), Point(2, 0), Point(0, 2))
    cc = circumcenter(t)
    assert abs(cc.x - 1.0) < 1e-9
    assert abs(cc.y - 1.0) < 1e-9


def test_in_circumcircle_basic():
    t = Triangle(Point(0, 0), Point(2, 0), Point(0, 2))
    inside = Point(1, 0.5)
    outside = Point(3, 3)
    assert in_circumcircle(t, inside) is True
    assert in_circumcircle(t, outside) is False


def test_unique_points_removes_duplicates():
    pts = [Point(0, 0), Point(0, 0), Point(1, 1)]
    out = unique_points(pts)
    assert len(out) == 2
