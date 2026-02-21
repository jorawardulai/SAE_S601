from domain.point import Point


class Segment:
    def __init__(self, p1: Point, p2: Point):
        
        if (p1.x, p1.y) < (p2.x, p2.y):
            self.p1 = p1
            self.p2 = p2
        else:
            self.p1 = p2
            self.p2 = p1

    def __eq__(self, other):
        return isinstance(other, Segment) and \
               self.p1 == other.p1 and \
               self.p2 == other.p2

    def __hash__(self):
        return hash((self.p1, self.p2))

    def __repr__(self):
        return f"Segment({self.p1}, {self.p2})"