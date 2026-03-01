"""
Tests unitaires — Diagramme de Voronoï (architecture modulaire)
===============================================================
Couvre :
  - geometry.primitives  : pts_equal, edge_equal
  - geometry.triangle    : Triangle (circumcircle, in_circumcircle, edges, has_supervertex)
  - algorithms.delaunay  : bowyer_watson (cas limites, propriété Delaunay, formule d'Euler)
  - algorithms.clipping  : sutherland_hodgman
  - algorithms.voronoi   : compute_voronoi (couverture, géométrie)
  - loaders.parser            : parse_json, parse_txt
  - visualization.colors : generate_colors

Lancement depuis la racine du projet :
    python -m pytest tests/test_voronoi.py -v
    python tests/test_voronoi.py
"""

import sys
import os
import math
import json
import random
import unittest
from unittest.mock import MagicMock

# ─────────────────────────────────────────────────────────────────────────────
#  Résolution du chemin — fonctionne depuis tests/ ou depuis la racine
# ─────────────────────────────────────────────────────────────────────────────

_here   = os.path.dirname(os.path.abspath(__file__))
_root   = os.path.dirname(_here)   # dossier parent = racine du projet

# On ajoute la racine au path pour que "from geometry import ..." fonctionne
if _root not in sys.path:
    sys.path.insert(0, _root)

# Neutraliser Streamlit et Matplotlib avant tout import des modules métier
for _mod in [
    "streamlit",
    "matplotlib", "matplotlib.pyplot", "matplotlib.patches",
    "matplotlib.collections", "matplotlib.colors", "matplotlib.figure",
]:
    sys.modules.setdefault(_mod, MagicMock())

# ── Imports des modules à tester ─────────────────────────────────────────────

from geometry.primitives import EPS, pts_equal, edge_equal
from geometry.triangle   import Triangle
from algorithms.delaunay import bowyer_watson
from algorithms.clipping import sutherland_hodgman
from algorithms.voronoi  import compute_voronoi
from loaders.parser           import parse_json, parse_txt
from visualization.colors import generate_colors, Palette


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers de test
# ─────────────────────────────────────────────────────────────────────────────

def nearly(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) < tol


def point_in_polygon(px: float, py: float, polygon: list) -> bool:
    """Ray-casting : True si (px, py) est à l'intérieur du polygone."""
    n, inside, j = len(polygon), False, len(polygon) - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def random_points(n: int, seed: int = 0, lo: float = 0.0, hi: float = 500.0) -> list:
    rng = random.Random(seed)
    return [(rng.uniform(lo, hi), rng.uniform(lo, hi)) for _ in range(n)]


def make_bbox(points: list, margin: float = 30.0) -> tuple:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs) - margin, max(xs) + margin,
            min(ys) - margin, max(ys) + margin)


def run_voronoi(points: list, margin: float = 30.0):
    triangles = bowyer_watson(points)
    bbox      = make_bbox(points, margin)
    cells     = compute_voronoi(points, triangles, bbox)
    return triangles, bbox, cells


# ═════════════════════════════════════════════════════════════════════════════
#  1. geometry.primitives
# ═════════════════════════════════════════════════════════════════════════════

class TestPtsEqual(unittest.TestCase):

    def test_points_identiques(self):
        self.assertTrue(pts_equal((1.0, 2.0), (1.0, 2.0)))

    def test_points_differents(self):
        self.assertFalse(pts_equal((1.0, 2.0), (1.0, 3.0)))
        self.assertFalse(pts_equal((0.0, 0.0), (1e-8, 0.0)))

    def test_dans_tolerance_eps(self):
        self.assertTrue(pts_equal((0.0, 0.0), (EPS / 2, 0.0)))

    def test_origine(self):
        self.assertTrue(pts_equal((0.0, 0.0), (0.0, 0.0)))

    def test_grands_nombres(self):
        self.assertTrue(pts_equal((1e9, 1e9), (1e9, 1e9)))
        self.assertFalse(pts_equal((1e9, 1e9), (1e9 + 1, 1e9)))


