class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-5 and abs(self.y - other.y) < 1e-5
    
    def __hash__(self):
        return hash((round(self.x, 5), round(self.y, 5)))