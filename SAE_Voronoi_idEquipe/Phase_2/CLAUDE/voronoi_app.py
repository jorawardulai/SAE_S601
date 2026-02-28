"""
Diagramme de Voronoï - Streamlit App
Implémentation manuelle de la Triangulation de Delaunay (Bowyer-Watson)
Sans scipy.spatial.Voronoi ni scipy.spatial.Delaunay
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import matplotlib.colors as mcolors
import json
import math
import random
import io
import colorsys

# ─────────────────────────────────────────────────────────────
#  STRUCTURES GÉOMÉTRIQUES DE BASE
# ─────────────────────────────────────────────────────────────

EPS = 1e-9


def pts_equal(a, b):
    return abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) < EPS


def edge_equal(e1, e2):
    """Vérifie si deux arêtes (non-orientées) sont identiques."""
    return (pts_equal(e1[0], e2[0]) and pts_equal(e1[1], e2[1])) or \
           (pts_equal(e1[0], e2[1]) and pts_equal(e1[1], e2[0]))


class Triangle:
    """Triangle avec calcul de cercle circonscrit."""

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
        self._cc = None        # centre du cercle circonscrit
        self._cr2 = None       # rayon² du cercle circonscrit

    def _compute_circumcircle(self):
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

    @property
    def circumcenter(self):
        if self._cc is None:
            self._compute_circumcircle()
        return self._cc

    @property
    def circumradius2(self):
        if self._cr2 is None:
            self._compute_circumcircle()
        return self._cr2

    def in_circumcircle(self, p):
        """Retourne True si p est strictement à l'intérieur du cercle circonscrit."""
        if self._cr2 is None:
            self._compute_circumcircle()
        if self._cr2 == math.inf:
            return False
        cx, cy = self._cc
        dx, dy = p[0] - cx, p[1] - cy
        return dx * dx + dy * dy < self._cr2 - EPS

    def edges(self):
        return [(self.a, self.b), (self.b, self.c), (self.c, self.a)]

    def has_supervertex(self, sv):
        """sv est un ensemble de 3 sommets du super-triangle."""
        for s in sv:
            if pts_equal(self.a, s) or pts_equal(self.b, s) or pts_equal(self.c, s):
                return True
        return False


# ─────────────────────────────────────────────────────────────
#  ALGORITHME DE BOWYER-WATSON
# ─────────────────────────────────────────────────────────────

def bowyer_watson(points):
    """
    Triangulation de Delaunay par l'algorithme incrémental de Bowyer-Watson.
    Retourne une liste de Triangle.
    """
    if len(points) < 3:
        return []

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    mn_x, mx_x = min(xs), max(xs)
    mn_y, mx_y = min(ys), max(ys)
    dx = mx_x - mn_x or 1.0
    dy = mx_y - mn_y or 1.0
    delta = max(dx, dy) * 20.0

    mid_x = (mn_x + mx_x) / 2.0
    mid_y = (mn_y + mx_y) / 2.0

    # Super-triangle englobant tous les points
    S1 = (mid_x - 2.0 * delta, mid_y - delta)
    S2 = (mid_x,               mid_y + 2.0 * delta)
    S3 = (mid_x + 2.0 * delta, mid_y - delta)
    super_verts = (S1, S2, S3)

    triangulation = [Triangle(S1, S2, S3)]

    for point in points:
        # 1) Trouver les "mauvais" triangles dont le cercle circonscrit
        #    contient le nouveau point
        bad = [t for t in triangulation if t.in_circumcircle(point)]

        # 2) Construire le polygone frontalier (arêtes non-partagées)
        boundary = []
        for tri in bad:
            for edge in tri.edges():
                shared = False
                for other in bad:
                    if other is tri:
                        continue
                    for oe in other.edges():
                        if edge_equal(edge, oe):
                            shared = True
                            break
                    if shared:
                        break
                if not shared:
                    boundary.append(edge)

        # 3) Supprimer les mauvais triangles
        for tri in bad:
            triangulation.remove(tri)

        # 4) Retrianguler le trou
        for edge in boundary:
            triangulation.append(Triangle(edge[0], edge[1], point))

    # 5) Retirer les triangles contenant un sommet du super-triangle
    triangulation = [t for t in triangulation if not t.has_supervertex(super_verts)]

    return triangulation


