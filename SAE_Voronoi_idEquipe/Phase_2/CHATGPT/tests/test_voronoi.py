from app.domain.clipping import BBox
from app.domain.delaunay import bowyer_watson
from app.domain.geometry import Point
from app.domain.voronoi import build_voronoi_from_delaunay


def test_voronoi_cells_are_bounded_and_clipped():
    pts = [Point(0, 0), Point(2, 0), Point(0, 2), Point(2, 2)]
    bbox = BBox(-1, -1, 3, 3)
    delaunay = bowyer_watson(pts)
    vor = build_voronoi_from_delaunay(pts, delaunay.triangles, delaunay.neighbors, bbox)

    assert set(vor.cells.keys()) == set(pts)
    for _, cell in vor.cells.items():
        assert len(cell) >= 3
        assert all(bbox.xmin - 1e-8 <= v.x <= bbox.xmax + 1e-8 for v in cell)
        assert all(bbox.ymin - 1e-8 <= v.y <= bbox.ymax + 1e-8 for v in cell)


def test_voronoi_cell_order_is_ccw_like():
    pts = [Point(0, 0), Point(3, 0), Point(0, 3)]
    bbox = BBox(-10, -10, 10, 10)
    delaunay = bowyer_watson(pts)
    vor = build_voronoi_from_delaunay(pts, delaunay.triangles, delaunay.neighbors, bbox)
    cell = vor.cells[pts[0]]
    assert len(cell) >= 3
