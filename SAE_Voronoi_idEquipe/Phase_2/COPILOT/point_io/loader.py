import os
from typing import List, Tuple

from .json_loader import load_points_from_json
from .txt_loader import load_points_from_txt

Point = Tuple[float, float]


def load_points_from_file(path: str) -> List[Point]:
    """
    Détecte l'extension du fichier et appelle le loader approprié.
    Gère les erreurs de format et fournit des messages explicites.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        return load_points_from_json(path)
    elif ext == ".txt":
        return load_points_from_txt(path)
    else:
        raise ValueError(f"Extension de fichier non supportée : {ext}")