# ─────────────────────────────────────────────────────────────
#  CONSTRUCTION DU DIAGRAMME DE VORONOÏ
# ─────────────────────────────────────────────────────────────

def compute_voronoi(points, triangles, bbox):
    """
    Calcule les cellules de Voronoï à partir de la triangulation de Delaunay.

    Pour les points intérieurs  → polygone formé des circumcentres des triangles adjacents.
    Pour les points sur l'enveloppe convexe → cellule non-bornée :
        on ajoute des "points lointains" le long des rayons de Voronoï infinis,
        puis on clippe sur la bbox (Sutherland-Hodgman).

    bbox = (xmin, xmax, ymin, ymax)
    Retourne: dict {idx_point: [liste de sommets (x,y)]}
    """
    xmin, xmax, ymin, ymax = bbox
    # Distance "infinie" = diagonale de la bbox × 10 (largement hors zone visible)
    FAR = math.sqrt((xmax - xmin) ** 2 + (ymax - ymin) ** 2) * 10.0

    # ── 1. Adjacence point → triangles ──────────────────────────
    adj = {i: [] for i in range(len(points))}
    for tri in triangles:
        for i, p in enumerate(points):
            for v in (tri.a, tri.b, tri.c):
                if pts_equal(v, p):
                    adj[i].append(tri)
                    break

    # ── 2. Arêtes de bord (hull) : appartiennent à UN seul triangle ──
    # On collecte toutes les arêtes avec leur triangle propriétaire.
    all_edges_with_tri = []
    for tri in triangles:
        for e in tri.edges():
            all_edges_with_tri.append((e, tri))

    # Une arête de bord n'a pas de "jumelle" dans un autre triangle.
    hull_edges = []      # liste de (edge, triangle)
    for idx_e, (e1, t1) in enumerate(all_edges_with_tri):
        is_hull = True
        for idx_f, (e2, t2) in enumerate(all_edges_with_tri):
            if idx_e != idx_f and edge_equal(e1, e2):
                is_hull = False
                break
        if is_hull:
            hull_edges.append((e1, t1))

    # Centroïde global pour orienter les normales sortantes
    cx_all = sum(p[0] for p in points) / len(points)
    cy_all = sum(p[1] for p in points) / len(points)

    def outward_normal(e):
        """Normale unitaire à l'arête e, orientée vers l'extérieur du nuage."""
        ex = e[1][0] - e[0][0]
        ey = e[1][1] - e[0][1]
        n1 = (-ey, ex)
        n2 = ( ey, -ex)
        mid_x = (e[0][0] + e[1][0]) / 2.0
        mid_y = (e[0][1] + e[1][1]) / 2.0
        # Choisir la normale qui s'éloigne du centroïde
        d1 = (mid_x + n1[0] - cx_all) ** 2 + (mid_y + n1[1] - cy_all) ** 2
        d2 = (mid_x + n2[0] - cx_all) ** 2 + (mid_y + n2[1] - cy_all) ** 2
        nx, ny = (n1 if d1 > d2 else n2)
        length = math.sqrt(nx * nx + ny * ny)
        if length < EPS:
            return (0.0, 0.0)
        return (nx / length, ny / length)

    # ── 3. Construction des cellules ─────────────────────────────
    cells = {}
    for i, pt in enumerate(points):
        tris = adj[i]
        if not tris:
            continue

        px, py = pt

        # Circumcentres des triangles adjacents (sommets Voronoï finis)
        cc_list = []
        for tri in tris:
            cc = tri.circumcenter
            if not (math.isinf(cc[0]) or math.isinf(cc[1])):
                cc_list.append(cc)

        if not cc_list:
            continue

        # Rayons infinis pour les arêtes de bord adjacentes à ce point
        far_pts = []
        for (e, tri) in hull_edges:
            # L'arête doit appartenir à ce point (un de ses deux sommets = pt)
            if not (pts_equal(e[0], pt) or pts_equal(e[1], pt)):
                continue
            cc = tri.circumcenter
            if math.isinf(cc[0]) or math.isinf(cc[1]):
                continue
            nx, ny = outward_normal(e)
            far_pts.append((cc[0] + nx * FAR, cc[1] + ny * FAR))

        # Combiner sommets finis + points lointains, trier par angle autour du site
        all_verts = cc_list + far_pts
        all_verts.sort(key=lambda c: math.atan2(c[1] - py, c[0] - px))

        # Clipper sur la bounding-box → cellule bornée
        clipped = sutherland_hodgman(all_verts, xmin, xmax, ymin, ymax)
        if len(clipped) >= 3:
            cells[i] = clipped

    return cells


