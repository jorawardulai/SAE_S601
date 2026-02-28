"""
Tests unitaires — Diagramme de Voronoï (Bowyer-Watson)
=======================================================
Couvre :
  - pts_equal / edge_equal
  - Triangle (cercle circonscrit, in_circumcircle, edges, has_supervertex)
  - bowyer_watson  (cas limites, propriété de Delaunay, formule d'Euler)
  - sutherland_hodgman  (clipping)
  - compute_voronoi  (couverture totale, cellules dans la bbox)
  - parse_json / parse_txt  (tous les formats)
  - generate_colors  (taille, déterminisme, valeurs RGB)

Lancement :
    python -m pytest test_voronoi.py -v
    # ou
    python test_voronoi.py
"""

import sys
import math
import types
import random
import json
import unittest
from unittest.mock import MagicMock

# ─────────────────────────────────────────────────────────────
#  Neutraliser les imports Streamlit / Matplotlib avant import
#  du module principal (évite de démarrer un serveur Streamlit)
# ─────────────────────────────────────────────────────────────
for mod_name in [
    "streamlit",
    "matplotlib", "matplotlib.pyplot", "matplotlib.patches",
    "matplotlib.collections", "matplotlib.colors",
]:
    sys.modules.setdefault(mod_name, MagicMock())

import importlib
import os

# ── Résolution du chemin vers voronoi_app.py ─────────────────────────────────
# On cherche dans le dossier du fichier de test EN PREMIER,
# puis dans son dossier parent (cas classique : test/ est un sous-dossier).
_here   = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)

if os.path.isfile(os.path.join(_here, "voronoi_app.py")):
    _app_path = os.path.join(_here, "voronoi_app.py")
elif os.path.isfile(os.path.join(_parent, "voronoi_app.py")):
    _app_path = os.path.join(_parent, "voronoi_app.py")
else:
    raise FileNotFoundError(
        "\n[test_voronoi.py] Impossible de trouver voronoi_app.py.\n"
        f"  → Cherché dans : {_here}\n"
        f"  → Cherché dans : {_parent}\n"
        "  Placez voronoi_app.py dans le même dossier que test_voronoi.py "
        "ou dans son dossier parent."
    )

sys.path.insert(0, os.path.dirname(_app_path))

# Import dynamique pour supporter le module avec "import streamlit as st"
spec = importlib.util.spec_from_file_location("voronoi_app", _app_path)
voronoi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voronoi)

# Raccourcis vers les symboles testés
pts_equal          = voronoi.pts_equal
edge_equal         = voronoi.edge_equal
Triangle           = voronoi.Triangle
bowyer_watson      = voronoi.bowyer_watson
sutherland_hodgman = voronoi.sutherland_hodgman
compute_voronoi    = voronoi.compute_voronoi
parse_json         = voronoi.parse_json
parse_txt          = voronoi.parse_txt
generate_colors    = voronoi.generate_colors
EPS                = voronoi.EPS


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

def nearly(a, b, tol=1e-6):
    """Égalité approchée entre deux flottants."""
    return abs(a - b) < tol


