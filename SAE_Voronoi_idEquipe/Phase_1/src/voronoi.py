import math
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
            
    lignes_voronoi = []

    for arete, liste_t in aretes_partagees.items():
        if len(liste_t) == 2:
            # La ligne sépare deux triangles, on relie leurs centres.
            lignes_voronoi.append(Segment(liste_t[0].center, liste_t[1].center))
            
        elif len(liste_t) == 1:
            # Il n'y a qu'un seul triangle, on doit faire "fuir" la ligne vers l'extérieur.
            t = liste_t[0]
            A = arete.p1
            B = arete.p2
            
            
            C = next(p for p in t.points if p != A and p != B)
            
            
            dx = B.x - A.x
            dy = B.y - A.y
            nx = -dy
            ny = dx
            
            
            mx = (A.x + B.x) / 2
            my = (A.y + B.y) / 2
            mcx = C.x - mx
            mcy = C.y - my
            
            if (nx * mcx + ny * mcy) > 0:
                nx = -nx
                ny = -ny
                
            
            longueur = math.hypot(nx, ny)
            if longueur != 0:
                nx /= longueur
                ny /= longueur
                
            point_lointain = Point(t.center.x + nx * 5000, t.center.y + ny * 5000)
            lignes_voronoi.append(Segment(t.center, point_lointain))
            
    return lignes_voronoi

def calculer_diagramme(liste_coordonnees: list[tuple]) -> dict:
    """
    Entrée : Liste de tuples (x, y)
    Sortie : Dictionnaire avec "sommet" et "aretes"
    """
    points = [Point(x, y) for x, y in liste_coordonnees]
    
    triangles = delaunay(points)
    
    lignes = voronoi(triangles)
    
    return {
        "sommet": [(p.x, p.y) for p in points],
        "aretes": [((l.p1.x, l.p1.y), (l.p2.x, l.p2.y)) for l in lignes]
    }
