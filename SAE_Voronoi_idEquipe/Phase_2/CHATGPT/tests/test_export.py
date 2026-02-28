from app.domain.clipping import BBox
from app.domain.geometry import Point
from app.infra.export import figure_to_png_bytes, figure_to_svg_bytes
from app.ui.renderer import RenderOptions, render_figure


def test_export_png_and_svg_non_empty():
    points = [Point(0, 0), Point(1, 0), Point(0, 1)]
    bbox = BBox(-1, -1, 2, 2)
    cells = {points[0]: [Point(0, 0), Point(0.5, 0), Point(0, 0.5)]}
    fig = render_figure(cells, points, delaunay_triangles=[], bbox=bbox, options=RenderOptions())

    png = figure_to_png_bytes(fig)
    svg = figure_to_svg_bytes(fig)

    assert isinstance(png, (bytes, bytearray)) and len(png) > 100
    assert isinstance(svg, (bytes, bytearray)) and len(svg) > 100
