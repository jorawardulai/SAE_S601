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
        st.write("Dessin du diagramme de Voronoï :")
        st.pyplot(dessin)

        

    except Exception as e:
        st.error(traceback.format_exc())

# Recupere l'image depuis le backend

#Afficher l'image 
#st.pyplot("??")
#st.download_button("Télecharger l'image en SVG",data= io.BytesIO("??"),file_name="voronoi.svg",mime="image/svg+xml")
#st.download_button("Télecharger l'image en PNG",data= io.BytesIO("??"),file_name="voronoi.png",mime="image/png")


