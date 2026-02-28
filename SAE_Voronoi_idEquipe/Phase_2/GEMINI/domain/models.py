import numpy as np

class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
    def to_tuple(self): return (self.x, self.y)

class Triangle:
    def __init__(self, p1, p2, p3):
        self.points = (p1, p2, p3)
        self.edges = {(p1, p2), (p2, p3), (p3, p1)}
        self.center, self.radius_sq = self._compute_circle()

    def _compute_circle(self):
        (p1, p2, p3) = self.points
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(D) < 1e-9: return Point(0,0), 0
        ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / D
        uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / D
        return Point(ux, uy), (x1 - ux)**2 + (y1 - uy)**2

    def circle_contains(self, p):
        return (p.x - self.center.x)**2 + (p.y - self.center.y)**2 < self.radius_sq