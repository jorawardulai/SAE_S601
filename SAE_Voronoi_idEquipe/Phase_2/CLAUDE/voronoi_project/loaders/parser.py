"""
Parseurs de fichiers sources pour les points 2D.

Formats JSON supportés :
  - [[x1, y1], [x2, y2], ...]
  - {"points": [[x1, y1], ...]}
  - [{"x": x1, "y": y1}, ...]

Formats TXT supportés (une paire par ligne) :
  - "x y"    (espace)
  - "x,y"    (virgule)
  - "(x, y)" (parenthèses)
  - "x;y"    (point-virgule)
  - Les lignes vides et commentaires (#) sont ignorés.
"""

import json
from typing import IO


def parse_json(content: str) -> list[tuple]:
    """
    Parse un contenu JSON en liste de points (x, y).

    Raises:
        ValueError: si le format JSON n'est pas reconnu.
        json.JSONDecodeError: si le contenu n'est pas du JSON valide.
    """
    data = json.loads(content)

    if isinstance(data, list):
        if not data:
            return []
        if isinstance(data[0], (list, tuple)):
            return [(float(p[0]), float(p[1])) for p in data]
        if isinstance(data[0], dict):
            return [(float(p["x"]), float(p["y"])) for p in data]

    if isinstance(data, dict):
        pts = data.get("points", data.get("Points", []))
        return parse_json(json.dumps(pts))

    raise ValueError(
        "Format JSON non reconnu. "
        "Attendu : [[x,y],...], {\"points\":[[x,y],...]}, ou [{\"x\":...,\"y\":...},...]"
    )


def parse_txt(content: str) -> list[tuple]:
    """
    Parse un contenu texte en liste de points (x, y).

    Chaque ligne non-vide et non-commentaire doit contenir exactement
    deux valeurs numériques séparées par un espace, virgule ou point-virgule.
    """
    points = []

    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        line = line.strip("()")
        sep = _detect_separator(line)
        parts = line.split(sep) if sep else line.split()

        if len(parts) >= 2:
            points.append((float(parts[0].strip()), float(parts[1].strip())))

    return points


def load_points(uploaded_file: IO) -> list[tuple]:
    """
    Charge des points depuis un fichier uploadé (Streamlit).

    Détecte le format à partir de l'extension ; en l'absence d'extension
    connue, essaie JSON puis TXT.

    Args:
        uploaded_file: objet fichier avec attributs `.name` et `.read()`.

    Returns:
        Liste de tuples (x, y).
    """
    content = uploaded_file.read().decode("utf-8")
    name = uploaded_file.name.lower()

    if name.endswith(".json"):
        return parse_json(content)
    if name.endswith(".txt"):
        return parse_txt(content)

    # Détection automatique
    try:
        return parse_json(content)
    except Exception:
        return parse_txt(content)


# ── Helpers privés ────────────────────────────────────────────────────────────

def _detect_separator(line: str) -> str | None:
    """Détecte le séparateur utilisé dans une ligne."""
    if "," in line:
        return ","
    if ";" in line:
        return ";"
    return None  # espace par défaut