class TestEdgeEqual(unittest.TestCase):

    A, B, C = (0.0, 0.0), (1.0, 0.0), (0.5, 1.0)

    def test_meme_orientation(self):
        self.assertTrue(edge_equal((self.A, self.B), (self.A, self.B)))

    def test_orientation_inverse(self):
        self.assertTrue(edge_equal((self.A, self.B), (self.B, self.A)))

    def test_aretes_differentes(self):
        self.assertFalse(edge_equal((self.A, self.B), (self.A, self.C)))

    def test_arete_degeneree(self):
        self.assertFalse(edge_equal((self.A, self.A), (self.A, self.B)))


# ═════════════════════════════════════════════════════════════════════════════
#  2. geometry.triangle
# ═════════════════════════════════════════════════════════════════════════════

class TestTriangleCircumcircle(unittest.TestCase):

    def test_triangle_equilateral(self):
        # A(0,0) B(2,0) C(1,√3) → CC = (1, 1/√3)
        t = Triangle((0.0, 0.0), (2.0, 0.0), (1.0, math.sqrt(3)))
        cx, cy = t.circumcenter
        self.assertTrue(nearly(cx, 1.0))
        self.assertTrue(nearly(cy, 1 / math.sqrt(3)))

    def test_triangle_rectangle(self):
        # A(0,0) B(4,0) C(0,3) → CC = milieu hypoténuse = (2, 1.5)
        t = Triangle((0.0, 0.0), (4.0, 0.0), (0.0, 3.0))
        cx, cy = t.circumcenter
        self.assertTrue(nearly(cx, 2.0))
        self.assertTrue(nearly(cy, 1.5))

    def test_rayon_carre_coherent_avec_tous_sommets(self):
        t = Triangle((0.0, 0.0), (4.0, 0.0), (0.0, 3.0))
        ccx, ccy = t.circumcenter
        r2 = t.circumradius2
        for vx, vy in [(0, 0), (4, 0), (0, 3)]:
            self.assertTrue(nearly((vx - ccx) ** 2 + (vy - ccy) ** 2, r2, tol=1e-9))

    def test_triangle_degenere_circumcenter_infini(self):
        t = Triangle((0.0, 0.0), (1.0, 0.0), (2.0, 0.0))
        cx, cy = t.circumcenter
        self.assertTrue(math.isinf(cx) or math.isinf(cy))

    def test_evaluation_paresseuse(self):
        t = Triangle((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))
        self.assertIsNone(t._cc)
        _ = t.circumcenter
        self.assertIsNotNone(t._cc)
        ref = t._cc
        _ = t.circumcenter
        self.assertIs(t._cc, ref)  # pas recalculé


class TestTriangleInCircumcircle(unittest.TestCase):

    def setUp(self):
        # Triangle inscrit dans le cercle unité centré en (0,0)
        self.t = Triangle((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0))

    def test_centre_interieur(self):
        self.assertTrue(self.t.in_circumcircle((0.0, 0.0)))

    def test_point_exterieur(self):
        self.assertFalse(self.t.in_circumcircle((10.0, 10.0)))

    def test_point_exactement_sur_le_cercle(self):
        # (0, -1) est sur le cercle → pas strictement intérieur
        self.assertFalse(self.t.in_circumcircle((0.0, -1.0)))

    def test_triangle_degenere_rejette_tout(self):
        t = Triangle((0.0, 0.0), (1.0, 0.0), (2.0, 0.0))
        self.assertFalse(t.in_circumcircle((1.0, 0.5)))


class TestTriangleEdgesAndSupervertex(unittest.TestCase):

    def test_edges_retourne_exactement_3_aretes(self):
        self.assertEqual(len(Triangle((0,0),(1,0),(0,1)).edges()), 3)

    def test_edges_couvrent_tous_les_sommets(self):
        A, B, C = (0,0), (1,0), (0,1)
        flat = [v for e in Triangle(A, B, C).edges() for v in e]
        for s in [A, B, C]:
            self.assertIn(s, flat)

    def test_has_supervertex_detecte_sommet_present(self):
        S1, S2, S3 = (-100, -100), (0, 100), (100, -100)
        self.assertTrue(Triangle(S1, (1,1), (2,1)).has_supervertex((S1, S2, S3)))

    def test_has_supervertex_absent(self):
        self.assertFalse(Triangle((0,0),(1,0),(0,1)).has_supervertex(
            ((-100,-100),(0,100),(100,-100))
        ))