def point_in_polygon(px, py, polygon):
    """Ray-casting : True si (px,py) est à l'intérieur du polygone."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def random_points(n, seed=0, lo=0.0, hi=500.0):
    rng = random.Random(seed)
    return [(rng.uniform(lo, hi), rng.uniform(lo, hi)) for _ in range(n)]


def make_bbox(points, margin=30):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin)


# ═════════════════════════════════════════════════════════════
#  1. PRIMITIVES GÉOMÉTRIQUES
# ═════════════════════════════════════════════════════════════

class TestPtsEqual(unittest.TestCase):

    def test_meme_point(self):
        self.assertTrue(pts_equal((1.0, 2.0), (1.0, 2.0)))

    def test_points_differents(self):
        self.assertFalse(pts_equal((1.0, 2.0), (1.0, 3.0)))
        self.assertFalse(pts_equal((0.0, 0.0), (1e-8, 0.0)))

    def test_dans_tolerance(self):
        # Deux points séparés de < EPS (~1e-10) doivent être considérés égaux
        tiny = EPS / 2
        self.assertTrue(pts_equal((0.0, 0.0), (tiny, 0.0)))

    def test_zero_et_zero(self):
        self.assertTrue(pts_equal((0.0, 0.0), (0.0, 0.0)))

    def test_grands_nombres(self):
        self.assertTrue(pts_equal((1e9, 1e9), (1e9, 1e9)))
        self.assertFalse(pts_equal((1e9, 1e9), (1e9 + 1, 1e9)))


class TestEdgeEqual(unittest.TestCase):

    A = (0.0, 0.0)
    B = (1.0, 0.0)
    C = (0.5, 1.0)

    def test_meme_orientation(self):
        self.assertTrue(edge_equal((self.A, self.B), (self.A, self.B)))

    def test_orientation_inverse(self):
        self.assertTrue(edge_equal((self.A, self.B), (self.B, self.A)))

    def test_aretes_differentes(self):
        self.assertFalse(edge_equal((self.A, self.B), (self.A, self.C)))
        self.assertFalse(edge_equal((self.A, self.B), (self.B, self.C)))

    def test_meme_sommet_des_deux_cotes(self):
        # (A,A) ≠ (A,B)
        self.assertFalse(edge_equal((self.A, self.A), (self.A, self.B)))


# ═════════════════════════════════════════════════════════════
#  2. CLASSE TRIANGLE
# ═════════════════════════════════════════════════════════════

class TestTriangleCircumcircle(unittest.TestCase):
    """Cercle circonscrit — valeurs analytiques connues."""

    def test_triangle_isocele_axe_y(self):
        # Triangle isocèle : A(0,0) B(2,0) C(1,√3) → équilatéral
        # Circumcenter = (1, 1/√3), r = 2/√3
        A, B = (0.0, 0.0), (2.0, 0.0)
        C = (1.0, math.sqrt(3))
        t = Triangle(A, B, C)
        cx, cy = t.circumcenter
        self.assertTrue(nearly(cx, 1.0),         f"cx attendu 1.0, obtenu {cx}")
        self.assertTrue(nearly(cy, 1/math.sqrt(3)), f"cy attendu {1/math.sqrt(3):.6f}, obtenu {cy}")

    def test_triangle_rectangle(self):
        # Triangle rectangle en A : hypothénuse = diamètre du cercle circonscrit
        # A(0,0) B(4,0) C(0,3) → CC = milieu de BC = (2, 1.5)
        A, B, C = (0.0, 0.0), (4.0, 0.0), (0.0, 3.0)
        t = Triangle(A, B, C)
        cx, cy = t.circumcenter
        self.assertTrue(nearly(cx, 2.0), f"cx attendu 2.0, obtenu {cx}")
        self.assertTrue(nearly(cy, 1.5), f"cy attendu 1.5, obtenu {cy}")

    def test_rayon_carre_coherent(self):
        A, B, C = (0.0, 0.0), (4.0, 0.0), (0.0, 3.0)
        t = Triangle(A, B, C)
        cx, cy = t.circumcenter
        r2 = t.circumradius2
        # r² doit égaler la distance² de chaque sommet au circumcenter
        for vx, vy in [(0.0,0.0), (4.0,0.0), (0.0,3.0)]:
            d2 = (vx - cx)**2 + (vy - cy)**2
            self.assertTrue(nearly(d2, r2, tol=1e-9), f"r² incohérent pour ({vx},{vy})")

    def test_triangle_degenere(self):
        # 3 points colinéaires → circumcenter à l'infini
        t = Triangle((0.0, 0.0), (1.0, 0.0), (2.0, 0.0))
        cx, cy = t.circumcenter
        self.assertTrue(math.isinf(cx) or math.isinf(cy))

    def test_lazy_evaluation(self):
        # Le calcul ne doit se faire qu'une fois (propriété _cc cachée)
        t = Triangle((0.0,0.0), (1.0,0.0), (0.0,1.0))
        self.assertIsNone(t._cc)
        _ = t.circumcenter
        self.assertIsNotNone(t._cc)
        cc1 = t._cc
        _ = t.circumcenter
        self.assertIs(t._cc, cc1)  # même objet → pas recalculé


class TestTriangleInCircumcircle(unittest.TestCase):

    def setUp(self):
        # Cercle de rayon 1 centré en (0,0) :
        # Triangle inscrit quelconque
        self.t = Triangle((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0))

    def test_centre_strictement_interieur(self):
        self.assertTrue(self.t.in_circumcircle((0.0, 0.0)))

    def test_point_exterieur(self):
        self.assertFalse(self.t.in_circumcircle((10.0, 10.0)))

    def test_point_sur_le_cercle(self):
        # (0, -1) est exactement sur le cercle → pas strictement intérieur
        self.assertFalse(self.t.in_circumcircle((0.0, -1.0)))

    def test_triangle_degenere_rejette_tout(self):
        t = Triangle((0.0, 0.0), (1.0, 0.0), (2.0, 0.0))
        self.assertFalse(t.in_circumcircle((1.0, 0.5)))


class TestTriangleEdgesAndSupervertex(unittest.TestCase):

    def test_edges_retourne_3_aretes(self):
        t = Triangle((0,0), (1,0), (0,1))
        edges = t.edges()
        self.assertEqual(len(edges), 3)

    def test_edges_contient_tous_les_sommets(self):
        A, B, C = (0,0), (1,0), (0,1)
        t = Triangle(A, B, C)
        flat = [v for e in t.edges() for v in e]
        for s in [A, B, C]:
            self.assertIn(s, flat)

    def test_has_supervertex_detecte(self):
        S1, S2, S3 = (-100, -100), (0, 100), (100, -100)
        t = Triangle(S1, (1.0, 1.0), (2.0, 1.0))
        self.assertTrue(t.has_supervertex((S1, S2, S3)))

    def test_has_supervertex_absent(self):
        S1, S2, S3 = (-100, -100), (0, 100), (100, -100)
        t = Triangle((0,0), (1,0), (0,1))
        self.assertFalse(t.has_supervertex((S1, S2, S3)))


# ═════════════════════════════════════════════════════════════
#  3. ALGORITHME DE BOWYER-WATSON
# ═════════════════════════════════════════════════════════════

class TestBowyerWatsonCasLimites(unittest.TestCase):

    def test_zero_point(self):
        self.assertEqual(bowyer_watson([]), [])

    def test_un_point(self):
        self.assertEqual(bowyer_watson([(0, 0)]), [])

    def test_deux_points(self):
        self.assertEqual(bowyer_watson([(0, 0), (1, 0)]), [])

    def test_trois_points_minimaux(self):
        tris = bowyer_watson([(0, 0), (1, 0), (0, 1)])
        self.assertEqual(len(tris), 1)

    def test_points_colineaires_ne_plante_pas(self):
        # 4 points colinéaires → pas de triangle valide
        pts = [(i, 0) for i in range(4)]
        tris = bowyer_watson(pts)
        # Peut retourner 0 ou quelques triangles dégénérés selon EPS,
        # l'essentiel est de ne pas lever d'exception
        self.assertIsInstance(tris, list)


class TestBowyerWatsonProprietes(unittest.TestCase):

    CONFIGS = [
        ("carré",       [(0,0),(1,0),(1,1),(0,1)],            2),
        ("pentagone",   [(math.cos(2*math.pi*i/5),
                          math.sin(2*math.pi*i/5)) for i in range(5)], 3),
        ("15 pts",      random_points(15, seed=1),            None),
        ("30 pts",      random_points(30, seed=2),            None),
        ("100 pts",     random_points(100, seed=3),           None),
    ]

    def _check_delaunay(self, points, triangles):
        """Propriété de Delaunay : aucun point dans le cercle circonscrit d'un triangle."""
        violations = 0
        for tri in triangles:
            for p in points:
                is_vertex = any(
                    pts_equal(v, p) for v in (tri.a, tri.b, tri.c)
                )
                if not is_vertex and tri.in_circumcircle(p):
                    violations += 1
        return violations

    def test_propriete_delaunay(self):
        for name, pts, _ in self.CONFIGS:
            with self.subTest(config=name):
                tris = bowyer_watson(pts)
                violations = self._check_delaunay(pts, tris)
                self.assertEqual(
                    violations, 0,
                    f"{name}: {violations} violations de la propriété de Delaunay"
                )

    def test_formule_euler(self):
        """Pour n points en position générale, T ≈ 2n − 2 − h (h = hull)."""
        for name, pts, expected in self.CONFIGS:
            with self.subTest(config=name):
                tris = bowyer_watson(pts)
                n = len(pts)
                # Borne large mais réaliste : T ∈ [n-2, 2n]
                self.assertGreaterEqual(len(tris), n - 2,
                    f"{name}: trop peu de triangles ({len(tris)} pour {n} pts)")
                self.assertLessEqual(len(tris), 2 * n,
                    f"{name}: trop de triangles ({len(tris)} pour {n} pts)")
                if expected is not None:
                    self.assertEqual(len(tris), expected,
                        f"{name}: {len(tris)} triangles, attendu {expected}")

    def test_pas_de_sommet_super_triangle(self):
        """Les sommets du super-triangle ne doivent jamais apparaître dans le résultat."""
        pts = random_points(50, seed=42)
        tris = bowyer_watson(pts)
        pt_set = set((round(p[0],4), round(p[1],4)) for p in pts)
        for tri in tris:
            for v in (tri.a, tri.b, tri.c):
                key = (round(v[0],4), round(v[1],4))
                self.assertIn(key, pt_set,
                    f"Sommet fantôme trouvé : {v} n'appartient pas aux points d'entrée")

    def test_tous_points_utilises(self):
        """Chaque point d'entrée doit apparaître dans au moins un triangle."""
        pts = random_points(20, seed=9)
        tris = bowyer_watson(pts)
        used = set()
        for tri in tris:
            for v in (tri.a, tri.b, tri.c):
                for i, p in enumerate(pts):
                    if pts_equal(v, p):
                        used.add(i)
        for i in range(len(pts)):
            self.assertIn(i, used, f"Point #{i} {pts[i]} absent de la triangulation")

    def test_reproductibilite(self):
        """Même entrée → même résultat (algorithme déterministe)."""
        pts = random_points(25, seed=77)
        t1 = bowyer_watson(pts[:])
        t2 = bowyer_watson(pts[:])
        self.assertEqual(len(t1), len(t2))


