#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import tempfile
import streamlit as st
import traceback

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.io_points import importFichier
from src.voronoi import calculer_diagramme
from src.render import dessiner_diagramme


st.title("Diagramme de Voronoï")

uploaded_file = st.file_uploader("Importer un fichier avec les points", type=["json", "txt","csv"])

if uploaded_file is not None:

    try: 
        coordonnee = importFichier(uploaded_file)
        st.success("Fichier importé avec succès !")
        
        diagramme = calculer_diagramme(coordonnee)
       
        dessin = dessiner_diagramme(diagramme)
        st.write("Diagramme de Voronoï généré:")
        st.pyplot(dessin)

        # --- EXPORT PNG ---
        png_buffer = io.BytesIO()
        dessin.savefig(png_buffer, format="png", bbox_inches="tight")
        png_buffer.seek(0)

        st.download_button(
            "Télécharger en PNG",
            data=png_buffer,
            file_name="diagramme_voronoi.png",
            mime="image/png"
        )

        # --- EXPORT SVG ---
        svg_buffer = io.BytesIO()
        dessin.savefig(svg_buffer, format="svg", bbox_inches="tight")
        svg_buffer.seek(0)

        st.download_button(
            "Télécharger en SVG",
            data=svg_buffer,
            file_name="diagramme_voronoi.svg",
            mime="image/svg+xml"
        )
        

    except Exception as e:
        st.error(traceback.format_exc())