# ═════════════════════════════════════════════════════════════════════════════
#  3. algorithms.delaunay (Bowyer-Watson)
# ═════════════════════════════════════════════════════════════════════════════

class TestBowyerWatsonCasLimites(unittest.TestCase):

    def test_zero_point(self):
        self.assertEqual(bowyer_watson([]), [])

    def test_un_point(self):
        self.assertEqual(bowyer_watson([(0, 0)]), [])

    def test_deux_points(self):
        self.assertEqual(bowyer_watson([(0, 0), (1, 0)]), [])

    def test_trois_points_produit_un_triangle(self):
        self.assertEqual(len(bowyer_watson([(0,0),(1,0),(0,1)])), 1)

    def test_points_colineaires_ne_leve_pas_exception(self):
        self.assertIsInstance(bowyer_watson([(i, 0) for i in range(4)]), list)


class TestBowyerWatsonProprietes(unittest.TestCase):

    _CONFIGS = [
        ("carré",     [(0,0),(1,0),(1,1),(0,1)],                               2),
        ("pentagone", [(math.cos(2*math.pi*i/5), math.sin(2*math.pi*i/5))
                       for i in range(5)],                                      3),
        ("15 pts",    random_points(15, seed=1),                               None),
        ("30 pts",    random_points(30, seed=2),                               None),
        ("100 pts",   random_points(100, seed=3),                              None),
    ]

    def _count_delaunay_violations(self, points, triangles):
        return sum(
            1
            for tri in triangles
            for p in points
            if not any(pts_equal(v, p) for v in (tri.a, tri.b, tri.c))
            and tri.in_circumcircle(p)
        )

    def test_propriete_delaunay(self):
        for name, pts, _ in self._CONFIGS:
            with self.subTest(config=name):
                tris = bowyer_watson(pts)
                self.assertEqual(
                    self._count_delaunay_violations(pts, tris), 0,
                    f"{name} : violation de la propriété de Delaunay"
                )

    def test_nombre_triangles_formule_euler(self):
        for name, pts, expected in self._CONFIGS:
            with self.subTest(config=name):
                tris = bowyer_watson(pts)
                n = len(pts)
                self.assertGreaterEqual(len(tris), n - 2)
                self.assertLessEqual(len(tris), 2 * n)
                if expected is not None:
                    self.assertEqual(len(tris), expected,
                        f"{name} : attendu {expected}, obtenu {len(tris)}")

    def test_aucun_sommet_super_triangle(self):
        pts = random_points(50, seed=42)
        tris = bowyer_watson(pts)
        pt_set = {(round(p[0], 4), round(p[1], 4)) for p in pts}
        for tri in tris:
            for v in (tri.a, tri.b, tri.c):
                self.assertIn((round(v[0], 4), round(v[1], 4)), pt_set,
                    f"Sommet hors-liste : {v}")

    def test_tous_points_dans_au_moins_un_triangle(self):
        pts = random_points(20, seed=9)
        tris = bowyer_watson(pts)
        used = {
            i
            for tri in tris
            for v in (tri.a, tri.b, tri.c)
            for i, p in enumerate(pts)
            if pts_equal(v, p)
        }
        for i in range(len(pts)):
            self.assertIn(i, used, f"Point #{i} absent de la triangulation")

    def test_determinisme(self):
        pts = random_points(25, seed=77)
        self.assertEqual(len(bowyer_watson(pts[:])), len(bowyer_watson(pts[:])))


# ═════════════════════════════════════════════════════════════════════════════
#  4. algorithms.clipping (Sutherland-Hodgman)
# ═════════════════════════════════════════════════════════════════════════════

