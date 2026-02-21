from domain.point import Point
from domain.segment import Segment

class Triangle:
    def __init__(self, p1, p2, p3):
        self.points = (p1, p2, p3)
        self.center = self._calculer_centre()

    def _calculer_centre(self):
        a, b, c = self.points
        d = 2 * (a.x*(b.y - c.y) + b.x*(c.y - a.y) + c.x*(a.y - b.y))
        
        if abs(d) < 1e-9:
            return Point((a.x+b.x+c.x)/3, (a.y+b.y+c.y)/3)
            
        ux = ((a.x**2 + a.y**2)*(b.y - c.y) + (b.x**2 + b.y**2)*(c.y - a.y) + (c.x**2 + c.y**2)*(a.y - b.y)) / d
        uy = ((a.x**2 + a.y**2)*(c.x - b.x) + (b.x**2 + b.y**2)*(a.x - c.x) + (c.x**2 + c.y**2)*(b.x - a.x)) / d
        return Point(ux, uy)

    def dans_cercle(self, p):
        r2 = (self.points[0].x - self.center.x)**2 + (self.points[0].y - self.center.y)**2
        dist2 = (p.x - self.center.x)**2 + (p.y - self.center.y)**2
        return dist2 <= r2 + 1e-5

    def aretes(self):
        return [Segment(self.points[0], self.points[1]),
                Segment(self.points[1], self.points[2]),
                Segment(self.points[2], self.points[0])]