# ═════════════════════════════════════════════════════════════
#  4. CLIPPING SUTHERLAND-HODGMAN
# ═════════════════════════════════════════════════════════════

class TestSutherlandHodgman(unittest.TestCase):

    BBOX = (0.0, 10.0, 0.0, 10.0)   # xmin, xmax, ymin, ymax

    def _clip(self, poly):
        return sutherland_hodgman(poly, *self.BBOX)

    def test_polygone_entierement_interieur(self):
        poly = [(1,1),(9,1),(9,9),(1,9)]
        result = self._clip(poly)
        self.assertEqual(len(result), 4)
        for p in result:
            self.assertGreaterEqual(p[0], 0.0 - 1e-9)
            self.assertLessEqual(p[0],   10.0 + 1e-9)

    def test_polygone_entierement_exterieur(self):
        poly = [(20,20),(30,20),(30,30),(20,30)]
        result = self._clip(poly)
        self.assertEqual(result, [])

    def test_polygone_partiellement_exterieur(self):
        # Carré centré en (5,5) de demi-côté 8 → dépasse sur les 4 côtés
        poly = [(-3,5),(5,13),(13,5),(5,-3)]
        result = self._clip(poly)
        # Doit donner un octogone (4 coins coupés)
        self.assertGreater(len(result), 4)
        for p in result:
            self.assertGreaterEqual(p[0], -1e-9,  f"x < xmin : {p}")
            self.assertLessEqual(p[0],   10 + 1e-9, f"x > xmax : {p}")
            self.assertGreaterEqual(p[1], -1e-9,  f"y < ymin : {p}")
            self.assertLessEqual(p[1],   10 + 1e-9, f"y > ymax : {p}")

    def test_triangle_coupant_un_cote(self):
        # Triangle dont un seul sommet dépasse à droite
        poly = [(2,2),(12,5),(2,8)]
        result = self._clip(poly)
        self.assertGreaterEqual(len(result), 3)
        for p in result:
            self.assertLessEqual(p[0], 10.0 + 1e-9)

    def test_polygone_vide(self):
        self.assertEqual(self._clip([]), [])

    def test_rectangle_sur_la_frontiere(self):
        # Polygone exactement sur la bbox → doit être conservé intégralement
        poly = [(0,0),(10,0),(10,10),(0,10)]
        result = self._clip(poly)
        self.assertEqual(len(result), 4)

    def test_tous_les_points_clippés_dans_bbox(self):
        rng = random.Random(123)
        # Grand polygone aléatoire
        poly = [(rng.uniform(-20, 20), rng.uniform(-20, 20)) for _ in range(12)]
        result = self._clip(poly)
        for p in result:
            self.assertGreaterEqual(p[0], -1e-9)
            self.assertLessEqual(p[0],   10 + 1e-9)
            self.assertGreaterEqual(p[1], -1e-9)
            self.assertLessEqual(p[1],   10 + 1e-9)