class TestSutherlandHodgman(unittest.TestCase):

    _BBOX = (0.0, 10.0, 0.0, 10.0)

    def _clip(self, poly):
        return sutherland_hodgman(poly, *self._BBOX)

    def _all_inside(self, pts):
        return all(
            -1e-9 <= x <= 10 + 1e-9 and -1e-9 <= y <= 10 + 1e-9
            for x, y in pts
        )

    def test_polygone_entierement_interieur_inchange(self):
        result = self._clip([(1,1),(9,1),(9,9),(1,9)])
        self.assertEqual(len(result), 4)

    def test_polygone_entierement_exterieur_vide(self):
        self.assertEqual(self._clip([(20,20),(30,20),(30,30),(20,30)]), [])

    def test_polygone_partiel_tous_sommets_dans_bbox(self):
        result = self._clip([(-3,5),(5,13),(13,5),(5,-3)])
        self.assertGreater(len(result), 4)
        self.assertTrue(self._all_inside(result))

    def test_triangle_depassant_un_cote(self):
        result = self._clip([(2,2),(12,5),(2,8)])
        self.assertGreaterEqual(len(result), 3)
        self.assertTrue(self._all_inside(result))

    def test_entree_vide(self):
        self.assertEqual(self._clip([]), [])

    def test_polygone_sur_frontiere_exact(self):
        self.assertEqual(len(self._clip([(0,0),(10,0),(10,10),(0,10)])), 4)

    def test_polygone_aleatoire_toujours_dans_bbox(self):
        rng = random.Random(123)
        poly = [(rng.uniform(-20, 20), rng.uniform(-20, 20)) for _ in range(12)]
        self.assertTrue(self._all_inside(self._clip(poly)))


# ═════════════════════════════════════════════════════════════════════════════
#  5. algorithms.voronoi (compute_voronoi)
# ═════════════════════════════════════════════════════════════════════════════

class TestComputeVoronoiCouverture(unittest.TestCase):
    """Tous les points doivent avoir une cellule (y compris le hull)."""

    def _assert_full_coverage(self, n, seed):
        pts = random_points(n, seed=seed)
        _, _, cells = run_voronoi(pts)
        self.assertEqual(len(cells), n,
            f"n={n} seed={seed} : {n - len(cells)} point(s) sans cellule")

    def test_6_points(self):   self._assert_full_coverage(6,   0)
    def test_15_points(self):  self._assert_full_coverage(15,  1)
    def test_30_points(self):  self._assert_full_coverage(30,  2)
    def test_55_points(self):  self._assert_full_coverage(55,  7)
    def test_100_points(self): self._assert_full_coverage(100, 42)

    def test_points_sur_enveloppe_convexe(self):
        # 4 coins + 1 centre
        pts = [(0,0),(10,0),(10,10),(0,10),(5,5)]
        _, _, cells = run_voronoi(pts)
        self.assertEqual(len(cells), 5)

    def test_grille_reguliere(self):
        pts = [(float(x), float(y)) for x in range(5) for y in range(5)]
        _, _, cells = run_voronoi(pts)
        self.assertEqual(len(cells), 25)

    def test_minimum_3_points(self):
        pts = [(0.0, 0.0), (10.0, 0.0), (5.0, 8.0)]
        _, _, cells = run_voronoi(pts)
        self.assertEqual(len(cells), 3)


class TestComputeVoronoiGeometrie(unittest.TestCase):
    """Propriétés géométriques des cellules."""

    def test_chaque_site_dans_sa_cellule(self):
        pts = random_points(20, seed=5)
        _, _, cells = run_voronoi(pts)
        for i, poly in cells.items():
            px, py = pts[i]
            self.assertTrue(
                point_in_polygon(px, py, poly),
                f"Site #{i} {pts[i]} n'est pas dans sa cellule"
            )

    def test_cellules_dans_la_bbox(self):
        pts = random_points(30, seed=6)
        _, bbox, cells = run_voronoi(pts)
        xmin, xmax, ymin, ymax = bbox
        tol = 1e-6
        for i, poly in cells.items():
            for x, y in poly:
                self.assertGreaterEqual(x, xmin - tol, f"cellule {i}: x={x:.4f} < xmin")
                self.assertLessEqual(x,   xmax + tol, f"cellule {i}: x={x:.4f} > xmax")
                self.assertGreaterEqual(y, ymin - tol, f"cellule {i}: y={y:.4f} < ymin")
                self.assertLessEqual(y,   ymax + tol, f"cellule {i}: y={y:.4f} > ymax")

    def test_cellules_ont_au_moins_3_sommets(self):
        _, _, cells = run_voronoi(random_points(25, seed=8))
        for i, poly in cells.items():
            self.assertGreaterEqual(len(poly), 3, f"Cellule #{i} : polygone invalide")

    def test_aucun_site_dans_la_cellule_dun_autre(self):
        pts = random_points(12, seed=10)
        _, _, cells = run_voronoi(pts)
        for i, poly_i in cells.items():
            for j, poly_j in cells.items():
                if i == j:
                    continue
                px, py = pts[i]
                if point_in_polygon(px, py, poly_j):
                    dx = pts[i][0] - pts[j][0]
                    dy = pts[i][1] - pts[j][1]
                    self.assertLess(math.sqrt(dx*dx + dy*dy), 1.0,
                        f"Site #{i} dans la cellule #{j} (points non quasi-confondus)")


