# 🔷 Diagramme de Voronoï – Streamlit App

## Lancement

```bash
pip install streamlit matplotlib
streamlit run voronoi_app.py
```

## Formats de fichiers acceptés

### JSON
```json
[[x1, y1], [x2, y2], ...]
{"points": [[x1, y1], ...]}
[{"x": 1.0, "y": 2.0}, ...]
```

### TXT (une paire par ligne)
```
x y
x,y
(x, y)
x;y
```

## Architecture

| Module | Description |
|--------|-------------|
| `Triangle` | Classe géométrique avec calcul exact du cercle circonscrit |
| `bowyer_watson()` | Triangulation de Delaunay – algorithme incrémental |
| `compute_voronoi()` | Dérivation des cellules Voronoï depuis les circumcentres |
| `sutherland_hodgman()` | Clipping des cellules sur la bounding-box |

## Algorithme

1. **Bowyer-Watson** : insertion incrémentale des points avec
   - Super-triangle englobant
   - Détection des "mauvais" triangles (point dans le cercle circonscrit)
   - Reconstruction du trou polygonal
   - Suppression des artefacts du super-triangle

2. **Voronoï depuis Delaunay** :
   - Les circumcentres des triangles adjacents à un site = sommets de la cellule
   - Tri angulaire pour obtenir l'ordre polygonal
   - Clipping Sutherland-Hodgman sur la bbox
