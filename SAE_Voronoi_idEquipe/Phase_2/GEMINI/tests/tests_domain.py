from domain.models import Point, Triangle

def test_triangle_center():
    """Vérifie le calcul du centre circonscrit."""
    p1, p2, p3 = Point(0, 0), Point(4, 0), Point(0, 4)
    t = Triangle(p1, p2, p3)
    assert t.center.x == 2.0
    assert t.center.y == 2.0
    assert t.radius_sq == 8.0

def test_circle_inclusion():
    """Vérifie si un point est dans le cercle ou non."""
    t = Triangle(Point(0,0), Point(10,0), Point(5,10))
    assert t.circle_contains(Point(5, 5)) is True
    assert t.circle_contains(Point(20, 20)) is False