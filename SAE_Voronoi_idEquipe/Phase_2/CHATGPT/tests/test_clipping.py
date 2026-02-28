from app.domain.clipping import BBox, clip_polygon_to_bbox
from app.domain.geometry import Point


def test_clip_polygon_fully_inside():
    bbox = BBox(0, 0, 10, 10)
    poly = [Point(1, 1), Point(9, 1), Point(9, 9), Point(1, 9)]
    out = clip_polygon_to_bbox(poly, bbox)
    assert len(out) == 4


def test_clip_polygon_fully_outside():
    bbox = BBox(0, 0, 10, 10)
    poly = [Point(20, 20), Point(21, 20), Point(21, 21), Point(20, 21)]
    out = clip_polygon_to_bbox(poly, bbox)
    assert out == []


def test_clip_polygon_partial():
    bbox = BBox(0, 0, 10, 10)
    poly = [Point(-5, 5), Point(5, 15), Point(15, 5), Point(5, -5)]
    out = clip_polygon_to_bbox(poly, bbox)
    assert len(out) >= 3
    assert all(bbox.xmin - 1e-8 <= p.x <= bbox.xmax + 1e-8 for p in out)
    assert all(bbox.ymin - 1e-8 <= p.y <= bbox.ymax + 1e-8 for p in out)