# ═════════════════════════════════════════════════════════════════════════════
#  6. loaders.parser
# ═════════════════════════════════════════════════════════════════════════════

class TestParseJson(unittest.TestCase):

    def test_liste_de_listes(self):
        self.assertEqual(parse_json("[[1.0,2.0],[3.0,4.5]]"),
                         [(1.0, 2.0), (3.0, 4.5)])

    def test_dict_avec_cle_points(self):
        self.assertEqual(parse_json('{"points":[[10,20],[30,40]]}'),
                         [(10.0, 20.0), (30.0, 40.0)])

    def test_liste_de_dicts_x_y(self):
        self.assertEqual(parse_json('[{"x":1.5,"y":2.5},{"x":3.0,"y":4.0}]'),
                         [(1.5, 2.5), (3.0, 4.0)])

    def test_entiers_convertis_en_float(self):
        for x, y in parse_json("[[0,0],[1,1]]"):
            self.assertIsInstance(x, float)
            self.assertIsInstance(y, float)

    def test_liste_vide(self):
        self.assertEqual(parse_json("[]"), [])

    def test_json_invalide_leve_exception(self):
        with self.assertRaises(Exception):
            parse_json('"chaine_simple"')

    def test_grands_nombres(self):
        pts = parse_json("[[1e9,-1e9]]")
        self.assertAlmostEqual(pts[0][0],  1e9)
        self.assertAlmostEqual(pts[0][1], -1e9)


class TestParseTxt(unittest.TestCase):

    def test_separateur_espace(self):
        self.assertEqual(parse_txt("1.0 2.0\n3.0 4.0"),
                         [(1.0, 2.0), (3.0, 4.0)])

    def test_separateur_virgule(self):
        self.assertEqual(parse_txt("1.0,2.0\n3.0,4.0"),
                         [(1.0, 2.0), (3.0, 4.0)])

    def test_separateur_parentheses(self):
        self.assertEqual(parse_txt("(1.0, 2.0)\n(3.0, 4.0)"),
                         [(1.0, 2.0), (3.0, 4.0)])

    def test_separateur_point_virgule(self):
        self.assertEqual(parse_txt("1.0;2.0\n3.0;4.0"),
                         [(1.0, 2.0), (3.0, 4.0)])

    def test_commentaires_ignores(self):
        self.assertEqual(parse_txt("# commentaire\n1.0 2.0\n# autre\n3.0 4.0"),
                         [(1.0, 2.0), (3.0, 4.0)])

    def test_lignes_vides_ignorees(self):
        self.assertEqual(parse_txt("\n1.0 2.0\n\n3.0 4.0\n"),
                         [(1.0, 2.0), (3.0, 4.0)])

    def test_contenu_vide(self):
        self.assertEqual(parse_txt(""), [])

    def test_nombres_negatifs(self):
        self.assertEqual(parse_txt("-1.5 -2.5\n0.0 0.0"),
                         [(-1.5, -2.5), (0.0, 0.0)])

    def test_notation_scientifique(self):
        pts = parse_txt("1e3 2.5e-1")
        self.assertAlmostEqual(pts[0][0], 1000.0)
        self.assertAlmostEqual(pts[0][1],   0.25)

    def test_espaces_multiples(self):
        self.assertEqual(parse_txt("  1.0   2.0  "), [(1.0, 2.0)])


# ═════════════════════════════════════════════════════════════════════════════
#  7. visualization.colors
# ═════════════════════════════════════════════════════════════════════════════

