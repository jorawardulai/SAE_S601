"""
README / Exemple d'utilisation
==============================

1. Installation des dépendances (dans un venv de préférence) :

    pip install streamlit matplotlib numpy

2. Lancer l'application Streamlit :

    streamlit run app.py

3. Préparation des fichiers de points :

   - Créer un dossier, par exemple `data/`.
   - Y placer des fichiers `.json` ou `.txt`.

   Formats acceptés :

   JSON :
     - Liste d'objets : [ {"x": 1.2, "y": 3.4}, {"x": 2.0, "y": 1.0}, ... ]
     - Liste de listes : [ [1.2, 3.4], [2.0, 1.0], ... ]

   TXT :
     - Un point par ligne, séparé par des espaces :
       1.2 3.4
       2.0 1.0
       ...

4. Dans l'interface Streamlit :

   - Saisir le chemin du dossier contenant les fichiers de points.
   - Choisir un fichier dans la liste.
   - Visualiser les points, le diagramme de Voronoï, et éventuellement la triangulation de Delaunay.
   - Utiliser les boutons pour exporter le diagramme en SVG ou PNG.

"""

import io
import os
from typing import List, Tuple

import matplotlib.pyplot as plt
import streamlit as st

from point_io.loader import load_points_from_file
from geometry.delaunay import compute_delaunay_triangulation
from geometry.voronoi import build_voronoi_diagram


Point = Tuple[float, float]


def list_point_files(folder: str) -> List[str]:
    """Retourne la liste des fichiers .json et .txt dans un dossier."""
    if not os.path.isdir(folder):
        return []
    files = []
    for name in os.listdir(folder):
        if name.lower().endswith(".json") or name.lower().endswith(".txt"):
            files.append(name)
    return sorted(files)


def create_voronoi_figure(
    points: List[Point],
    voronoi_cells: dict,
    triangles: List[Tuple[int, int, int]],
    show_delaunay: bool,
):
    """Crée une figure matplotlib avec Voronoï + points (+ Delaunay optionnel)."""
    fig, ax = plt.subplots(figsize=(6, 6))

    # Points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, c="black", s=20, zorder=3)

    # Couleurs pour les cellules
    cmap = plt.get_cmap("tab20")
    n_colors = len(points) if points else 1

    for idx, cell in voronoi_cells.items():
        if not cell:
            continue
        color = cmap(idx % 20)
        poly_x = [p[0] for p in cell]
        poly_y = [p[1] for p in cell]
        ax.fill(poly_x, poly_y, color=color, alpha=0.4, edgecolor="k", linewidth=0.5)

    # Delaunay (optionnel)
    if show_delaunay:
        for (i, j, k) in triangles:
            x_tri = [points[i][0], points[j][0], points[k][0], points[i][0]]
            y_tri = [points[i][1], points[j][1], points[k][1], points[i][1]]
            ax.plot(x_tri, y_tri, color="gray", linewidth=0.8, alpha=0.7, zorder=2)

    ax.set_aspect("equal", "box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Diagramme de Voronoï (et triangulation de Delaunay optionnelle)")
    ax.grid(True, linestyle="--", alpha=0.3)

    return fig


def main():
    st.title("Diagramme de Voronoï / Triangulation de Delaunay (Watson)")

    st.markdown(
        """
        Cette application :
        - Lit des points 2D depuis des fichiers `.json` ou `.txt` dans un dossier.
        - Construit une triangulation de Delaunay via l'algorithme de Watson (insertion incrémentale).
        - Construit le diagramme de Voronoï dual.
        - Affiche le résultat et permet l'export en SVG et PNG.
        """
    )

    folder = st.text_input(
        "Chemin du dossier contenant les fichiers de points",
        value="data",
        help="Saisis un chemin valide sur le système de fichiers du serveur.",
    )

    files = list_point_files(folder)
    if not files:
        st.info("Aucun fichier .json ou .txt trouvé dans ce dossier.")
        return

    file_name = st.selectbox("Choisir un fichier de points", files)
    file_path = os.path.join(folder, file_name)

    show_delaunay = st.checkbox("Afficher la triangulation de Delaunay", value=True)

    if st.button("Charger et calculer"):
        try:
            points = load_points_from_file(file_path)
        except Exception as e:
            st.error(f"Erreur lors du chargement des points : {e}")
            return

        if len(points) < 3:
            st.error("Il faut au moins 3 points pour construire une triangulation de Delaunay.")
            return

        try:
            triangles, super_indices = compute_delaunay_triangulation(points)
        except Exception as e:
            st.error(f"Erreur lors du calcul de la triangulation de Delaunay : {e}")
            return

        try:
            voronoi_cells, bbox = build_voronoi_diagram(points, triangles, super_indices)
        except Exception as e:
            st.error(f"Erreur lors de la construction du diagramme de Voronoï : {e}")
            return

        st.success("Calcul terminé.")

        fig = create_voronoi_figure(points, voronoi_cells, triangles, show_delaunay)
        st.pyplot(fig)

        # Export SVG
        svg_buffer = io.BytesIO()
        fig.savefig(svg_buffer, format="svg", bbox_inches="tight")
        svg_buffer.seek(0)
        st.download_button(
            label="Télécharger le diagramme en SVG",
            data=svg_buffer,
            file_name="voronoi_diagram.svg",
            mime="image/svg+xml",
        )

        # Export PNG
        png_buffer = io.BytesIO()
        fig.savefig(png_buffer, format="png", dpi=300, bbox_inches="tight")
        png_buffer.seek(0)
        st.download_button(
            label="Télécharger le diagramme en PNG",
            data=png_buffer,
            file_name="voronoi_diagram.png",
            mime="image/png",
        )


if __name__ == "__main__":
    main()
