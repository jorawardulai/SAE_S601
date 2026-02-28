from logique.engine import VoronoiEngine

def test_bowyer_watson_integration(sample_points):
    """Vérifie l'exécution complète de l'algorithme."""
    engine = VoronoiEngine(sample_points)
    engine.run_bowyer_watson()
    
    # Vérifie que Delaunay a généré des triangles
    assert len(engine.triangles) > 0
    
    # Vérifie que Voronoï a généré des cellules pour tous les points
    cells = engine.get_voronoi_cells()
    assert len(cells) == len(sample_points)

def test_cell_is_closed(sample_points):
    """Vérifie que le point central a une cellule fermée (min 3 sommets)."""
    engine = VoronoiEngine(sample_points)
    engine.run_bowyer_watson()
    cells = engine.get_voronoi_cells()
    
    center_pt = sample_points[4] # Le point (5,5)
    assert len(cells[center_pt]) >= 3