import streamlit as st
import json, random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Imports de ton architecture
from domain.models import Point
from logique.engine import VoronoiEngine

class VoronoiApp:
    @staticmethod
    def run():
        st.set_page_config(page_title="Rendu Voronoï Mosaïque", layout="wide")
        st.title("💠 Mosaïque de Voronoï via Bowyer-Watson")
        st.markdown("Uploadez votre fichier pour voir la mosaïque se dessiner.")

        uploaded_file = st.sidebar.file_uploader("JSON (Coordonnées)", type=['json'])

        if uploaded_file:
            data = json.load(uploaded_file)
            pts = [Point(p[0], p[1]) for p in data]
            
            # Exécution stricte de Bowyer-Watson
            engine = VoronoiEngine(pts)
            engine.run_bowyer_watson()
            cells = engine.get_voronoi_cells()

            # --- CORRECTION DU RENDU POUR CORRESPONDRE À L'IMAGE ---
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # Définir des limites strictes basées sur tes points de données
            xs, ys = [p.x for p in pts], [p.y for p in pts]
            margin = 5
            ax.set_xlim(min(xs) - margin, max(xs) + margin)
            ax.set_ylim(min(ys) - margin, max(ys) + margin)
            
            # Pour chaque cellule, générer une couleur aléatoire contrastée
            for p, vertices in cells.items():
                if len(vertices) >= 3:
                    # Couleur aléatoire vive
                    color = [random.uniform(0.1, 0.9) for _ in range(3)]
                    
                    # Le polygone (cellule)
                    poly = Polygon([v.to_tuple() for v in vertices], 
                                   facecolor=color,
                                   # Bordure noire fine
                                   edgecolor='black', 
                                   linewidth=0.5,
                                   closed=True) # Assure que le dernier point rejoint le premier
                    ax.add_patch(poly)

            # Dessin des points générateurs (petits points noirs)
            ax.scatter(xs, ys, c='black', s=10, zorder=10)
            
            # Paramètres de plot pour un rendu mosaïque pur
            ax.set_aspect('equal')
            plt.axis('off') # Cache les axes
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0) # Maximise l'espace
            
            st.pyplot(fig)

            # Exportation (PNG)
            import io
            png_buf = io.BytesIO()
            fig.savefig(png_buf, format='png', bbox_inches='tight')
            st.download_button("💾 Télécharger la Mosaïque (PNG)", png_buf.getvalue(), "mosaique.png")

if __name__ == "__main__":
    VoronoiApp.run()