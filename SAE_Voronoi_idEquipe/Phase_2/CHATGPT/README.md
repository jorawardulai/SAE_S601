# Voronoï Streamlit (Delaunay Bowyer–Watson, sans SciPy/Shapely)

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # mac/linux
# .venv\Scripts\activate   # windows
pip install -r requirements.txt
```

## Lancer l’app
```bash
streamlit run app/main.py
```

## Formats d’entrée
### TXT
Une paire `x y` par ligne, séparateur espace ou virgule.
Commentaires possibles avec `#`.

Ex:
```
0 0
1,2
3 4
```

### JSON
- `[[x,y], [x,y], ...]`
ou
- `{"points": [{"x":0,"y":0}, ...]}`

## Dossier ou fichier
- Upload Streamlit : 1 fichier.
- Chemin local (champ texte) : un fichier **ou** un dossier ; l’app scanne récursivement `.txt` et `.json`.

## Algo
1) Triangulation Delaunay : Bowyer–Watson (implémenté).
2) Voronoï : construit à partir du graphe de voisinage Delaunay.
   - Les cellules infinies sont rendues finies via **clipping sur une bounding box**.
   - Construction pratique des cellules : intersection de la bbox avec les **demi-plans** des médiatrices entre un site et ses voisins Delaunay.
   - Les circumcenters des triangles Delaunay sont aussi calculés (debug/dualité).

## Tests
```bash
pytest -q
```

## Exports
- PNG / SVG via `download_button`.
