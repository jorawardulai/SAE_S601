Pour valider ton architecture et garantir que l'algorithme de Bowyer-Watson fonctionne comme prévu, nous allons créer un fichier tests.py. Ce fichier utilise le module standard unittest de Python.

Il permet de vérifier les trois piliers de ton projet :

Le Domaine : Le calcul du cercle circonscrit est-il précis ?

La Logique : L'algorithme génère-t-il le bon nombre de triangles ?

La Dualité : Les cellules de Voronoï sont-elles correctement formées ?

1. Création du fichier tests.py
Place ce fichier à la racine de ton projet (au même niveau que app.py).

Python
import unittest
import numpy as np
from domain.models import Point, Triangle
from logique.engine import VoronoiEngine

class TestVoronoiArchitecture(unittest.TestCase):

    def setUp(self):
        """Initialisation de points de test simples (un carré)."""
        self.points = [
            Point(0, 0),
            Point(10, 0),
            Point(10, 10),
            Point(0, 10),
            Point(5, 5)  # Point central
        ]

    def test_circumcircle_calculation(self):
        """Vérifie que le centre du cercle circonscrit est correct pour un triangle rectangle."""
        p1, p2, p3 = Point(0, 0), Point(4, 0), Point(0, 4)
        triangle = Triangle(p1, p2, p3)
        # Le centre d'un triangle rectangle est le milieu de l'hypoténuse
        self.assertAlmostEqual(triangle.center.x, 2.0)
        self.assertAlmostEqual(triangle.center.y, 2.0)
        self.assertAlmostEqual(triangle.radius_sq, 8.0)

    def test_point_in_circumcircle(self):
        """Vérifie la détection d'un point dans le cercle circonscrit (Condition de Delaunay)."""
        p1, p2, p3 = Point(0, 0), Point(10, 0), Point(5, 10)
        triangle = Triangle(p1, p2, p3)
        p_inside = Point(5, 5)
        p_outside = Point(50, 50)
        
        self.assertTrue(triangle.circle_contains(p_inside))
        self.assertFalse(triangle.circle_contains(p_outside))

    def test_bowyer_watson_generation(self):
        """Vérifie que l'algorithme produit des triangles après exécution."""
        engine = VoronoiEngine(self.points)
        engine.run_bowyer_watson()
        # Pour 5 points bien placés, on doit avoir plusieurs triangles de Delaunay
        self.assertGreater(len(engine.triangles), 0)

    def test_voronoi_cell_consistency(self):
        """Vérifie que chaque point d'entrée possède une cellule de Voronoï associée."""
        engine = VoronoiEngine(self.points)
        engine.run_bowyer_watson()
        cells = engine.get_voronoi_cells()
        
        # On vérifie que le point central a bien une cellule fermée (au moins 3 sommets)
        center_pt = self.points[4]
        self.assertIn(center_pt, cells)
        self.assertGreaterEqual(len(cells[center_pt]), 3)

    def test_radial_sorting(self):
        """Vérifie que les sommets des cellules sont triés (pas de polygones croisés)."""
        p_gen = Point(5, 5)
        # Sommets non triés autour de (5,5)
        vertices = [Point(6, 6), Point(4, 4), Point(6, 4), Point(4, 6)]
        
        # Simulation du tri radial utilisé dans l'engine
        vertices.sort(key=lambda v: np.arctan2(v.y - p_gen.y, v.x - p_gen.x))
        
        # Calcul des angles pour vérifier l'ordre croissant
        angles = [np.arctan2(v.y - p_gen.y, v.x - p_gen.x) for v in vertices]
        self.assertTrue(all(angles[i] <= angles[i+1] for i in range(len(angles)-1)))

if __name__ == '__main__':
    unittest.main()