# ─────────────────────────────────────────────────────────────
#  CLIPPING DE POLYGONE (Sutherland-Hodgman)
# ─────────────────────────────────────────────────────────────

def _clip_half_plane(polygon, inside_fn, intersect_fn):
    """Étape générique du clipping de Sutherland-Hodgman."""
    if not polygon:
        return []
    output = []
    n = len(polygon)
    for idx in range(n):
        cur = polygon[idx]
        prev = polygon[(idx - 1) % n]
        if inside_fn(cur):
            if not inside_fn(prev):
                output.append(intersect_fn(prev, cur))
            output.append(cur)
        elif inside_fn(prev):
            output.append(intersect_fn(prev, cur))
    return output


def _line_intersect_x(p1, p2, x):
    """Intersection du segment [p1,p2] avec la droite verticale x=x."""
    dx = p2[0] - p1[0]
    if abs(dx) < EPS:
        return (x, p1[1])
    t = (x - p1[0]) / dx
    return (x, p1[1] + t * (p2[1] - p1[1]))


def _line_intersect_y(p1, p2, y):
    """Intersection du segment [p1,p2] avec la droite horizontale y=y."""
    dy = p2[1] - p1[1]
    if abs(dy) < EPS:
        return (p1[0], y)
    t = (y - p1[1]) / dy
    return (p1[0] + t * (p2[0] - p1[0]), y)


def sutherland_hodgman(polygon, xmin, xmax, ymin, ymax):
    """Clipping d'un polygone (convexe ou non) sur un rectangle."""
    poly = polygon[:]
    # Gauche
    poly = _clip_half_plane(poly,
                            lambda p: p[0] >= xmin,
                            lambda a, b: _line_intersect_x(a, b, xmin))
    # Droite
    poly = _clip_half_plane(poly,
                            lambda p: p[0] <= xmax,
                            lambda a, b: _line_intersect_x(a, b, xmax))
    # Bas
    poly = _clip_half_plane(poly,
                            lambda p: p[1] >= ymin,
                            lambda a, b: _line_intersect_y(a, b, ymin))
    # Haut
    poly = _clip_half_plane(poly,
                            lambda p: p[1] <= ymax,
                            lambda a, b: _line_intersect_y(a, b, ymax))
    return poly


# ─────────────────────────────────────────────────────────────
#  PARSING DES FICHIERS SOURCE
# ─────────────────────────────────────────────────────────────

