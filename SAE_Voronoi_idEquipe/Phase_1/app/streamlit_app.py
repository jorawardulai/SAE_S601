#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io

import streamlit as st
from pathlib import Path
from PIL import Image


# ------------------ PAGE PRINCIPALE ------------------
st.title("Diagramme de Voronoï")
st.write("Uploade un fichier de points")

uploaded_file = st.file_uploader("Choisis un fichier", type=["json", "txt","csv"])


# Recupere l'image depuis le backend

#Afficher l'image 
st.pyplot("??")
st.download_button("Télecharger l'image en SVG",data= io.BytesIO("??"),file_name="voronoi.svg",mime="image/svg+xml")
st.download_button("Télecharger l'image en PNG",data= io.BytesIO("??"),file_name="voronoi.png",mime="image/png")


