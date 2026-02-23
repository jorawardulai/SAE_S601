import math
from .domain.point import Point
from .domain.segment import Segment
from .delaunay_bw import delaunay  

def voronoi(triangles):
    aretes_partagees = {}
    
    for t in triangles:
        for arete in t.aretes():
            if arete not in aretes_partagees:
                aretes_partagees[arete] = []
            aretes_partagees[arete].append(t)
            
    lignes_voronoi = []

    for arete, liste_t in aretes_partagees.items():
        if len(liste_t) == 2:
            lignes_voronoi.append(Segment(liste_t[0].center, liste_t[1].center))
            
        elif len(liste_t) == 1:
            t = liste_t[0]
            A = arete.p1
            B = arete.p2
            
            C = None
            for p in t.points:
                if p != A and p != B:
                    C = p
                    break 
            
            dx = B.x - A.x
            dy = B.y - A.y
            
            nx = -dy
            ny = dx
            
            milieu_x = (A.x + B.x) / 2
            milieu_y = (A.y + B.y) / 2
            
            vec_interieur_x = C.x - milieu_x
            vec_interieur_y = C.y - milieu_y
            
            produit_scalaire = (nx * vec_interieur_x) + (ny * vec_interieur_y)
            
            if produit_scalaire > 0:
                nx = -nx
                ny = -ny
                

            longueur = math.sqrt((nx * nx) + (ny * ny)) 
            
            
            if longueur != 0:
                nx = nx / longueur
                ny = ny / longueur
                
            point_infini = Point(t.center.x + (nx * 9999), t.center.y + (ny * 9999))
            lignes_voronoi.append(Segment(t.center, point_infini))
            
    return lignes_voronoi

def calculer_diagramme(liste_coordonnees):
    
    points = []
    for x, y in liste_coordonnees:
        points.append(Point(x, y))
    
    triangles = delaunay(points)
    lignes = voronoi(triangles)
    
    resultat = {
        "sommet": [],
        "aretes": []
    }
    
    for p in points:
        resultat["sommet"].append((p.x, p.y))
        
    for l in lignes:
        resultat["aretes"].append(((l.p1.x, l.p1.y), (l.p2.x, l.p2.y)))
        
    return resultat