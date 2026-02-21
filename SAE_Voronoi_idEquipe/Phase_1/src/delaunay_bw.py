from domain.point import Point
from domain.triangle import Triangle

def delaunay(points):
    """Calcule la triangulation de Delaunay via l'algorithme de Bowyer-Watson."""
    p1 = Point(-50000, -50000)
    p2 = Point(50000, -50000)
    p3 = Point(0, 50000)
    super_t = Triangle(p1, p2, p3)
    
    triangles = [super_t]
    
    for p in points:
        mauvais_triangles = [t for t in triangles if t.dans_cercle(p)]
        contour = {}
        for t in mauvais_triangles:
            for arete in t.aretes():
                contour[arete] = contour.get(arete, 0) + 1
        
        aretes_externes = [arete for arete, count in contour.items() if count == 1]
        triangles = [t for t in triangles if t not in mauvais_triangles]
        
        for arete in aretes_externes:
            triangles.append(Triangle(arete.p1, arete.p2, p))
            
    return [t for t in triangles if not any(pt in super_t.points for pt in t.points)]