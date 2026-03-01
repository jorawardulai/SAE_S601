"""
Classe Triangle avec calcul paresseux du cercle circonscrit.
"""

import math
from geometry.primitives import EPS, pts_equal


class Triangle:
    """
    Triangle défini par trois sommets (a, b, c).

    Le cercle circonscrit est calculé à la demande (lazy) et mis en cache.
    Pour un triangle dégénéré (points colinéaires), le circumcenter est (∞, ∞).
    """

    __slots__ = ("a", "b", "c", "_cc", "_cr2")

    def __init__(self, a: tuple, b: tuple, c: tuple) -> None:
        self.a = a
        self.b = b
        self.c = c
        self._cc: tuple | None = None   # centre du cercle circonscrit
        self._cr2: float | None = None  # rayon² du cercle circonscrit

    # ── Calcul interne ────────────────────────────────────────────

    def _compute_circumcircle(self) -> None:
        ax, ay = self.a
        bx, by = self.b
        cx, cy = self.c

        D = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

        if abs(D) < EPS:
            self._cc = (math.inf, math.inf)
            self._cr2 = math.inf
            return

        a2 = ax * ax + ay * ay
        b2 = bx * bx + by * by
        c2 = cx * cx + cy * cy

        ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / D
        uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / D

        self._cc = (ux, uy)
        self._cr2 = (ax - ux) ** 2 + (ay - uy) ** 2

    # ── Propriétés publiques ──────────────────────────────────────

    @property
    def circumcenter(self) -> tuple:
        if self._cc is None:
            self._compute_circumcircle()
        return self._cc

    @property
    def circumradius2(self) -> float:
        if self._cr2 is None:
            self._compute_circumcircle()
        return self._cr2

    # ── Méthodes publiques ────────────────────────────────────────

    def in_circumcircle(self, p: tuple) -> bool:
        """Retourne True si p est strictement à l'intérieur du cercle circonscrit."""
        if self._cr2 is None:
            self._compute_circumcircle()
        if self._cr2 == math.inf:
            return False
        ccx, ccy = self._cc
        dx, dy = p[0] - ccx, p[1] - ccy
        return dx * dx + dy * dy < self._cr2 - EPS

    def edges(self) -> list[tuple]:
        """Retourne les 3 arêtes orientées du triangle."""
        return [(self.a, self.b), (self.b, self.c), (self.c, self.a)]

    def has_supervertex(self, super_verts: tuple) -> bool:
        """Retourne True si au moins un sommet appartient au super-triangle."""
        return any(
            pts_equal(self.a, s) or pts_equal(self.b, s) or pts_equal(self.c, s)
            for s in super_verts
        )

    def __repr__(self) -> str:
        return f"Triangle({self.a}, {self.b}, {self.c})"
