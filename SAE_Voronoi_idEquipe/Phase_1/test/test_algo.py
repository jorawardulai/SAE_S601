import pytest
from src.domain.point import Point
from src.domain.triangle import Triangle

from src.delaunay_bw import delaunay
from src.voronoi import voronoi, calculer_diagramme

def test_should_return_two_triangles_for_four_square_points():
    # Arrange
    points = [
        Point(0, 0), Point(0, 2),
        Point(2, 0), Point(2, 2)
    ]
    
    # Act
    triangles = delaunay(points)
    
    # Assert
    assert len(triangles) == 2


def test_should_return_correct_dictionary_structure_for_voronoi_diagram():
    # Arrange
    coordonnees = [
        (2, 4), (5.3, 4.5), (18, 50), (12.5, 23.7)
    ]
    
    # Act
    resultat = calculer_diagramme(coordonnees)
    
    # Assert
    assert "sommets" in resultat
    assert "aretes" in resultat
    
    assert len(resultat["sommets"]) == 4
    assert len(resultat["aretes"]) > 0

    premiere_arete = resultat["aretes"][0]
    assert len(premiere_arete) == 2       
    assert len(premiere_arete[0]) == 2     

def test_should_return_infinite_ray_when_edge_is_on_hull():
    # Arrange
    p1, p2, p3 = Point(0, 0), Point(2, 0), Point(1, 2)
    triangle = Triangle(p1, p2, p3)
    triangles = [triangle]
    # Act 
    bord = voronoi(triangles)
    # Assert
    assert len(bord) == 3
    assert bord[0].p1 == triangle.center or bord[0].p2 == triangle.center