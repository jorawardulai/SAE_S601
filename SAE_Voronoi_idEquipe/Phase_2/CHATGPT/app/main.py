from __future__ import annotations

import streamlit as st

from app.domain.clipping import BBox
from app.domain.delaunay import bowyer_watson
from app.domain.geometry import Point
from app.domain.voronoi import build_voronoi_from_delaunay
from app.infra.export import figure_to_png_bytes, figure_to_svg_bytes
from app.infra.io_points import load_points_from_path, parse_points_bytes
from app.ui.renderer import RenderOptions, render_figure


def _auto_bbox(points: list[Point], pad_ratio: float = 0.10) -> BBox:
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    dx = xmax - xmin
    dy = ymax - ymin
    d = max(dx, dy) if max(dx, dy) > 0 else 1.0
    pad = d * pad_ratio
    return BBox(xmin - pad, ymin - pad, xmax + pad, ymax + pad)


st.set_page_config(page_title="Voronoï (Bowyer–Watson)", layout="wide")
st.title("Diagramme de Voronoï ")

with st.sidebar:
    st.header("Entrée des points")
    uploaded = st.file_uploader("Fichier .txt ou .json", type=["txt", "json"])
    folder_path = st.text_input("Ou chemin vers un fichier/dossier local (optionnel)")

    st.divider()
    st.header("Affichage")
    show_points = st.checkbox("Afficher les points", value=True)
    show_voronoi_edges = st.checkbox("Afficher bords Voronoï", value=True)
    show_delaunay = st.checkbox("Afficher triangulation Delaunay", value=False)
    alpha = st.slider("Transparence (alpha)", 0.05, 1.0, 0.55, 0.05)
    seed = st.number_input("Seed couleurs", min_value=0, max_value=10_000_000, value=123, step=1)

    st.divider()
    st.header("Bounding box (clipping)")
    use_auto_bbox = st.checkbox("Auto bbox", value=True)

points: list[Point] = []
sources: list[str] = []

try:
    if uploaded is not None:
        points = parse_points_bytes(uploaded.name, uploaded.getvalue())
        sources = [uploaded.name]
    elif folder_path.strip():
        res = load_points_from_path(folder_path.strip())
        points = res.points
        sources = res.sources
except Exception as e:
    st.error(f"Erreur de chargement: {e}")

if not points:
    st.info("Charge un fichier .txt/.json ou saisis un chemin local pour commencer.")
    st.stop()

st.write(f"✅ Points chargés: **{len(points)}**")
if sources:
    with st.expander("Sources"):
        for s in sources[:50]:
            st.write("-", s)
        if len(sources) > 50:
            st.write(f"... (+{len(sources) - 50} fichiers)")

if use_auto_bbox:
    bbox = _auto_bbox(points)
else:
    col1, col2 = st.columns(2)
    with col1:
        xmin = st.number_input("xmin", value=float(min(p.x for p in points)))
        ymin = st.number_input("ymin", value=float(min(p.y for p in points)))
    with col2:
        xmax = st.number_input("xmax", value=float(max(p.x for p in points)))
        ymax = st.number_input("ymax", value=float(max(p.y for p in points)))
    bbox = BBox(float(xmin), float(ymin), float(xmax), float(ymax))

options = RenderOptions(
    show_points=show_points,
    show_voronoi_edges=show_voronoi_edges,
    show_delaunay=show_delaunay,
    alpha=float(alpha),
    seed=int(seed),
)

if st.button("Générer Voronoï", type="primary"):
    with st.spinner("Calcul Delaunay (Bowyer–Watson) puis Voronoï..."):
        delaunay = bowyer_watson(points)
        vor = build_voronoi_from_delaunay(points, delaunay.triangles, delaunay.neighbors, bbox)
        fig = render_figure(vor.cells, points, vor.delaunay_triangles, bbox, options)

    st.pyplot(fig, use_container_width=True)

    png_bytes = figure_to_png_bytes(fig)
    svg_bytes = figure_to_svg_bytes(fig)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Exporter PNG", data=png_bytes, file_name="voronoi.png", mime="image/png")
    with c2:
        st.download_button("Exporter SVG", data=svg_bytes, file_name="voronoi.svg", mime="image/svg+xml")
else:
    st.caption("Clique sur « Générer Voronoï » pour lancer le calcul et voir/ exporter le rendu.")