class TestGenerateColors(unittest.TestCase):

    def test_nombre_de_couleurs_correct(self):
        for n in [1, 5, 20, 100]:
            with self.subTest(n=n):
                self.assertEqual(len(generate_colors(n)), n)

    def test_valeurs_rgb_dans_intervalle_unitaire(self):
        for palette in Palette:
            with self.subTest(palette=palette.value):
                for r, g, b in generate_colors(20, palette=palette.value):
                    self.assertGreaterEqual(r, 0.0)
                    self.assertLessEqual(r,   1.0)
                    self.assertGreaterEqual(g, 0.0)
                    self.assertLessEqual(g,   1.0)
                    self.assertGreaterEqual(b, 0.0)
                    self.assertLessEqual(b,   1.0)

    def test_determinisme_par_seed(self):
        self.assertEqual(
            generate_colors(10, seed=42),
            generate_colors(10, seed=42)
        )

    def test_seeds_differentes_resultats_differents(self):
        self.assertNotEqual(
            generate_colors(10, palette=Palette.RANDOM.value, seed=0),
            generate_colors(10, palette=Palette.RANDOM.value, seed=1)
        )

    def test_toutes_palettes_retournent_n_elements(self):
        for palette in Palette:
            with self.subTest(palette=palette.value):
                self.assertEqual(len(generate_colors(5, palette=palette.value)), 5)

    def test_une_couleur(self):
        colors = generate_colors(1)
        self.assertEqual(len(colors), 1)
        r, g, b = colors[0]
        self.assertIsInstance(r, float)


# ═════════════════════════════════════════════════════════════════════════════
#  8. Tests d'intégration (pipeline complet)
# ═════════════════════════════════════════════════════════════════════════════

class TestIntegration(unittest.TestCase):

    def test_pipeline_depuis_json(self):
        raw = json.dumps([[50,200],[150,80],[300,350],[420,120],[500,300],
                          [200,450],[350,500],[80,380],[450,420],[250,250]])
        pts = parse_json(raw)
        _, _, cells = run_voronoi(pts)
        self.assertEqual(len(cells), len(pts))

    def test_pipeline_depuis_txt(self):
        content = "\n".join(f"{x},{y}" for x, y in random_points(20, seed=99))
        pts = parse_txt(content)
        _, _, cells = run_voronoi(pts)
        self.assertEqual(len(cells), len(pts))

    def test_pipeline_200_points_couverture_quasi_totale(self):
        pts = random_points(200, seed=123)
        _, _, cells = run_voronoi(pts)
        self.assertGreaterEqual(len(cells) / len(pts), 0.98)

    def test_robustesse_sur_10_graines(self):
        for seed in range(10):
            with self.subTest(seed=seed):
                pts = random_points(25, seed=seed)
                _, _, cells = run_voronoi(pts)
                self.assertEqual(len(cells), len(pts),
                    f"seed={seed}: {len(pts) - len(cells)} point(s) sans cellule")

    def test_points_clusteres(self):
        rng = random.Random(55)
        pts = [
            (cx + rng.uniform(-5, 5), cy + rng.uniform(-5, 5))
            for cx, cy in [(rng.uniform(100, 400), rng.uniform(100, 400))
                           for _ in range(5)]
            for _ in range(5)
        ]
        _, _, cells = run_voronoi(pts)
        self.assertGreater(len(cells), 0)

    def test_grille_reguliere_couverture_totale_et_delaunay(self):
        pts = [(float(i * 10), float(j * 10)) for i in range(6) for j in range(6)]
        tris = bowyer_watson(pts)

        violations = sum(
            1
            for tri in tris
            for p in pts
            if not any(pts_equal(v, p) for v in (tri.a, tri.b, tri.c))
            and tri.in_circumcircle(p)
        )
        self.assertEqual(violations, 0)

        _, _, cells = run_voronoi(pts)
        self.assertEqual(len(cells), len(pts))


# ─────────────────────────────────────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)

    total  = result.testsRun
    passed = total - len(result.failures) - len(result.errors)

    print("\n" + "═" * 60)
    if result.wasSuccessful():
        print(f"  ✅  {passed}/{total} tests réussis")
    else:
        print(f"  ❌  {passed}/{total} réussis  "
              f"({len(result.failures)} échec(s), {len(result.errors)} erreur(s))")
    print("═" * 60)

    sys.exit(0 if result.wasSuccessful() else 1)
