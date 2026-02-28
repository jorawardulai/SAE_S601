from typing import List, Tuple

Point = Tuple[float, float]


def load_points_from_txt(path: str) -> List[Point]:
    """
    Charge une liste de points depuis un fichier texte.

    Format :
        Un point par ligne, deux nombres séparés par des espaces (ou tabulations) :
            1.2 3.4
            2.0 1.0
            ...
    Les lignes vides ou commentées (#) sont ignorées.
    """
    points: List[Point] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                raise ValueError(f"Ligne {line_no}: au moins deux valeurs sont requises.")
            try:
                x = float(parts[0])
                y = float(parts[1])
            except ValueError:
                raise ValueError(f"Ligne {line_no}: valeurs non numériques.")
            points.append((x, y))
    return points
