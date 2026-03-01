"""
Génération de palettes de couleurs pour le rendu Voronoï.

Chaque fonction retourne une liste de n tuples (r, g, b) avec r, g, b ∈ [0, 1].
"""

import colorsys
import random
from enum import Enum


class Palette(str, Enum):
    PASTEL = "pastel"
    VIVID  = "vivid"
    EARTH  = "earth"
    RANDOM = "random"


# Couleurs terre pré-calculées en RGB normalisé — indépendant de matplotlib
_EARTH_BASE: list[tuple] = [
    (0.545, 0.435, 0.278),
    (0.627, 0.471, 0.353),
    (0.769, 0.584, 0.416),
    (0.831, 0.663, 0.416),
    (0.710, 0.514, 0.353),
    (0.478, 0.420, 0.314),
    (0.608, 0.549, 0.420),
    (0.784, 0.663, 0.478),
    (0.690, 0.565, 0.376),
    (0.541, 0.439, 0.333),
]


def generate_colors(
    n: int,
    palette: str = Palette.PASTEL,
    seed: int = 42,
) -> list[tuple]:
    """
    Génère n couleurs distinctes selon la palette choisie.

    Args:
        n      : nombre de couleurs à générer.
        palette: nom de la palette (pastel, vivid, earth, random).
        seed   : graine du générateur aléatoire (reproductibilité).

    Returns:
        Liste de n tuples (r, g, b) avec valeurs dans [0, 1].
    """
    generators = {
        Palette.PASTEL: _pastel,
        Palette.VIVID:  _vivid,
        Palette.EARTH:  _earth,
        Palette.RANDOM: _random,
    }
    generator = generators.get(palette, _pastel)
    return generator(n, seed)


# ── Générateurs de palettes ───────────────────────────────────────────────────

def _pastel(n: int, seed: int) -> list[tuple]:
    colors = [
        colorsys.hls_to_rgb(i / max(n, 1), 0.78, 0.65)
        for i in range(n)
    ]
    random.Random(seed).shuffle(colors)
    return colors


def _vivid(n: int, seed: int) -> list[tuple]:
    colors = [
        colorsys.hls_to_rgb(i / max(n, 1), 0.55, 0.85)
        for i in range(n)
    ]
    random.Random(seed).shuffle(colors)
    return colors


def _earth(n: int, _seed: int) -> list[tuple]:
    return [_EARTH_BASE[i % len(_EARTH_BASE)] for i in range(n)]


def _random(n: int, seed: int) -> list[tuple]:
    rng = random.Random(seed)
    return [(rng.random(), rng.random(), rng.random()) for _ in range(n)]
