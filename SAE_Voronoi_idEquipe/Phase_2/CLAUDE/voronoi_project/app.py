"""
Diagramme de Voronoï — Application Streamlit
=============================================
Point d'entrée unique. Orchestre les modules métier sans logique algorithmique.

Lancement :
    streamlit run app.py
"""

import io
import json
import random
import sys
import os

# ── Résolution des imports locaux ─────────────────────────────────────────────
# Streamlit peut exécuter ce fichier depuis un répertoire de travail différent
# de celui du projet. On insère explicitement la racine du projet en tête de
# sys.path pour garantir que geometry/, algorithms/, loaders/ et visualization/
# soient toujours trouvables.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

from algorithms import bowyer_watson, compute_voronoi
from loaders.parser import load_points
from visualization.colors import generate_colors, Palette
from visualization.renderer import draw_voronoi, RenderConfig


# ─────────────────────────────────────────────────────────────────────────────
#  Constantes UI
# ─────────────────────────────────────────────────────────────────────────────

_EXAMPLE_POINTS = [
    [50, 200], [150, 80], [300, 350], [420, 120], [500, 300],
    [200, 450], [350, 500], [80, 380], [450, 420], [250, 250],
]

_CSS = """
<style>
.main { background: #0f0f1a; }
h1 { font-size: 2.2rem !important; }
.stButton > button {
    background: linear-gradient(135deg, #6c63ff, #3ecfcf);
    color: white; border: none; border-radius: 8px;
    padding: 0.5rem 2rem; font-weight: 700; font-size: 1rem;
}
.stButton > button:hover { opacity: 0.85; }
.block-container { padding-top: 1rem; }
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _deduplicate(points: list) -> list:
    """Supprime les doublons en conservant l'ordre d'apparition."""
    seen, unique = set(), []
    for p in points:
        key = (round(p[0], 6), round(p[1], 6))
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def _compute_bbox(points: list, margin_ratio: float = 0.08) -> tuple:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    margin = max(max(xs) - min(xs), max(ys) - min(ys)) * margin_ratio + 1.0
    return (min(xs) - margin, max(xs) + margin,
            min(ys) - margin, max(ys) + margin)


def _fig_to_bytes(fig, bg_color: str) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=bg_color)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
#  Sections UI
# ─────────────────────────────────────────────────────────────────────────────

def _render_sidebar():
    """Construit la sidebar et retourne tous les paramètres utilisateur."""
    with st.sidebar:
        st.header("⚙️ Paramètres")

        st.subheader("📂 Source de données")
        uploaded = st.file_uploader(
            "Fichier JSON ou TXT", type=["json", "txt"],
            help="Formats : [[x,y],...] · {\"points\":...} · x y · x,y · (x,y)"
        )

        st.subheader("🎨 Palette de couleurs")
        palette    = st.selectbox("Palette", [p.value for p in Palette], index=0)
        color_seed = st.slider("Graine couleur", 0, 100, 42)

        st.subheader("🖼️ Rendu")
        bg_color   = st.color_picker("Fond",              "#1a1a2e")
        edge_color = st.color_picker("Arêtes Voronoï",    "#ffffff")
        site_color = st.color_picker("Sites générateurs", "#ff4444")
        fig_size   = st.slider("Taille figure", 5, 14, 9)

        st.subheader("👁️ Affichage")
        show_sites    = st.checkbox("Sites générateurs",      value=True)
        show_edges    = st.checkbox("Arêtes Voronoï",         value=True)
        show_delaunay = st.checkbox("Triangulation Delaunay", value=False)

        st.subheader("🎲 Points aléatoires")
        n_random  = st.slider("Nombre de points", 5, 300, 40)
        area_size = st.slider("Taille zone",      100, 1000, 500)
        rnd_seed  = st.slider("Graine aléatoire", 0, 200, 7)
        gen_btn   = st.button("Générer points aléatoires")

        st.divider()
        st.caption(
            "**JSON** : `[[x,y],...]` · `{\"points\":[...]}` · `[{\"x\":..}]`\n\n"
            "**TXT**  : `x y` · `x,y` · `(x,y)` · `x;y`"
        )

    config = RenderConfig(
        show_sites=show_sites, show_edges=show_edges, show_delaunay=show_delaunay,
        bg_color=bg_color, edge_color=edge_color, site_color=site_color,
        fig_size=fig_size,
    )
    return uploaded, gen_btn, n_random, area_size, rnd_seed, config, palette, color_seed


def _render_welcome() -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.info("👈 Chargez un fichier ou générez des points dans la barre latérale.")
        st.markdown(
            "**Algorithme :**\n"
            "- Triangulation Delaunay → **Bowyer-Watson** (O(n²))\n"
            "- Circumcentres → sommets de Voronoï\n"
            "- Cellules non-bornées → rayons infinis\n"
            "- **Sutherland-Hodgman** clipping sur la bbox"
        )
    with col2:
        st.markdown("#### Exemple de fichier JSON")
        st.code(json.dumps(_EXAMPLE_POINTS, indent=2), language="json")


def _render_stats(points, triangles, cells) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Points",             len(points))
    c2.metric("Triangles Delaunay", len(triangles))
    c3.metric("Cellules Voronoï",   len(cells))
    c4.metric("Couverture",         f"{100 * len(cells) // max(len(points), 1)} %")


def _render_raw_data(points, triangles) -> None:
    with st.expander("📊 Données brutes"):
        tab_pts, tab_tri = st.tabs(["Points", "Triangles Delaunay"])
        with tab_pts:
            st.dataframe(
                [{"#": i, "x": round(p[0], 4), "y": round(p[1], 4)}
                 for i, p in enumerate(points)],
                use_container_width=True, height=300,
            )
        with tab_tri:
            rows = [
                {
                    "#": k,
                    "A":  f"({t.a[0]:.2f}, {t.a[1]:.2f})",
                    "B":  f"({t.b[0]:.2f}, {t.b[1]:.2f})",
                    "C":  f"({t.c[0]:.2f}, {t.c[1]:.2f})",
                    "CC": f"({t.circumcenter[0]:.2f}, {t.circumcenter[1]:.2f})",
                }
                for k, t in enumerate(triangles[:200])
            ]
            st.dataframe(rows, use_container_width=True, height=300)
            if len(triangles) > 200:
                st.caption(f"Limité aux 200 premiers sur {len(triangles)}")


# ─────────────────────────────────────────────────────────────────────────────
#  Pipeline principal
# ─────────────────────────────────────────────────────────────────────────────

def _load_or_generate(uploaded, gen_btn, n_random, area_size, rnd_seed):
    """Retourne les points depuis l'upload, le bouton ou le cache de session."""
    if gen_btn:
        rng = random.Random(rnd_seed)
        pts = [(rng.uniform(0, area_size), rng.uniform(0, area_size))
               for _ in range(n_random)]
        st.session_state["points_cache"] = pts
        st.success(f"✅ {n_random} points générés aléatoirement.")
        return pts

    if uploaded is not None:
        try:
            pts = load_points(uploaded)
            if len(pts) < 3:
                st.error("❌ Au moins 3 points sont nécessaires.")
                return None
            st.success(f"✅ {len(pts)} points chargés depuis **{uploaded.name}**.")
            return pts
        except Exception as exc:
            st.error(f"❌ Erreur de lecture : {exc}")
            return None

    if "points_cache" in st.session_state and not uploaded:
        return st.session_state["points_cache"]

    return None


