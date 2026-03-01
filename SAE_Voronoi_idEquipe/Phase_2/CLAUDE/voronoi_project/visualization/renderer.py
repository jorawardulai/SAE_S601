"""
Rendu matplotlib du diagramme de Voronoï.
"""

from dataclasses import dataclass, field

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon as MplPolygon

from geometry.triangle import Triangle


@dataclass
class RenderConfig:
    """Paramètres visuels du rendu."""
    show_sites   : bool  = True
    show_edges   : bool  = True
    show_delaunay: bool  = False
    bg_color     : str   = "#1a1a2e"
    edge_color   : str   = "#ffffff"
    site_color   : str   = "#ff4444"
    cell_alpha   : float = 0.75
    fig_size     : int   = 8
    dpi          : int   = 120


def draw_voronoi(
    points   : list[tuple],
    triangles: list[Triangle],
    cells    : dict[int, list[tuple]],
    colors   : list[tuple],
    config   : RenderConfig | None = None,
) -> Figure:
    """
    Produit la figure matplotlib du diagramme de Voronoï.

    Args:
        points   : sites générateurs.
        triangles: triangulation de Delaunay (affiché si config.show_delaunay).
        cells    : dictionnaire {index: polygone} des cellules Voronoï.
        colors   : liste de couleurs (r, g, b) indexée par position.
        config   : paramètres visuels (RenderConfig par défaut si None).

    Returns:
        Figure matplotlib prête à être affichée ou sauvegardée.
    """
    if config is None:
        config = RenderConfig()

    fig, ax = plt.subplots(figsize=(config.fig_size, config.fig_size), dpi=config.dpi)
    fig.patch.set_facecolor(config.bg_color)
    ax.set_facecolor(config.bg_color)
    ax.set_aspect("equal")
    ax.axis("off")

    _draw_cells(ax, cells, colors, config)

    if config.show_delaunay:
        _draw_delaunay(ax, triangles)

    if config.show_sites:
        _draw_sites(ax, points, config.site_color)

    ax.autoscale_view()
    plt.tight_layout(pad=0)
    return fig


# ── Helpers de dessin ─────────────────────────────────────────────────────────

def _draw_cells(ax, cells, colors, config: RenderConfig) -> None:
    for i, poly_pts in cells.items():
        if len(poly_pts) < 3:
            continue
        color = colors[i % len(colors)]
        patch = MplPolygon(
            poly_pts,
            closed=True,
            facecolor=(*color, config.cell_alpha),
            edgecolor=config.edge_color if config.show_edges else "none",
            linewidth=0.8 if config.show_edges else 0,
        )
        ax.add_patch(patch)


def _draw_delaunay(ax, triangles) -> None:
    for tri in triangles:
        xs = [tri.a[0], tri.b[0], tri.c[0], tri.a[0]]
        ys = [tri.a[1], tri.b[1], tri.c[1], tri.a[1]]
        ax.plot(xs, ys, color="#ffffff", linewidth=0.4, alpha=0.4, zorder=3)


def _draw_sites(ax, points, site_color: str) -> None:
    sx = [p[0] for p in points]
    sy = [p[1] for p in points]
    ax.scatter(sx, sy, color=site_color, s=18, zorder=5,
               linewidths=0.5, edgecolors="white")
