import json
from typing import List, Tuple

Point = Tuple[float, float]


def load_points_from_json(path: str) -> List[Point]:
    """
    Charge une liste de points depuis un fichier JSON.

    Formats acceptés :
    - [ {"x": 1.2, "y": 3.4}, {"x": 2.0, "y": 1.0}, ... ]
    - [ [1.2, 3.4], [2.0, 1.0], ... ]
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Le JSON doit contenir une liste.")

    points: List[Point] = []

    for idx, item in enumerate(data):
        if isinstance(item, dict):
            if "x" not in item or "y" not in item:
                raise ValueError(f"Objet à l'index {idx} sans clés 'x' et 'y'.")
            x, y = float(item["x"]), float(item["y"])
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            x, y = float(item[0]), float(item[1])
        else:
            raise ValueError(
                f"Élément à l'index {idx} invalide : doit être dict ou liste/tuple de longueur 2."
            )
        points.append((x, y))

    if len(points) == 0:
        raise ValueError("Aucun point trouvé dans le fichier JSON.")

    return points
