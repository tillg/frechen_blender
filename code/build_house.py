"""Frechenlehen – Blender model generated from the ALLPLAN PDFs (Grundriss EG/OG, Ansichten, 1:100).

Coordinates in metres: origin = outer SW corner of the main house, +X = east, +Y = north, Z = up.
EG wall segments come from the vector data of "Grundriss Frechenlehen EG.pdf" (gray wall fills);
OG walls and all heights were measured from the plans/elevations (approx. +-5 cm).

Run inside Blender (e.g. via the Blender MCP server):  exec(open(".../code/build_house.py").read())
Re-running replaces the "Haus" collection.
"""
import bpy, math, os
from mathutils import Vector

PROJECT = "/Users/tgartner/git/frechen_blender"

W_OUT, D_OUT = 14.885, 12.887           # outer footprint of main house
RIDGE_Y, RIDGE_Z = D_OUT / 2, 7.67      # ridge runs east-west (elevations: 7.65-7.69)
SLOPE, ROOF_T = 0.3635, 0.10            # ~20 deg pitch; thin eave edge as drawn
EAVE_OH, GABLE_OH = 1.34, 1.49          # overhang at eaves (N/S) and gables (E/W), measured
Z_EG_TOP, Z_OG, Z_OG_TOP, Z_ATTIC = 2.40, 2.70, 4.90, 5.10
DOOR_H = 2.0                            # interior door height


def roof_top(y):
    return RIDGE_Z - SLOPE * abs(y - RIDGE_Y)


def roof_under(y):
    return roof_top(y) - ROOF_T


# ---------------------------------------------------------------- materials
MAT_DEF = {
    "Putz":      (0.93, 0.92, 0.88, 1),
    "Decke":     (0.80, 0.80, 0.78, 1),
    "Boden":     (0.62, 0.46, 0.30, 1),
    "Dach":      (0.17, 0.17, 0.19, 1),
    "Holz":      (0.36, 0.21, 0.10, 1),
    "Rahmen":    (0.45, 0.28, 0.14, 1),
    "Laden":     (0.30, 0.17, 0.08, 1),
    "Tuer":      (0.28, 0.16, 0.08, 1),
    "Glas":      (0.70, 0.85, 0.95, 0.25),
    "Stein":     (0.62, 0.61, 0.58, 1),
    "Wiese":     (0.24, 0.42, 0.18, 1),
    "Kachel":    (0.35, 0.47, 0.42, 1),
    "Kies":      (0.55, 0.52, 0.47, 1),
}
MAT = {}


def make_materials():
    for name, rgba in MAT_DEF.items():
        m = bpy.data.materials.get("FL_" + name) or bpy.data.materials.new("FL_" + name)
        m.use_nodes = True
        m.diffuse_color = rgba
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.1 if name == "Glas" else 0.8
        if name == "Glas":
            bsdf.inputs["Alpha"].default_value = 0.25
            m.surface_render_method = "BLENDED"
        MAT[name] = m


# ---------------------------------------------------------------- geometry accumulator
GEO = {}   # (collection, object) -> {"v": [...], "f": [...], "m": [...]}


def add(coll, obj, mat, verts, faces):
    g = GEO.setdefault((coll, obj), {"v": [], "f": [], "m": []})
    off = len(g["v"])
    g["v"] += verts
    for f in faces:
        g["f"].append([i + off for i in f])
        g["m"].append(mat)


