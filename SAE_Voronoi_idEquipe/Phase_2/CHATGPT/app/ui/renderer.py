from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

from app.domain.clipping import BBox
from app.domain.geometry import Point, Triangle


@dataclass(frozen=True, slots=True)
class RenderOptions:
    show_points: bool = True
    show_voronoi_edges: bool = True
    show_delaunay: bool = False
    alpha: float = 0.55
    seed: int = 123


def _color_for_site(site: Point, rng: Random) -> Tuple[float, float, float]:
    # stable-ish per site (by hashing coords)
    h = hash((round(site.x, 6), round(site.y, 6)))
    local = Random(h ^ rng.randint(0, 2**31 - 1))
    return (local.random(), local.random(), local.random())


def render_figure(
    cells: Dict[Point, List[Point]],
    points: List[Point],
    delaunay_triangles: List[Triangle],
    bbox: BBox,
    options: RenderOptions,
) -> plt.Figure:
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111)

    rng = Random(options.seed)

    # Voronoi cells (filled polygons)
    for site, poly in cells.items():
        if len(poly) < 3:
            continue
        color = _color_for_site(site, rng)
        patch = MplPolygon([(p.x, p.y) for p in poly], closed=True, alpha=options.alpha, linewidth=1.0)
        patch.set_facecolor(color)
        ax.add_patch(patch)
        if options.show_voronoi_edges:
            outline = MplPolygon([(p.x, p.y) for p in poly], closed=True, fill=False, linewidth=1.0)
            ax.add_patch(outline)

    if options.show_delaunay:
        for t in delaunay_triangles:
            xs = [t.a.x, t.b.x, t.c.x, t.a.x]
            ys = [t.a.y, t.b.y, t.c.y, t.a.y]
            ax.plot(xs, ys, linewidth=0.8)

    if options.show_points:
        ax.scatter([p.x for p in points], [p.y for p in points], s=18)

    ax.set_xlim(bbox.xmin, bbox.xmax)
    ax.set_ylim(bbox.ymin, bbox.ymax)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.0)
    return fig