def _run_pipeline(points, config, palette, color_seed) -> None:
    """Exécute triangulation → Voronoï → rendu → affichage."""
    with st.spinner("🔧 Triangulation de Delaunay (Bowyer-Watson)…"):
        triangles = bowyer_watson(points)

    bbox = _compute_bbox(points)

    with st.spinner("🎨 Construction du diagramme de Voronoï…"):
        cells = compute_voronoi(points, triangles, bbox)

    _render_stats(points, triangles, cells)

    colors = generate_colors(len(points), palette=palette, seed=color_seed)

    with st.spinner("🖌️ Rendu…"):
        fig = draw_voronoi(points, triangles, cells, colors, config)

    st.pyplot(fig, use_container_width=True)

    st.download_button(
        "⬇️ Télécharger le diagramme (PNG)",
        data=_fig_to_bytes(fig, config.bg_color),
        file_name="voronoi_diagram.png",
        mime="image/png",
    )

    _render_raw_data(points, triangles)


# ─────────────────────────────────────────────────────────────────────────────
#  Entrée principale
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="Diagramme de Voronoï",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown("## 🔷 Diagramme de Voronoï")
    st.markdown(
        "Triangulation de Delaunay **(Bowyer-Watson)** implémentée manuellement "
        "— sans `scipy.spatial`."
    )
    st.divider()

    uploaded, gen_btn, n_random, area_size, rnd_seed, config, palette, color_seed = (
        _render_sidebar()
    )

    points = _load_or_generate(uploaded, gen_btn, n_random, area_size, rnd_seed)

    if points is None:
        _render_welcome()
        return

    points = _deduplicate(points)

    if len(points) < 3:
        st.error("❌ Au moins 3 points distincts sont nécessaires.")
        return

    _run_pipeline(points, config, palette, color_seed)


if __name__ == "__main__":
    main()