def box(coll, obj, mat, x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    if min(x1 - x0, y1 - y0, z1 - z0) < 1e-4:
        return
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    add(coll, obj, mat, v, f)


def prism_x(coll, obj, mat, x0, x1, prof):
    """Extrude a (y, z) profile polygon from x0 to x1."""
    n = len(prof)
    v = [(x0, y, z) for y, z in prof] + [(x1, y, z) for y, z in prof]
    f = [list(range(n))[::-1], list(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    add(coll, obj, mat, v, f)


def roof_profile(ya, yb, fb, ft):
    ys = [ya] + ([RIDGE_Y] if ya < RIDGE_Y < yb else []) + [yb]
    return [(y, fb(y)) for y in ys] + [(y, ft(y)) for y in reversed(ys)]


# ---------------------------------------------------------------- walls with openings
def wall(coll, x0, x1, y0, y1, z0, z1, ops=(), out=0, mat="Putz"):
    """Straight wall (axis-aligned box) with openings.

    ops: (a, b, sill, head, kind[, shutters]) along the wall's long axis.
    kind: W window, FD french door, SL sliding door, D solid door, I interior opening (no fill).
    out: +1 / -1 = side of the thin axis that faces outside (for shutters).
    """
    obj, fo = coll + "_Waende", coll + "_Fenster_Tueren"
    ax = "x" if (x1 - x0) >= (y1 - y0) else "y"
    u0, u1, t0, t1 = (x0, x1, y0, y1) if ax == "x" else (y0, y1, x0, x1)

    def B(m, ua, ub, ta, tb, za, zb, o=obj):
        if ax == "x":
            box(coll, o, m, ua, ub, ta, tb, za, zb)
        else:
            box(coll, o, m, ta, tb, ua, ub, za, zb)

    cur = u0
    for op in sorted(ops):
        a, b, sill, head, kind = op[:5]
        sh = len(op) > 5 and op[5]
        B(mat, cur, a, t0, t1, z0, z1)
        B(mat, a, b, t0, t1, z0, sill)
        B(mat, a, b, t0, t1, head, z1)
        cur = b
        if kind == "I":
            continue
        tm, fd, fw = (t0 + t1) / 2, 0.04, 0.06
        B("Rahmen", a, a + fw, tm - fd, tm + fd, sill, head, fo)
        B("Rahmen", b - fw, b, tm - fd, tm + fd, sill, head, fo)
        B("Rahmen", a, b, tm - fd, tm + fd, head - fw, head, fo)
        if kind == "D":
            B("Tuer", a + fw, b - fw, tm - 0.025, tm + 0.025, sill, head - fw, fo)
        else:
            B("Rahmen", a, b, tm - fd, tm + fd, sill, sill + fw, fo)
            n = 3 if kind == "SL" else (2 if b - a > 0.75 else 1)
            for k in range(1, n):
                c = a + (b - a) * k / n
                B("Rahmen", c - fw / 2, c + fw / 2, tm - fd, tm + fd, sill, head, fo)
            B("Glas", a + fw, b - fw, tm - 0.005, tm + 0.005, sill + fw, head - fw, fo)
        if sh and out:
            w = (b - a) / 2
            ta, tb = (t1, t1 + 0.03) if out > 0 else (t0 - 0.03, t0)
            B("Laden", a - w, a - 0.02, ta, tb, sill, head, coll + "_Laeden")
            B("Laden", b + 0.02, b + w, ta, tb, sill, head, coll + "_Laeden")
    B(mat, cur, u1, t0, t1, z0, z1)


def interior(coll, x0, x1, y0, y1, doors=(), z0=0.0, z1=Z_EG_TOP, head=DOOR_H):
    wall(coll, x0, x1, y0, y1, z0, z1, [(a, b, z0, z0 + head, "I") for a, b in doors])


# ---------------------------------------------------------------- EG
def build_eg():
    c, z0, z1 = "EG", 0.0, Z_EG_TOP
    # exterior walls (segments = PDF vector wall fills, gaps = openings)
    wall(c, 0, W_OUT, 12.473, D_OUT, z0, z1, [
        (1.109, 2.008, 0, 2.0, "FD", 1), (3.866, 4.765, 0, 2.0, "FD", 1),
        (6.953, 7.852, 1.0, 2.0, "W", 1), (10.020, 10.919, 0, 2.0, "FD", 1),
        (12.867, 13.766, 0, 2.0, "FD", 1)], out=+1)
    wall(c, 2.358, W_OUT, 0, 0.415, z0, z1, [
        (3.831, 4.730, 1.03, 2.0, "W", 1), (6.618, 7.917, 1.03, 2.0, "W", 1),
        (9.785, 13.741, 0, 2.2, "SL")], out=-1)
    wall(c, 14.575, W_OUT, 6.349, 12.473, z0, z1, [
        (6.458, 7.507, 0, 2.2, "D"), (8.007, 8.476, 1.2, 2.1, "W"),
        (10.315, 11.214, 1.0, 2.0, "W", 1)], out=+1)
    wall(c, 14.351, W_OUT, 0.415, 6.349, z0, z1, [(1.254, 4.880, 0, 2.2, "SL")], out=+1)
    wall(c, 0, 0.31, 5.145, 12.473, z0, z1, [
        (5.724, 6.324, 1.57, 2.17, "W"), (7.408, 8.377, 0, 2.3, "D"),
        (9.460, 10.060, 1.57, 2.17, "W")], out=-1)
    wall(c, 0.31, 2.358, 5.145, 5.475, z0, z1)              # WC south (towards Schuppen)
    wall(c, 2.358, 2.772, 0.415, 5.849, z0, z1)             # west wall Speis/Essen
    # interior walls
    interior(c, 6.024, 6.174, 8.876, 12.473)
    interior(c, 2.657, 14.575, 8.576, 8.876,
             [(4.406, 5.335), (7.333, 8.282), (9.780, 10.719), (13.517, 14.575)])
    interior(c, 0.31, 2.358, 8.506, 8.656, [(0.824, 1.853)])
    interior(c, 0.31, 2.358, 6.574, 6.723, [(1.419, 2.218)])
    interior(c, 2.358, 2.657, 6.349, 12.473, [(7.408, 8.506), (9.13, 9.97)])
    interior(c, 2.358, 14.351, 5.849, 6.349, [(7.045, 7.944), (11.004, 11.803)])
    interior(c, 8.557, 9.056, 0.415, 5.849, [(0.54, 2.938)])
    interior(c, 5.240, 5.490, 3.002, 5.849, [(3.631, 4.580)])
    interior(c, 9.051, 9.351, 8.876, 9.585)                 # offener Kamin – wall ends
    interior(c, 9.051, 9.351, 12.213, 12.473)
    interior(c, 0.31, 2.358, 10.10, 10.25)                  # new: Bad / WC Großeltern
    interior(c, 11.13, 11.28, 8.876, 12.473, [(9.6, 11.9)])  # new: Musikraum / Büro
    interior(c, 2.772, 5.240, 3.13, 3.29)                   # new: Speis / Essen
    interior(c, 12.25, 12.38, 6.349, 8.576, [(6.5, 8.45)])   # new: Windfang
    # Kachelofen
    box(c, "EG_Kachelofen", "Kachel", 9.06, 10.56, 4.34, 5.849, 0, 1.9)
    # stair 15 x 18.0/25.5, starts at x=11.19 and rises westwards to OG
    for i in range(1, 15):
        box(c, "EG_Treppe", "Holz", 11.19 - i * 0.255, 11.19 - (i - 1) * 0.255,
            7.56, 8.45, 0, i * 0.18)


# ---------------------------------------------------------------- OG
def build_og():
    c, z0, z1 = "OG", Z_OG, Z_OG_TOP
    fd = lambda a, b: (a, b, z0, 4.60, "FD", 1)
    win = lambda a, b, sh=1: (a, b, 3.62, 4.60, "W", sh)
    wall(c, 0, W_OUT, 12.485, D_OUT, z0, z1,
         [fd(3.88, 4.78), fd(6.97, 7.87), fd(10.03, 10.95), fd(12.91, 13.80)], out=+1)
    wall(c, 0, 0.31, 5.12, 12.485, z0, z1, [
        (11.26, 12.23, z0, 4.66, "FD"), (8.96, 9.95, z0, 4.66, "FD"),
        (6.77, 7.76, z0, 4.66, "FD"), (5.72, 6.32, 4.18, 4.78, "W")], out=-1)
    wall(c, 0.31, 2.71, 5.12, 5.46, z0, z1)
    wall(c, 2.37, 2.71, 0, 5.12, z0, z1, [(2.03, 2.92, 3.70, 4.70, "W", 1)], out=-1)
    wall(c, 2.71, W_OUT, 0, 0.40, z0, z1,
         [win(3.85, 4.70), win(6.84, 7.72), fd(9.84, 10.70), win(12.84, 13.70)], out=-1)
    wall(c, 14.575, W_OUT, 6.40, 12.485, z0, z1, [
        win(9.86, 10.78), (8.17, 8.47, 3.87, 4.30, "W"), (6.50, 7.50, z0, 4.60, "FD", 1)], out=+1)
    wall(c, 14.35, W_OUT, 0.40, 6.40, z0, z1, [win(1.74, 2.67), win(4.15, 5.04)], out=+1)
    # eave band between OG wall top and roof (north / south)
    box(c, "OG_Waende", "Putz", 0, W_OUT, 12.485, D_OUT, z1, roof_under(D_OUT))
    box(c, "OG_Waende", "Putz", 2.37, W_OUT, 0, 0.40, z1, roof_under(0))
    # interior
    H = DOOR_H
    interior(c, 0.31, 14.575, 8.57, 8.86, [(3.17, 4.15), (7.28, 8.17), (12.30, 13.18)], z0, z1, H)
    interior(c, 6.05, 6.21, 8.86, 12.485, (), z0, z1)
    interior(c, 9.08, 9.25, 8.86, 12.485, (), z0, z1)
    interior(c, 2.57, 2.71, 5.46, 8.57, [(7.66, 8.47)], z0, z1, H)
    interior(c, 2.71, 14.35, 6.06, 6.35,
             [(4.02, 4.87), (7.15, 8.17), (8.76, 9.65), (10.66, 11.51)], z0, z1, H)
    interior(c, 0.31, 1.57, 6.44, 6.54, [(0.55, 1.35)], z0, z1, H)   # WC 2,26
    interior(c, 1.57, 1.67, 5.46, 6.44, (), z0, z1)
    interior(c, 5.44, 5.59, 0.40, 6.06, (), z0, z1)
    interior(c, 5.59, 8.59, 2.62, 2.79, (), z0, z1)                  # HWR / Bad (new)
    interior(c, 8.59, 8.72, 0.40, 6.06, [(1.65, 2.58)], z0, z1, H)
    interior(c, 10.0, 10.15, 3.84, 6.06, (), z0, z1)                 # WC 2,30 (new)
    interior(c, 8.72, 10.0, 3.84, 3.98, (), z0, z1)


# ---------------------------------------------------------------- slabs / floors
FOOT = [(0, W_OUT, 5.145, D_OUT), (2.358, W_OUT, 0, 5.145)]
STAIR_HOLE = (7.60, 11.25, 7.55, 8.45)


def slab(coll, obj, mat, z0, z1, inset=0.0, hole=None):
    for i, (x0, x1, y0, y1) in enumerate(FOOT):
        # the southern rectangle keeps its top edge so both parts join without a seam
        x0, x1, y0, y1 = x0 + inset, x1 - inset, y0 + inset, y1 - (inset if i == 0 else -inset)
        if hole and y0 <= hole[2] and hole[3] <= y1:
            hx0, hx1, hy0, hy1 = hole
            box(coll, obj, mat, x0, x1, y0, hy0, z0, z1)
            box(coll, obj, mat, x0, x1, hy1, y1, z0, z1)
            box(coll, obj, mat, x0, hx0, hy0, hy1, z0, z1)
            box(coll, obj, mat, hx1, x1, hy0, hy1, z0, z1)
        else:
            box(coll, obj, mat, x0, x1, y0, y1, z0, z1)


def build_slabs():
    slab("EG", "EG_Bodenplatte", "Decke", -0.30, 0.0)
    slab("EG", "EG_Boden", "Boden", 0.0, 0.01, inset=0.2)
    slab("OG", "OG_Decke_EG", "Decke", Z_EG_TOP, Z_OG, hole=STAIR_HOLE)
    slab("OG", "OG_Boden", "Boden", Z_OG, Z_OG + 0.01, inset=0.2, hole=STAIR_HOLE)
    slab("Dach", "Decke_OG", "Decke", Z_OG_TOP, Z_ATTIC)


# ---------------------------------------------------------------- roof & gables
def gable(x0, x1, y0, y1, windows=(), woff=0.7):
    c = "Dach"
    zb = Z_OG_TOP
    cuts = sorted(windows)
    edges, cur = [], y0
    for ya, yb, zw in cuts:
        edges.append((cur, ya, None)); edges.append((ya, yb, zw)); cur = yb
    edges.append((cur, y1, None))
    top_w = lambda y: roof_top(y) - woff
    xm = (x0 + x1) / 2
    for ya, yb, zw in edges:
        if yb - ya < 1e-4:
            continue
        if zw is None:
            prism_x(c, "Giebel", "Putz", x0, x1, roof_profile(ya, yb, lambda y: zb, roof_under))
        else:
            prism_x(c, "Giebel", "Putz", x0, x1, roof_profile(ya, yb, lambda y: zb, lambda y: zw))
            prism_x(c, "Giebel", "Putz", x0, x1, roof_profile(ya, yb, top_w, roof_under))
            prism_x(c, "Giebel_Fenster", "Glas", xm - 0.005, xm + 0.005,
                    roof_profile(ya, yb, lambda y: zw, top_w))
            prism_x(c, "Giebel_Fenster", "Rahmen", xm - 0.04, xm + 0.04,
                    roof_profile(ya, yb, lambda y: zw, lambda y: zw + 0.06))
            prism_x(c, "Giebel_Fenster", "Rahmen", xm - 0.04, xm + 0.04,
                    roof_profile(ya, yb, lambda y: top_w(y) - 0.06, top_w))
            for yy in (ya, yb - 0.06):
                prism_x(c, "Giebel_Fenster", "Rahmen", xm - 0.04, xm + 0.04,
                        roof_profile(yy, yy + 0.06, lambda y: zw, top_w))


def build_roof():
    for ya, yb in [(-EAVE_OH, RIDGE_Y), (RIDGE_Y, D_OUT + EAVE_OH)]:
        prism_x("Dach", "Dach", "Dach", -GABLE_OH, W_OUT + GABLE_OH,
                [(ya, roof_top(ya)), (yb, roof_top(yb)), (yb, roof_under(yb)), (ya, roof_under(ya))])
    gable(14.575, W_OUT, 0, D_OUT, [(4.26, 6.21, 5.0), (6.90, 8.88, 5.0)], woff=0.78)   # Osten
    gable(0, 0.31, 5.145, D_OUT, [(5.69, 7.66, 5.0), (7.85, 9.83, 5.0)], woff=0.60)     # Westen
    gable(2.358, 2.772, 0, 5.475)                                                     # Westen, Rücksprung


# ---------------------------------------------------------------- balconies, terrace, surroundings
def balcony(name, x0, x1, y0, y1, ztop, sides, ph=0.86):
    c = "Balkone"
    box(c, name, "Putz", x0, x1, y0, y1, ztop - 0.25, ztop)
    t, zb, zt = 0.05, ztop - 0.10, ztop + ph
    # boards stand slightly proud of the slab edge (1 cm N/S, 2 cm E/W) so no two faces are
    # coplanar – coplanar faces z-fight (brown/white flicker in the film)
    if "N" in sides: box(c, name, "Holz", x0, x1, y1 - t + 0.01, y1 + 0.01, zb, zt)
    if "S" in sides: box(c, name, "Holz", x0, x1, y0 - 0.01, y0 + t - 0.01, zb, zt)
    if "E" in sides: box(c, name, "Holz", x1 - t + 0.02, x1 + 0.02, y0, y1, zb, zt)
    if "W" in sides: box(c, name, "Holz", x0 - 0.02, x0 + t - 0.02, y0, y1, zb, zt)


def build_outside():
    balcony("Balkon_OG_Nord", 0.17, 14.45, D_OUT, 14.17, Z_OG, "NEW")
    balcony("Balkon_OG_Ost", W_OUT, 16.085, 0.95, 11.75, Z_OG, "NES")
    balcony("Balkon_OG_Sued", 9.00, 12.93, -1.10, 0, Z_OG, "SEW")
    balcony("Balkon_EG_Nord", 0.17, 5.86, D_OUT, 14.08, 0.0, "NEW", ph=0.90)
    c = "Umgebung"
    # L-shaped terrace, 4 m wide, along the full south and east sides
    tw = 4.0
    box(c, "Terrasse", "Stein", 0, W_OUT + tw, -tw, 0, -0.10, -0.01)
    box(c, "Terrasse", "Stein", W_OUT, W_OUT + tw, 0, D_OUT, -0.10, -0.01)
    box(c, "Schuppen", "Kies", 0.10, 2.358, 0.20, 5.145, -0.05, -0.01)
    build_shed()
    box(c, "Gelaende", "Wiese", -20, 35, -25, 35, -0.30, -0.05)


def build_shed():
    """Wooden Schuppen in the SW corner (plan: thin double lines, no masonry). Leans against
    the house walls at x=2.358 (east) and y=5.145 (north); lean-to roof falling to the west.
    Height and door position are assumptions – not given in the drawings."""
    c, o = "Umgebung", "Schuppen_Holz"
    x0, x1, y0, y1, t = 0.0, 2.358, 0.0, 5.145, 0.10
    h_w, h_e = 2.20, 2.45                                   # eave (west) / top at house wall
    h = lambda x: h_w + (h_e - h_w) * (x - x0) / (x1 - x0)
    door = (1.90, 3.30)                                     # double door in the west wall
    # south wall; its top steps up with the roof slope
    box(c, o, "Holz", x0, x1, y0, y0 + t, 0, h_w)
    n = 12
    for i in range(n):
        xa, xb = x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n
        box(c, o, "Holz", xa, xb, y0, y0 + t, h_w, h((xa + xb) / 2))
    # west wall with double door
    box(c, o, "Holz", x0, x0 + t, y0 + t, door[0], 0, h_w)
    box(c, o, "Holz", x0, x0 + t, door[1], y1, 0, h_w)
    box(c, o, "Holz", x0, x0 + t, door[0], door[1], 2.00, h_w)
    for a, b in [(door[0], sum(door) / 2), (sum(door) / 2, door[1])]:
        box(c, o, "Tuer", x0 + 0.02, x0 + 0.06, a + 0.01, b - 0.01, 0.02, 2.00)
    # vertical battens on the outside for a board look
    for k in range(1, 26):
        y = y0 + k * 0.2
        if not (door[0] - 0.05 < y < door[1] + 0.05) and y < y1:
            box(c, o, "Laden", x0 - 0.02, x0, y - 0.02, y + 0.02, 0, h_w)
    for k in range(1, 12):
        x = x0 + k * 0.2
        box(c, o, "Laden", x - 0.02, x + 0.02, y0 - 0.02, y0, 0, h(x) - 0.02)
    # lean-to roof with small overhang to west and south
    ov = 0.25
    slope = (h_e - h_w) / (x1 - x0)
    xa, ya = x0 - ov, y0 - ov
    za = h_w - slope * ov
    base = [(xa, ya, za), (x1, ya, h_e), (x1, y1, h_e), (xa, y1, za)]
    v = base + [(x, y, z + 0.08) for x, y, z in base]
    add(c, o, "Dach", v, [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6),
                          (3, 0, 4, 7)])


# ---------------------------------------------------------------- reference plans (hidden)
def reference_plane(name, img, center, z):
    path = os.path.join(PROJECT, "input", img)
    im = bpy.data.images.load(path, check_existing=True)
    w, h = 841.92 / 28.3465, 595.32 / 28.3465          # A4 landscape at 1:100 in metres
    cx, cy = center
    me = bpy.data.meshes.new(name)
    me.from_pydata([(cx - w / 2, cy - h / 2, z), (cx + w / 2, cy - h / 2, z),
                    (cx + w / 2, cy + h / 2, z), (cx - w / 2, cy + h / 2, z)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = co
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = im
    nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    coll("Referenz").objects.link(ob)


def build_references():
    # page top-left in world coords: EG wall vectors put the outer SW corner at pt (170.27, 507.91)
    tlx, tly = -170.27 / 28.3465, 507.91 / 28.3465
    w, h = 841.92 / 28.3465, 595.32 / 28.3465
    reference_plane("Ref_Grundriss_EG", "grundriss_eg.png", (tlx + w / 2, tly - h / 2), 0.02)
    reference_plane("Ref_Grundriss_OG", "grundriss_og.png",
                    (tlx + w / 2 + 0.195, tly - h / 2 + 0.57), Z_OG + 0.02)


# ---------------------------------------------------------------- scene assembly
ROOT = "Haus"
SUBS = ["EG", "OG", "Dach", "Balkone", "Umgebung", "Referenz"]


def coll(name):
    return bpy.data.collections[name if name == ROOT else "FL_" + name]


def reset_collections():
    old = bpy.data.collections.get(ROOT)
    if old:
        for c in [old] + list(old.children_recursive):
            for ob in list(c.objects):
                me = ob.data
                bpy.data.objects.remove(ob)
                if me and me.users == 0:
                    bpy.data.meshes.remove(me)
        for c in list(old.children_recursive):
            bpy.data.collections.remove(c)
        bpy.data.collections.remove(old)
    root = bpy.data.collections.new(ROOT)
    bpy.context.scene.collection.children.link(root)
    for s in SUBS:
        root.children.link(bpy.data.collections.new("FL_" + s))


def flush_geometry():
    import bmesh
    for (c, name), g in GEO.items():
        me = bpy.data.meshes.new(name)
        me.from_pydata(g["v"], [], g["f"])
        mats = sorted(set(g["m"]))
        for m in mats:
            me.materials.append(MAT[m])
        me.polygons.foreach_set("material_index", [mats.index(m) for m in g["m"]])
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(name, me)
        coll(c).objects.link(ob)
    GEO.clear()


def setup_scene():
    sc = bpy.context.scene
    cube = bpy.data.objects.get("Cube")
    if cube and cube.data.name == "Cube":
        bpy.data.objects.remove(cube)
    # sun
    sun = bpy.data.objects.get("FL_Sonne")
    if not sun:
        sun = bpy.data.objects.new("FL_Sonne", bpy.data.lights.new("FL_Sonne", "SUN"))
        sc.collection.objects.link(sun)
    sun.data.energy = 4.0
    sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    old_light = bpy.data.objects.get("Light")
    if old_light:
        old_light.hide_viewport = old_light.hide_render = True
    # world
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.62, 0.76, 0.92, 1)
    bg.inputs["Strength"].default_value = 1.0
    # camera from south-east
    cam = sc.camera or bpy.data.objects.get("Camera")
    if cam:
        cam.location = (33.0, -24.0, 13.0)
        target = Vector((7.4, 6.4, 3.2))
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = 40
        cam.data.clip_end = 500
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    # reference plans hidden by default
    lc = bpy.context.view_layer.layer_collection.children[ROOT].children["FL_Referenz"]
    lc.hide_viewport = True
    coll("Referenz").hide_render = True


def main():
    make_materials()
    reset_collections()
    build_eg(); build_og(); build_slabs(); build_roof(); build_outside()
    flush_geometry()
    build_references()
    setup_scene()


main()
