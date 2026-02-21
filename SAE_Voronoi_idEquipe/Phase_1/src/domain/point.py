import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class VoronoiResult:
    def __init__(self, cells, edges):
        self.cells = cells
        self.edges = edges


def compute_voronoi(points, bbox, resolution=0.5):

    x_min, x_max, y_min, y_max = bbox

    cells = {site: [] for site in points}

    grid_owner = []
    x_values = []
    y_values = []

    x = x_min
    while x <= x_max:
        row = []
        y = y_min
        y_row = []

        while y <= y_max:
            current_point = Point(x, y)

            closest = min(points, key=lambda p: distance(current_point, p))

            cells[closest].append((x, y))
            row.append(closest)

            y_row.append(y)
            y += resolution

        grid_owner.append(row)
        x_values.append(x)
        y_values = y_row
        x += resolution

    edges = detect_edges(grid_owner, x_values, y_values, resolution)

    return VoronoiResult(cells, edges)


def detect_edges(grid_owner, x_values, y_values, resolution):

    edges = []

    rows = len(grid_owner)
    cols = len(grid_owner[0])

    for i in range(rows - 1):
        for j in range(cols - 1):

            current = grid_owner[i][j]

            
            if grid_owner[i + 1][j] != current:
                x1 = x_values[i]
                y1 = y_values[j]
                x2 = x_values[i] + resolution
                y2 = y_values[j]
                edges.append(((x1, y1), (x2, y2)))

            if grid_owner[i][j + 1] != current:
                x1 = x_values[i]
                y1 = y_values[j]
                x2 = x_values[i]
                y2 = y_values[j] + resolution
                edges.append(((x1, y1), (x2, y2)))

    return edges
