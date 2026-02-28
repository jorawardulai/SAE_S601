from domain.models import Point, Triangle
import numpy as np

class VoronoiEngine:
    def __init__(self, points):
        self.points = points
        self.triangles = []

    def run_bowyer_watson(self):
        # 1. Super-Triangle (doit englober TOUS les points)
        min_x, max_x = min(p.x for p in self.points), max(p.x for p in self.points)
        min_y, max_y = min(p.y for p in self.points), max(p.y for p in self.points)
        dx, dy = max_x - min_x, max_y - min_y
        st_p1 = Point(min_x - 20 * dx, min_y - dy)
        st_p2 = Point(max_x + 20 * dx, min_y - dy)
        st_p3 = Point(min_x + dx/2, max_y + 20 * dy)
        
        super_triangle = Triangle(st_p1, st_p2, st_p3)
        self.triangles = [super_triangle]

        for p in self.points:
            bad_triangles = [t for t in self.triangles if t.circle_contains(p)]
            polygon_edges = []
            
            # Trouver les arêtes de la cavité (non partagées entre bad_triangles)
            for t in bad_triangles:
                for edge in [(t.points[0], t.points[1]), (t.points[1], t.points[2]), (t.points[2], t.points[0])]:
                    # Normaliser l'arête pour la comparaison (tri par id/coordonnées)
                    sorted_edge = tuple(sorted(edge, key=lambda pt: (pt.x, pt.y)))
                    is_shared = False
                    for other in bad_triangles:
                        if t == other: continue
                        if any(tuple(sorted(e, key=lambda pt: (pt.x, pt.y))) == sorted_edge 
                               for e in [(other.points[0], other.points[1]), (other.points[1], other.points[2]), (other.points[2], other.points[0])]):
                            is_shared = True
                            break
                    if not is_shared:
                        polygon_edges.append(edge)

            for t in bad_triangles: self.triangles.remove(t)
            for edge in polygon_edges:
                self.triangles.append(Triangle(edge[0], edge[1], p))

        # Supprimer les triangles liés au super-triangle
        self.triangles = [t for t in self.triangles if not any(pt in [st_p1, st_p2, st_p3] for pt in t.points)]

    def get_voronoi_cells(self):
        cells = {p: [] for p in self.points}
        for t in self.triangles:
            for p in t.points:
                if p in cells:
                    cells[p].append(t.center)
        
        # Tri radial pour que Matplotlib dessine des polygones convexes
        for p, vertices in cells.items():
            if len(vertices) > 2:
                vertices.sort(key=lambda v: np.arctan2(v.y - p.y, v.x - p.x))
        return cells