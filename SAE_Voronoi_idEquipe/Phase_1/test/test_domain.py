import pytest

from src.domain.point import Point
from src.domain.segment import Segment
from src.domain.triangle import Triangle

def test_should_return_true_when_points_have_same_coordinates():
    # Arrange
    p1 = Point(2.0, 3.5)
    p2 = Point(2.0, 3.5)
    p3 = Point(2.0, 3.6)
    
    # Act
    p1_egal_p2 = (p1 == p2)
    p1_egal_p3 = (p1 == p3)
    
    # Assert
    assert p1_egal_p2 is True
    assert p1_egal_p3 is False


def test_should_return_true_when_segments_are_reversed():
    # Arrange
    point_a = Point(0, 0)
    point_b = Point(10, 10)
    
    # Act
    segment_1 = Segment(point_a, point_b)
    segment_2 = Segment(point_b, point_a)
    
    # Assert
    assert segment_1 == segment_2


def test_should_return_correct_circumcenter_for_right_triangle():
    # Arrange
    point_a = Point(0, 0)
    point_b = Point(2, 0)
    point_c = Point(0, 2)
    triangle = Triangle(point_a, point_b, point_c)
    
    # Act
    center_x = triangle.center.x
    center_y = triangle.center.y
    
    # Assert
    assert center_x == pytest.approx(1.0)
    assert center_y == pytest.approx(1.0)


def test_should_return_true_when_point_is_inside_circumcircle():
    # Arrange
    triangle = Triangle(Point(0, 0), Point(2, 0), Point(0, 2))
    point_interieur = Point(0.5, 0.5)
    point_exterieur = Point(5, 5)
    
    # Act
    a_l_interieur = triangle.dans_cercle(point_interieur)
    a_l_exterieur = triangle.dans_cercle(point_exterieur)
    
    # Assert
    assert a_l_interieur is True
    assert a_l_exterieur is False