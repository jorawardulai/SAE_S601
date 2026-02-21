from .domain.point import Point
from .domain.segment import Segment
from .delaunay_bw import delaunay  

def voronoi(triangles):
    """Construit les arêtes de Voronoï à partir des triangles de Delaunay."""
    aretes_partagees = {}
    for t in triangles:
        for arete in t.aretes():
            if arete not in aretes_partagees:
                aretes_partagees[arete] = []
            aretes_partagees[arete].append(t)
            
    return [Segment(liste_t[0].center, liste_t[1].center) 
            for liste_t in aretes_partagees.values() if len(liste_t) == 2]

def calculer_diagramme(liste_coordonnees: list[tuple]) -> dict:
    """
    Entrée : Liste de tuples (x, y)
    Sortie : Dictionnaire avec "sommet" et "aretes"
    """
    points = [Point(x, y) for x, y in liste_coordonnees]
    
    points_calcul = points.copy()
    points_calcul.extend([
        Point(-50, -50), Point(50, -50),
        Point(50, 50), Point(-50, 50)
    ])
    
    triangles = delaunay(points_calcul)
    
    lignes = voronoi(triangles)
    
    return {
        "sommet": [(p.x, p.y) for p in points],
        "aretes": [((l.p1.x, l.p1.y), (l.p2.x, l.p2.y)) for l in lignes]
    }
