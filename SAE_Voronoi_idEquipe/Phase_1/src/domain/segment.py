class Segment:
    def __init__(self, p1, p2):
        if (p1.x, p1.y) < (p2.x, p2.y):
            self.p1, self.p2 = p1, p2
        else:
            self.p1, self.p2 = p2, p1
            
    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2
        
    def __hash__(self):
        return hash((self.p1, self.p2))