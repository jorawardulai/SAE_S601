from domain.triangle import Triangle
from domain.point import Point


def triangulation_delaunay(points: list[Point]) -> list[Triangle]:

    super_triangle = creer_super_triangle(points)

    triangles = [super_triangle]
    for point in points:

        triangles_invalides = []

        for triangle in triangles:
            if triangle.point_dans_cercle(point):
                triangles_invalides.append(triangle)

        aretes_frontiere = []

        for triangle in triangles_invalides:
            for arete in triangle.segments():
                if not est_arete_partagee(arete, triangles_invalides):
                    aretes_frontiere.append(arete)

        
        for triangle in triangles_invalides:
            triangles.remove(triangle)

        
        for arete in aretes_frontiere:
            nouveau_triangle = Triangle(arete.p1, arete.p2, point)
            triangles.append(nouveau_triangle)

    triangles_finaux = []
    for triangle in triangles:
        if not triangle.partage_sommet(super_triangle):
            triangles_finaux.append(triangle)

    return triangles_finaux


def creer_super_triangle(points: list[Point]) -> Triangle:

    abscisses = [p.x for p in points]
    ordonnees = [p.y for p in points]

    min_abscisse, max_abscisse = min(abscisses), max(abscisses)
    min_ordonnees, max_ordonnees = min(ordonnees), max(ordonnees)

    largeur = max_abscisse - min_abscisse
    hauteur = max_ordonnees - min_ordonnees
    marge = max(largeur, hauteur) * 10

    sommet_1 = Point(min_abscisse - marge, min_ordonnees - marge)
    sommet_2 = Point(min_abscisse - marge, max_ordonnees + marge * 2)
    sommet_3 = Point(max_abscisse + marge * 2, min_ordonnees - marge)

    return Triangle(sommet_1, sommet_2, sommet_3)


def est_arete_partagee(arete, triangles: list[Triangle]) -> bool:

    compteur = 0
    for triangle in triangles:
        for segment in triangle.segments():
            if segment == arete:
                compteur += 1

    return compteur > 1