# ═════════════════════════════════════════════════════════════
#  5. COMPUTE_VORONOI
# ═════════════════════════════════════════════════════════════

class TestComputeVoronoi(unittest.TestCase):

    def _run(self, pts, margin=30):
        tris = bowyer_watson(pts)
        bbox = make_bbox(pts, margin)
        cells = compute_voronoi(pts, tris, bbox)
        return tris, bbox, cells

    # ── 5.1 Couverture totale ──────────────────────────────

    def test_chaque_point_a_une_cellule(self):
        """Aucun point ne doit être sans cellule (bug original corrigé)."""
        for n, seed in [(6, 0), (15, 1), (30, 2), (55, 7), (100, 42)]:
            with self.subTest(n=n, seed=seed):
                pts = random_points(n, seed=seed)
                _, _, cells = self._run(pts)
                self.assertEqual(
                    len(cells), n,
                    f"n={n}: {n - len(cells)} point(s) sans cellule"
                )

    def test_points_enveloppe_convexe_ont_une_cellule(self):
        """Les points sur l'enveloppe convexe (cas non-borné) doivent aussi avoir une cellule."""
        # Carré : 4 points sur l'enveloppe + 1 intérieur
        pts = [(0,0),(10,0),(10,10),(0,10),(5,5)]
        _, _, cells = self._run(pts)
        self.assertEqual(len(cells), 5)

    def test_configuration_reguliere(self):
        """Grille régulière : chaque nœud doit avoir sa cellule."""
        pts = [(float(x), float(y)) for x in range(5) for y in range(5)]
        _, _, cells = self._run(pts)
        self.assertEqual(len(cells), 25)

    # ── 5.2 Géométrie des cellules ─────────────────────────

    def test_cellules_contiennent_leur_site(self):
        """Chaque site générateur doit se trouver dans sa propre cellule."""
        pts = random_points(20, seed=5)
        _, _, cells = self._run(pts)
        for i, poly in cells.items():
            px, py = pts[i]
            self.assertTrue(
                point_in_polygon(px, py, poly),
                f"Point #{i} {pts[i]} n'est pas dans sa cellule"
            )

    def test_cellules_dans_la_bbox(self):
        """Aucun sommet de cellule ne doit déborder de la bbox."""
        pts = random_points(30, seed=6)
        _, bbox, cells = self._run(pts)
        xmin, xmax, ymin, ymax = bbox
        tol = 1e-6
        for i, poly in cells.items():
            for x, y in poly:
                self.assertGreaterEqual(x, xmin - tol, f"cellule {i}: x={x} < xmin={xmin}")
                self.assertLessEqual(x, xmax + tol,    f"cellule {i}: x={x} > xmax={xmax}")
                self.assertGreaterEqual(y, ymin - tol, f"cellule {i}: y={y} < ymin={ymin}")
                self.assertLessEqual(y, ymax + tol,    f"cellule {i}: y={y} > ymax={ymax}")

    def test_cellules_ont_au_moins_3_sommets(self):
        """Une cellule valide doit être un polygone (≥ 3 sommets)."""
        pts = random_points(25, seed=8)
        _, _, cells = self._run(pts)
        for i, poly in cells.items():
            self.assertGreaterEqual(len(poly), 3, f"Cellule #{i} a seulement {len(poly)} sommet(s)")

    def test_pas_de_chevauchement_apparent(self):
        """
        Le site i ne doit PAS être dans la cellule j (i≠j) si les deux points
        sont suffisamment éloignés. Test heuristique sur petite config.
        """
        pts = random_points(12, seed=10)
        _, _, cells = self._run(pts)
        for i, poly_i in cells.items():
            for j, poly_j in cells.items():
                if i == j:
                    continue
                px, py = pts[i]
                # Le site i dans la cellule j serait une violation flagrante
                if point_in_polygon(px, py, poly_j):
                    # Vérifier que pts[i] et pts[j] ne sont pas quasi-confondus
                    dx = pts[i][0] - pts[j][0]
                    dy = pts[i][1] - pts[j][1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    self.assertLess(dist, 1.0,
                        f"Site #{i} {pts[i]} apparaît dans la cellule #{j} {pts[j]}"
                        f" (dist={dist:.3f})")

    def test_minimum_3_points(self):
        """compute_voronoi doit fonctionner avec exactement 3 points."""
        pts = [(0.0, 0.0), (10.0, 0.0), (5.0, 8.0)]
        _, _, cells = self._run(pts)
        self.assertEqual(len(cells), 3)


# ═════════════════════════════════════════════════════════════
#  6. PARSEURS DE FICHIERS
# ═════════════════════════════════════════════════════════════

class TestParseJson(unittest.TestCase):

    def test_format_liste_de_listes(self):
        data = json.dumps([[1.0, 2.0], [3.0, 4.5]])
        pts = parse_json(data)
        self.assertEqual(pts, [(1.0, 2.0), (3.0, 4.5)])

    def test_format_dict_points(self):
        data = json.dumps({"points": [[10, 20], [30, 40]]})
        pts = parse_json(data)
        self.assertEqual(pts, [(10.0, 20.0), (30.0, 40.0)])

    def test_format_liste_de_dicts(self):
        data = json.dumps([{"x": 1.5, "y": 2.5}, {"x": 3.0, "y": 4.0}])
        pts = parse_json(data)
        self.assertEqual(pts, [(1.5, 2.5), (3.0, 4.0)])

    def test_valeurs_entieres_converties_en_float(self):
        data = json.dumps([[0, 0], [1, 1]])
        pts = parse_json(data)
        for x, y in pts:
            self.assertIsInstance(x, float)
            self.assertIsInstance(y, float)

    def test_liste_vide(self):
        pts = parse_json("[]")
        self.assertEqual(pts, [])

    def test_format_invalide_leve_erreur(self):
        with self.assertRaises(Exception):
            parse_json('"juste une chaine"')

    def test_grands_nombres(self):
        data = json.dumps([[1e9, -1e9]])
        pts = parse_json(data)
        self.assertAlmostEqual(pts[0][0],  1e9)
        self.assertAlmostEqual(pts[0][1], -1e9)


class TestParseTxt(unittest.TestCase):

    def test_format_espace(self):
        pts = parse_txt("1.0 2.0\n3.0 4.0")
        self.assertEqual(pts, [(1.0, 2.0), (3.0, 4.0)])

    def test_format_virgule(self):
        pts = parse_txt("1.0,2.0\n3.0,4.0")
        self.assertEqual(pts, [(1.0, 2.0), (3.0, 4.0)])

    def test_format_parentheses(self):
        pts = parse_txt("(1.0, 2.0)\n(3.0, 4.0)")
        self.assertEqual(pts, [(1.0, 2.0), (3.0, 4.0)])

    def test_format_point_virgule(self):
        pts = parse_txt("1.0;2.0\n3.0;4.0")
        self.assertEqual(pts, [(1.0, 2.0), (3.0, 4.0)])

    def test_commentaires_ignores(self):
        content = "# commentaire\n1.0 2.0\n# autre\n3.0 4.0"
        pts = parse_txt(content)
        self.assertEqual(pts, [(1.0, 2.0), (3.0, 4.0)])

    def test_lignes_vides_ignorees(self):
        pts = parse_txt("\n1.0 2.0\n\n3.0 4.0\n")
        self.assertEqual(pts, [(1.0, 2.0), (3.0, 4.0)])

    def test_contenu_vide(self):
        self.assertEqual(parse_txt(""), [])

    def test_nombres_negatifs(self):
        pts = parse_txt("-1.5 -2.5\n0.0 0.0")
        self.assertEqual(pts, [(-1.5, -2.5), (0.0, 0.0)])

    def test_valeurs_scientifiques(self):
        pts = parse_txt("1e3 2.5e-1")
        self.assertAlmostEqual(pts[0][0], 1000.0)
        self.assertAlmostEqual(pts[0][1], 0.25)

    def test_espaces_multiples(self):
        pts = parse_txt("  1.0   2.0  ")
        self.assertEqual(pts, [(1.0, 2.0)])


# ═════════════════════════════════════════════════════════════
#  7. GENERATE_COLORS
# ═════════════════════════════════════════════════════════════

class TestGenerateColors(unittest.TestCase):

    PALETTES = ["pastel", "vivid", "earth", "random"]

    def test_nombre_de_couleurs(self):
        for n in [1, 5, 20, 100]:
            with self.subTest(n=n):
                colors = generate_colors(n)
                self.assertEqual(len(colors), n)

    def test_valeurs_rgb_dans_01(self):
        for palette in self.PALETTES:
            with self.subTest(palette=palette):
                for r, g, b in generate_colors(20, palette=palette):
                    self.assertGreaterEqual(r, 0.0)
                    self.assertLessEqual(r, 1.0)
                    self.assertGreaterEqual(g, 0.0)
                    self.assertLessEqual(g, 1.0)
                    self.assertGreaterEqual(b, 0.0)
                    self.assertLessEqual(b, 1.0)

    def test_determinisme_par_seed(self):
        c1 = generate_colors(10, palette="pastel", seed=42)
        c2 = generate_colors(10, palette="pastel", seed=42)
        self.assertEqual(c1, c2)

    def test_seeds_differentes_donnent_resultats_differents(self):
        c1 = generate_colors(10, palette="random", seed=0)
        c2 = generate_colors(10, palette="random", seed=1)
        self.assertNotEqual(c1, c2)

    def test_toutes_palettes_fonctionnent(self):
        for palette in self.PALETTES:
            with self.subTest(palette=palette):
                colors = generate_colors(5, palette=palette)
                self.assertEqual(len(colors), 5)

    def test_une_seule_couleur(self):
        colors = generate_colors(1)
        self.assertEqual(len(colors), 1)
        r, g, b = colors[0]
        self.assertIsInstance(r, float)


# ═════════════════════════════════════════════════════════════
#  8. TESTS D'INTÉGRATION (pipeline complet)
# ═════════════════════════════════════════════════════════════

class TestIntegration(unittest.TestCase):

    def test_pipeline_complet_petit(self):
        """JSON → parse → Bowyer-Watson → Voronoï : toutes les cellules présentes."""
        raw = json.dumps([[50,200],[150,80],[300,350],[420,120],[500,300],
                          [200,450],[350,500],[80,380],[450,420],[250,250]])
        pts = parse_json(raw)
        tris = bowyer_watson(pts)
        bbox = make_bbox(pts)
        cells = compute_voronoi(pts, tris, bbox)
        self.assertEqual(len(cells), len(pts))

    def test_pipeline_complet_txt(self):
        content = "\n".join(f"{x},{y}" for x,y in random_points(20, seed=99))
        pts = parse_txt(content)
        tris = bowyer_watson(pts)
        bbox = make_bbox(pts)
        cells = compute_voronoi(pts, tris, bbox)
        self.assertEqual(len(cells), len(pts))

    def test_pipeline_200_points(self):
        pts = random_points(200, seed=123)
        tris = bowyer_watson(pts)
        bbox = make_bbox(pts)
        cells = compute_voronoi(pts, tris, bbox)
        # Tolérance : ≥ 98 % des points doivent avoir une cellule
        ratio = len(cells) / len(pts)
        self.assertGreaterEqual(ratio, 0.98,
            f"Couverture insuffisante : {len(cells)}/{len(pts)} = {ratio:.1%}")

    def test_stabilite_points_aleatoires_differentes_graines(self):
        """Vérifier la robustesse sur plusieurs configurations aléatoires."""
        for seed in range(10):
            with self.subTest(seed=seed):
                pts = random_points(25, seed=seed)
                tris = bowyer_watson(pts)
                bbox = make_bbox(pts)
                cells = compute_voronoi(pts, tris, bbox)
                self.assertEqual(len(cells), len(pts),
                    f"seed={seed}: {len(pts)-len(cells)} point(s) sans cellule")

    def test_points_clusteres(self):
        """Points très proches les uns des autres (clusters)."""
        rng = random.Random(55)
        pts = []
        for _ in range(5):
            cx, cy = rng.uniform(100, 400), rng.uniform(100, 400)
            for _ in range(5):
                pts.append((cx + rng.uniform(-5, 5), cy + rng.uniform(-5, 5)))
        tris = bowyer_watson(pts)
        bbox = make_bbox(pts)
        cells = compute_voronoi(pts, tris, bbox)
        self.assertGreater(len(cells), 0)

    def test_points_en_grille_reguliere(self):
        """Grille uniforme : propriété de Delaunay + couverture complète."""
        pts = [(float(i*10), float(j*10)) for i in range(6) for j in range(6)]
        tris = bowyer_watson(pts)
        # Vérification Delaunay
        for tri in tris:
            for p in pts:
                is_v = any(pts_equal(v, p) for v in (tri.a, tri.b, tri.c))
                if not is_v:
                    self.assertFalse(tri.in_circumcircle(p),
                        f"Violation Delaunay en grille régulière")
        bbox = make_bbox(pts)
        cells = compute_voronoi(pts, tris, bbox)
        self.assertEqual(len(cells), len(pts))


# ─────────────────────────────────────────────────────────────
#  Point d'entrée
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)

    total  = result.testsRun
    fails  = len(result.failures)
    errors = len(result.errors)
    passed = total - fails - errors

    print("\n" + "═" * 60)
    print(f"  Résultats : {passed}/{total} tests réussis", end="")
    if fails or errors:
        print(f"  ❌  ({fails} échec(s), {errors} erreur(s))")
    else:
        print("  ✅")
    print("═" * 60)

    sys.exit(0 if result.wasSuccessful() else 1)