def parse_json(content: str):
    """
    Formats acceptés :
    - [[x1,y1],[x2,y2], ...]
    - {"points": [[x1,y1], ...]}
    - [{"x":..,"y":..}, ...]
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
    raise ValueError("Format JSON non reconnu.")


def parse_txt(content: str):
    """
    Formats acceptés (une paire (x,y) par ligne) :
    - "x y"
    - "x,y"
    - "(x, y)"
    - "x;y"
    """
    points = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.strip("()")
        sep = "," if "," in line else (";" if ";" in line else None)
        if sep:
            parts = line.split(sep)
        else:
            parts = line.split()
        if len(parts) >= 2:
            points.append((float(parts[0].strip()), float(parts[1].strip())))
    return points


def load_points(uploaded_file) -> list:
    content = uploaded_file.read().decode("utf-8")
    name = uploaded_file.name.lower()
    if name.endswith(".json"):
        return parse_json(content)
    elif name.endswith(".txt"):
        return parse_txt(content)
    else:
        # Essai auto
        try:
            return parse_json(content)
        except Exception:
            return parse_txt(content)


# ─────────────────────────────────────────────────────────────
#  GÉNÉRATION DE COULEURS DISTINCTES
# ─────────────────────────────────────────────────────────────

def generate_colors(n, palette="pastel", seed=42):
    rng = random.Random(seed)
    if palette == "pastel":
        colors = []
        for i in range(n):
            h = i / n
            r, g, b = colorsys.hls_to_rgb(h, 0.78, 0.65)
            colors.append((r, g, b))
        rng.shuffle(colors)
        return colors
    elif palette == "vivid":
        colors = []
        for i in range(n):
            h = i / n
            r, g, b = colorsys.hls_to_rgb(h, 0.55, 0.85)
            colors.append((r, g, b))
        rng.shuffle(colors)
        return colors
    elif palette == "earth":
        base = [
            "#8B6F47","#A0785A","#C4956A","#D4A96A","#B5835A",
            "#7A6B50","#9B8C6B","#C8A97A","#B09060","#8A7055",
        ]
        return [mcolors.to_rgb(base[i % len(base)]) for i in range(n)]
    else:  # random
        return [(rng.random(), rng.random(), rng.random()) for _ in range(n)]


# ─────────────────────────────────────────────────────────────
#  VISUALISATION
# ─────────────────────────────────────────────────────────────

def draw_voronoi(points, triangles, cells, colors,
                 show_delaunay=False, show_sites=True, show_edges=True,
                 bg_color="#1a1a2e", edge_color="#ffffff", site_color="#ff4444",
                 fig_size=8, dpi=120):

    fig, ax = plt.subplots(figsize=(fig_size, fig_size), dpi=dpi)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.set_aspect("equal")
    ax.axis("off")

    # Dessin des cellules remplies
    for i, poly_pts in cells.items():
        if len(poly_pts) < 3:
            continue
        color = colors[i % len(colors)]
        patch = MplPolygon(poly_pts, closed=True,
                           facecolor=(*color, 0.75),
                           edgecolor=edge_color if show_edges else "none",
                           linewidth=0.8 if show_edges else 0)
        ax.add_patch(patch)

    # Triangulation de Delaunay (optionnel)
    if show_delaunay:
        for tri in triangles:
            xs = [tri.a[0], tri.b[0], tri.c[0], tri.a[0]]
            ys = [tri.a[1], tri.b[1], tri.c[1], tri.a[1]]
            ax.plot(xs, ys, color="#ffffff", linewidth=0.4, alpha=0.4, zorder=3)

    # Sites générateurs
    if show_sites:
        sx = [p[0] for p in points]
        sy = [p[1] for p in points]
        ax.scatter(sx, sy, color=site_color, s=18, zorder=5, linewidths=0.5,
                   edgecolors="white")

    # Centroïdes des cellules (pour indexer)
    for i, poly_pts in cells.items():
        xs_c = [p[0] for p in poly_pts]
        ys_c = [p[1] for p in poly_pts]
        cx = sum(xs_c) / len(xs_c)
        cy = sum(ys_c) / len(ys_c)

    ax.autoscale_view()
    plt.tight_layout(pad=0)
    return fig


# ─────────────────────────────────────────────────────────────
#  INTERFACE STREAMLIT
# ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Diagramme de Voronoï",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # CSS personnalisé
    st.markdown("""
    <style>
    .main { background: #0f0f1a; }
    h1 { font-size:2.2rem !important; }
    .stButton>button {
        background: linear-gradient(135deg,#6c63ff,#3ecfcf);
        color:white; border:none; border-radius:8px;
        padding:0.5rem 2rem; font-weight:700; font-size:1rem;
    }
    .stButton>button:hover { opacity:0.85; }
    .block-container { padding-top:1rem; }
    </style>
    """, unsafe_allow_html=True)

    # ── Titre ──────────────────────────────────────────────
    st.markdown("## 🔷 Diagramme de Voronoï")
    st.markdown(
        "Triangulation de Delaunay **(Bowyer-Watson)** implémentée manuellement — "
        "sans `scipy.spatial`."
    )
    st.divider()

    # ── Sidebar ────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Paramètres")

        st.subheader("📂 Source de données")
        uploaded = st.file_uploader(
            "Fichier JSON ou TXT",
            type=["json", "txt"],
            help="Voir les formats acceptés ci-dessous."
        )

        st.subheader("🎨 Palette de couleurs")
        palette = st.selectbox(
            "Palette",
            ["pastel", "vivid", "earth", "random"],
            index=0,
        )
        color_seed = st.slider("Graine couleur", 0, 100, 42)

        st.subheader("🖼️ Rendu")
        bg_color   = st.color_picker("Fond",             "#1a1a2e")
        edge_color = st.color_picker("Arêtes Voronoï",   "#ffffff")
        site_color = st.color_picker("Sites générateurs","#ff4444")
        fig_size   = st.slider("Taille figure", 5, 14, 9)

        st.subheader("👁️ Affichage")
        show_sites    = st.checkbox("Sites générateurs",         True)
        show_edges    = st.checkbox("Arêtes Voronoï",            True)
        show_delaunay = st.checkbox("Triangulation Delaunay",    False)

        st.subheader("🎲 Points aléatoires")
        n_random   = st.slider("Nombre de points", 5, 300, 40)
        area_size  = st.slider("Taille zone",      100, 1000, 500)
        rnd_seed   = st.slider("Graine aléatoire", 0, 200, 7)

        generate_random = st.button("Générer points aléatoires")
        st.divider()
        st.caption(
            "**Formats JSON :**\n"
            "```\n[[x,y], ...]\n{\"points\":[[x,y],...]}\n[{\"x\":...,\"y\":...},...]\n```\n"
            "**Formats TXT :**\n"
            "```\nx y\nx,y\n(x, y)\nx;y\n```"
        )

    # ── Chargement / génération des points ─────────────────
    points = None

    if generate_random or ("points_cache" in st.session_state and not uploaded):
        rng = random.Random(rnd_seed)
        points = [(rng.uniform(0, area_size), rng.uniform(0, area_size))
                  for _ in range(n_random)]
        st.session_state["points_cache"] = points
        st.success(f"✅ {n_random} points générés aléatoirement.")
    elif uploaded is not None:
        try:
            points = load_points(uploaded)
            if len(points) < 3:
                st.error("❌ Au moins 3 points sont nécessaires.")
                return
            st.success(f"✅ {len(points)} points chargés depuis **{uploaded.name}**.")
        except Exception as e:
            st.error(f"❌ Erreur de lecture : {e}")
            return
    elif "points_cache" in st.session_state:
        points = st.session_state["points_cache"]

    if points is None:
        # Écran d'accueil
        col1, col2 = st.columns([1, 1])
        with col1:
            st.info("👈 Chargez un fichier ou générez des points aléatoires dans la barre latérale.")
            st.markdown("""
**Comment utiliser :**
1. Téléchargez un fichier `.json` ou `.txt` contenant vos points 2D
2. Ou cliquez sur **Générer points aléatoires**
3. Ajustez les paramètres visuels dans la barre latérale
4. Le diagramme se génère automatiquement !

**Algorithme :**
- Triangulation de Delaunay via **Bowyer-Watson** (O(n²))
- Centres circonscrits → sommets de Voronoï
- Clipping **Sutherland-Hodgman** sur la bounding-box
""")
        with col2:
            st.markdown("#### Exemple de fichier JSON")
            st.code(
                json.dumps([[50,200],[150,80],[300,350],[420,120],[500,300],
                            [200,450],[350,500],[80,380],[450,420],[250,250]], indent=2),
                language="json"
            )
        return

    # ── Dédoublonnage & vérification ───────────────────────
    seen, unique_pts = set(), []
    for p in points:
        key = (round(p[0], 6), round(p[1], 6))
        if key not in seen:
            seen.add(key)
            unique_pts.append(p)
    if len(unique_pts) < len(points):
        st.warning(f"⚠️ {len(points)-len(unique_pts)} doublon(s) supprimé(s).")
    points = unique_pts

    if len(points) < 3:
        st.error("❌ Au moins 3 points distincts sont nécessaires.")
        return

    # ── Calcul ─────────────────────────────────────────────
    with st.spinner("🔧 Triangulation de Delaunay (Bowyer-Watson)…"):
        try:
            triangles = bowyer_watson(points)
        except Exception as e:
            st.error(f"❌ Erreur triangulation : {e}")
            return

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    margin = max((max(xs)-min(xs)), (max(ys)-min(ys))) * 0.08 + 1.0
    bbox = (min(xs)-margin, max(xs)+margin, min(ys)-margin, max(ys)+margin)

    with st.spinner("🎨 Construction du diagramme de Voronoï…"):
        try:
            cells = compute_voronoi(points, triangles, bbox)
        except Exception as e:
            st.error(f"❌ Erreur Voronoï : {e}")
            return

    # ── Affichage stats ────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Points",           len(points))
    c2.metric("Triangles Delaunay", len(triangles))
    c3.metric("Cellules Voronoï",  len(cells))
    c4.metric("Couverture",        f"{100*len(cells)//max(len(points),1)} %")

    # ── Dessin ─────────────────────────────────────────────
    colors = generate_colors(len(points), palette=palette, seed=color_seed)

    with st.spinner("🖌️ Rendu…"):
        fig = draw_voronoi(
            points, triangles, cells, colors,
            show_delaunay=show_delaunay,
            show_sites=show_sites,
            show_edges=show_edges,
            bg_color=bg_color,
            edge_color=edge_color,
            site_color=site_color,
            fig_size=fig_size,
        )

    st.pyplot(fig, use_container_width=True)

    # ── Téléchargement ─────────────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=bg_color)
    buf.seek(0)
    st.download_button(
        "⬇️ Télécharger le diagramme (PNG)",
        data=buf,
        file_name="voronoi_diagram.png",
        mime="image/png",
    )

    # ── Données brutes (optionnel) ─────────────────────────
    with st.expander("📊 Données brutes (points & triangles)"):
        tab1, tab2 = st.tabs(["Points", "Triangles Delaunay"])
        with tab1:
            st.dataframe(
                [{"#": i, "x": round(p[0], 4), "y": round(p[1], 4)}
                 for i, p in enumerate(points)],
                use_container_width=True,
                height=300,
            )
        with tab2:
            rows = []
            for k, t in enumerate(triangles[:200]):
                rows.append({
                    "#": k,
                    "A": f"({t.a[0]:.2f}, {t.a[1]:.2f})",
                    "B": f"({t.b[0]:.2f}, {t.b[1]:.2f})",
                    "C": f"({t.c[0]:.2f}, {t.c[1]:.2f})",
                    "CC": f"({t.circumcenter[0]:.2f}, {t.circumcenter[1]:.2f})",
                })
            st.dataframe(rows, use_container_width=True, height=300)
            if len(triangles) > 200:
                st.caption(f"(Affichage limité aux 200 premiers triangles sur {len(triangles)})")


if __name__ == "__main__":
    main()
