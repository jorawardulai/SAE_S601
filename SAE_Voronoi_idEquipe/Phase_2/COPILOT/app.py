"""
Application Streamlit : Diagramme de Voronoï et triangulation de Delaunay (algorithme de Watson)

Utilisation :
- Lancer l'application :
    streamlit run app.py

- Entrée :
    Dans la barre latérale, saisir le chemin d'un dossier contenant des fichiers .json ou .txt.
    Formats acceptés :
        JSON :
            [
                {"x": 1.2, "y": 3.4},
                {"x": 2.0, "y": 1.0},
                ...
            ]
        ou
            [
                [1.2, 3.4],
                [2.0, 1.0],
                ...
            ]

        TXT :
            Un point par ligne, séparé par des espaces :
                1.2 3.4
                2.0 1.0
                ...

- Fonctionnalités :
    - Sélection du fichier de points à visualiser.
    - Calcul de la triangulation de Delaunay (Watson).
    - Construction du diagramme de Voronoï dual.
    - Affichage des points, des cellules de Voronoï colorées, et optionnellement de la triangulation.
    - Export du diagramme affiché en SVG et PNG via boutons de téléchargement.
"""

import os
import io
from typing import List, Tuple

import streamlit as st
import matplotlib.pyplot as plt

from geometry.delaunay import compute_delaunay_triangulation
from geometry.voronoi import build_voronoi_cells
from geometry.utils import compute_bounding_box
from point_io.json_loader import load_points_from_json
from point_io.txt_loader import load_points_from_txt


Point = Tuple[float, float]


def list_point_files(folder: str) -> List[str]:
    """Retourne la liste des fichiers .json et .txt dans un dossier."""
    if not folder or not os.path.isdir(folder):
        return []
    files = []
    for name in os.listdir(folder):
        if name.lower().endswith(".json") or name.lower().endswith(".txt"):
            files.append(name)
    return sorted(files)


def load_points_from_file(path: str) -> List[Point]:
    """Charge les points depuis un fichier JSON ou TXT, avec gestion d'erreurs."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        return load_points_from_json(path)
    elif ext == ".txt":
        return load_points_from_txt(path)
    else:
        raise ValueError(f"Extension de fichier non supportée : {ext}")


def plot_voronoi_and_delaunay(
    points: List[Point],
    triangles,
    voronoi_cells,
    show_delaunay: bool,
    figsize=(6, 6),
):
    """
    Crée une figure matplotlib avec :
    - les points
    - les cellules de Voronoï colorées
    - optionnellement la triangulation de Delaunay
    Retourne la figure.
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Déterminer une bounding box raisonnable pour l'affichage
    min_x, min_y, max_x, max_y = compute_bounding_box(points)
    margin_x = (max_x - min_x) * 0.1 if max_x > min_x else 1.0
    margin_y = (max_y - min_y) * 0.1 if max_y > min_y else 1.0
    ax.set_xlim(min_x - margin_x, max_x + margin_x)
    ax.set_ylim(min_y - margin_y, max_y + margin_y)
    ax.set_aspect("equal", adjustable="box")

    # Affichage des cellules de Voronoï
    import random

    random.seed(42)
    for idx, poly in voronoi_cells.items():
        if len(poly) < 3:
            continue
        # Couleur pseudo-aléatoire mais stable
        random.seed(idx + 123)
        color = (random.random() * 0.6 + 0.2,
                 random.random() * 0.6 + 0.2,
                 random.random() * 0.6 + 0.2)
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        ax.fill(xs, ys, color=color, alpha=0.6, edgecolor="k", linewidth=0.5)

    # Affichage des points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, color="black", s=20, zorder=5)

    # Optionnel : triangulation de Delaunay
    if show_delaunay:
        for tri in triangles:
            i, j, k = tri.vertices
            x_tri = [points[i][0], points[j][0], points[k][0], points[i][0]]
            y_tri = [points[i][1], points[j][1], points[k][1], points[i][1]]
            ax.plot(x_tri, y_tri, color="blue", linewidth=0.8, alpha=0.7)

    ax.set_title("Diagramme de Voronoï (et triangulation de Delaunay optionnelle)")
    return fig


def main():
    st.set_page_config(page_title="Voronoï / Delaunay - Watson", layout="wide")
    st.title("Diagramme de Voronoï à partir de la triangulation de Delaunay (Watson)")

    st.sidebar.header("Configuration des données")
    folder = st.sidebar.text_input(
        "Chemin du dossier contenant les fichiers de points (.json / .txt)",
        value="",
        help="Exemple : /home/user/points_data",
    )

    files = list_point_files(folder)
    if not folder:
        st.info("Veuillez saisir un chemin de dossier dans la barre latérale.")
        return

    if not os.path.isdir(folder):
        st.error("Le chemin fourni n'est pas un dossier valide.")
        return

    if not files:
        st.warning("Aucun fichier .json ou .txt trouvé dans ce dossier.")
        return

    selected_file = st.sidebar.selectbox("Fichier de points", files)
    show_delaunay = st.sidebar.checkbox("Afficher la triangulation de Delaunay", value=True)

    full_path = os.path.join(folder, selected_file)

    st.write(f"**Fichier sélectionné :** `{selected_file}`")

    # Chargement des points
    try:
        points = load_points_from_file(full_path)
    except Exception as e:
        st.error(f"Erreur lors du chargement des points : {e}")
        return

    if len(points) < 3:
        st.error("Il faut au moins 3 points pour construire une triangulation de Delaunay.")
        return

    st.write(f"Nombre de points chargés : **{len(points)}**")

    # Calcul Delaunay + Voronoï
    try:
        triangles = compute_delaunay_triangulation(points)
    except Exception as e:
        st.error(f"Erreur lors du calcul de la triangulation de Delaunay : {e}")
        return

    try:
        voronoi_cells = build_voronoi_cells(points, triangles)
    except Exception as e:
        st.error(f"Erreur lors de la construction du diagramme de Voronoï : {e}")
        return

    # Affichage
    fig = plot_voronoi_and_delaunay(points, triangles, voronoi_cells, show_delaunay)

    col_plot, col_dl = st.columns([3, 1])

    with col_plot:
        st.pyplot(fig, use_container_width=True)

    # Export SVG / PNG
    with col_dl:
        st.subheader("Export")

        # PNG
        png_buffer = io.BytesIO()
        fig.savefig(png_buffer, format="png", bbox_inches="tight")
        png_buffer.seek(0)
        st.download_button(
            label="Télécharger PNG",
            data=png_buffer,
            file_name="voronoi.png",
            mime="image/png",
        )

        # SVG
        svg_buffer = io.BytesIO()
        fig.savefig(svg_buffer, format="svg", bbox_inches="tight")
        svg_buffer.seek(0)
        st.download_button(
            label="Télécharger SVG",
            data=svg_buffer,
            file_name="voronoi.svg",
            mime="image/svg+xml",
        )


if __name__ == "__main__":
    main()
