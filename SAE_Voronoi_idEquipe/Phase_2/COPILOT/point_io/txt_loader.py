from typing import List, Tuple

Point = Tuple[float, float]


def load_points_from_txt(path: str) -> List[Point]:
    """
    Charge une liste de points depuis un fichier texte.

    Format :
      - Un point par ligne, deux nombres séparés par des espaces :
        1.2 3.4
        2.0 1.0
        ...
    """
    points: List[Point] = []

    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) != 2:
                raise ValueError(
                    f"Ligne {line_no}: attendu 2 valeurs (x y), trouvé {len(parts)}."
                )
            try:
                x = float(parts[0])
                y = float(parts[1])
            except ValueError:
                raise ValueError(
                    f"Ligne {line_no}: impossible de convertir en float : '{stripped}'."
                )
            points.append((x, y))

    if len(points) == 0:
        raise ValueError("Aucun point trouvé dans le fichier texte.")

    return points
