import math
from domain.point import Point
from domain.segment import Segment


class Triangle:

    def __init__(self, a: Point, b: Point, c: Point):
        self.points = (a, b, c)

    def segments(self):
        a, b, c = self.points
        return [
            Segment(a, b),
            Segment(b, c),
            Segment(c, a)
        ]

    def centre_circonscrit(self) -> Point:
        a, b, c = self.points

        x1, y1 = a.x, a.y
        x2, y2 = b.x, b.y
        x3, y3 = c.x, c.y

        denominateur = 2 * (
            x1 * (y2 - y3) +
            x2 * (y3 - y1) +
            x3 * (y1 - y2)
        )

        if abs(denominateur) < 1e-12:
            
            return Point(x1, y1)

        x_centre = (
            (x1**2 + y1**2) * (y2 - y3) +
            (x2**2 + y2**2) * (y3 - y1) +
            (x3**2 + y3**2) * (y1 - y2)
        ) / denominateur

        y_centre = (
            (x1**2 + y1**2) * (x3 - x2) +
            (x2**2 + y2**2) * (x1 - x3) +
            (x3**2 + y3**2) * (x2 - x1)
        ) / denominateur

        return Point(x_centre, y_centre)

    def point_dans_cercle(self, candidat: Point) -> bool:
        centre = self.centre_circonscrit()

        dx_ref = centre.x - self.points[0].x
        dy_ref = centre.y - self.points[0].y
        rayon_carre = dx_ref * dx_ref + dy_ref * dy_ref

        dx_test = centre.x - candidat.x
        dy_test = centre.y - candidat.y
        distance_carre = dx_test * dx_test + dy_test * dy_test

        return distance_carre <= rayon_carre


    def partage_sommet(self, autre_triangle) -> bool:
        return any(p in autre_triangle.points for p in self.points)

    def __eq__(self, other):
        if not isinstance(other, Triangle):
            return False
        return set(self.points) == set(other.points)

    def __hash__(self):
        points_tries = sorted(self.points, key=lambda p: (p.x, p.y))
        return hash(tuple((p.x, p.y) for p in points_tries))

    def __repr__(self):
        a, b, c = self.points
        return f"Triangle({a}, {b}, {c})"