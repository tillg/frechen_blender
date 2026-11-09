"""Frechenlehen – the pure-Python core: constants, materials as data, primitives and builders.

No bpy, no mathutils. build() returns a Blueprint; the backends turn it into output:
build_house.py (Blender scene) and export_gltf.py (glTF for the web viewer).
Coordinates in metres: origin = outer SW corner of the main house, +X = east, +Y = north, Z = up.
EG wall segments come from the vector data of "Grundriss Frechenlehen EG.pdf" (gray wall fills);
OG walls and all heights were measured from the plans/elevations (approx. +-5 cm).
Details (doors, balconies, cladding, terrace, lamps, eaves) follow the photos in input/.
"""
import math, random
from dataclasses import dataclass
import ofen  # the stoves (code/ofen.py); it uses the primitives below via house_core.*
import desk  # the Büro desk sub-model (code/desk.py), the same way
import bad   # the Bad Großeltern sub-model (code/bad.py), the same way
import kueche  # the Küche sub-model (code/kueche.py), the same way

W_OUT, D_OUT = 14.885, 12.887           # outer footprint of main house
RIDGE_Y, RIDGE_Z = D_OUT / 2, 7.67      # ridge runs east-west (elevations: 7.65-7.69)
SLOPE, ROOF_T = 0.3635, 0.10            # ~20 deg pitch; thin eave edge as drawn
EAVE_OH, GABLE_OH = 1.34, 1.49          # overhang at eaves (N/S) and gables (E/W), measured
Z_EG_TOP, Z_OG, Z_OG_TOP, Z_ATTIC = 2.40, 2.70, 4.90, 5.10
DOOR_H = 2.0                            # interior door height
SOFFIT = 0.02                           # board layer under the roof
ANNEX = (-1.64, 2.358, 0.25, 5.145)     # Elektroraum/Heizung annex, outside x0, x1, y0, y1 (plan)
ANNEX_TOP = 2.42                        # its flat roof top (elevations)


def roof_top(y):
    return RIDGE_Z - SLOPE * abs(y - RIDGE_Y)


def roof_under(y):
    return roof_top(y) - ROOF_T


# ---------------------------------------------------------------- materials
# rgba: plain colour. wood: (dark, light, grain axis) – procedural grain in object space.
# speck: (c1, c2, scale) – speckled stone. bump: (scale, strength). "rnd" face attribute
# (one random value per part) varies brightness so boards and slabs read as single pieces.
WOOD_OLD = ((0.045, 0.032, 0.024), (0.17, 0.12, 0.085))       # weathered wood (back door)
MAT_DEF = {
    "Putz":       dict(rgba=(0.93, 0.92, 0.88, 1), bump=(45, 0.6)),
    "Decke":      dict(rgba=(0.80, 0.80, 0.78, 1)),
    "Dach":       dict(rgba=(0.17, 0.17, 0.19, 1)),
    "Holz":       dict(wood=(*WOOD_OLD, "z")),
    "Rahmen":     dict(rgba=(0.45, 0.28, 0.14, 1)),
    "Laden":      dict(rgba=(0.30, 0.17, 0.08, 1)),
    "Tuer":       dict(wood=((0.07, 0.022, 0.006), (0.36, 0.11, 0.028), "z")),   # stained larch
    "Innentuer":  dict(wood=((0.22, 0.11, 0.035), (0.42, 0.25, 0.09), "z")),    # pine
    "Kiefer":     dict(wood=((0.30, 0.21, 0.12), (0.55, 0.43, 0.29), "z")),    # limed pine (stair)
    "Stufe":      dict(wood=((0.20, 0.07, 0.02), (0.42, 0.17, 0.05), "x")),    # worn treads
    "Eiche":      dict(wood=((0.06, 0.025, 0.008), (0.26, 0.11, 0.035), "x")),    # oak planks
    "Kalkstein":  dict(speck=((0.40, 0.28, 0.16), (0.62, 0.48, 0.32), 25), hue=0.04),
    "Laerche":    dict(wood=((0.38, 0.14, 0.040), (0.62, 0.27, 0.085), "z")),   # fresh larch
    "FichteX":    dict(wood=((0.42, 0.20, 0.07), (0.70, 0.42, 0.18), "x")),     # spruce soffit
    "FichteY":    dict(wood=((0.42, 0.20, 0.07), (0.70, 0.42, 0.18), "y")),
    "FichteZ":    dict(wood=((0.42, 0.20, 0.07), (0.70, 0.42, 0.18), "z")),
    "NussX":      dict(wood=((0.035, 0.016, 0.007), (0.13, 0.06, 0.025), "x")),   # dark walnut (bookcase)
    "NussZ":      dict(wood=((0.035, 0.016, 0.007), (0.13, 0.06, 0.025), "z")),
    "TeakX":      dict(wood=((0.16, 0.07, 0.025), (0.40, 0.20, 0.08), "x")),     # Stube side table, armchair legs
    "TeakZ":      dict(wood=((0.16, 0.07, 0.025), (0.40, 0.20, 0.08), "z")),
    "Buecher":    dict(speck=((0.07, 0.018, 0.010), (0.10, 0.028, 0.016), 300), hue=0.4),   # one dark colour per book
    "Glas":       dict(rgba=(0.70, 0.85, 0.95, 0.25), alpha=0.25, rough=0.1),
    "Milchglas":  dict(rgba=(0.90, 0.90, 0.88, 0.85), alpha=0.85, rough=0.4),
    "Wiese":      dict(speck=((0.05, 0.12, 0.025), (0.12, 0.20, 0.04), 3)),
    "Feuer":      dict(rgba=(1.0, 0.22, 0.02, 1), emit=2.0),               # flames (code/fire.py): outer
    "FeuerKern":  dict(rgba=(1.0, 0.70, 0.12, 1), emit=2.6),               # inner, brighter core
    "Kies":       dict(speck=((0.30, 0.28, 0.25), (0.62, 0.60, 0.56), 150), bump=(150, 0.5)),
    "Erde":       dict(speck=((0.025, 0.014, 0.008), (0.07, 0.04, 0.022), 60), bump=(60, 0.6)),
    "Granit":     dict(speck=((0.30, 0.29, 0.26), (0.62, 0.58, 0.50), 220), hue=0.06),
    "Fuge":       dict(rgba=(0.16, 0.16, 0.15, 1)),
    "Kiesel":     dict(rgba=(0.52, 0.50, 0.46, 1), rough=0.5),
    "Ofenglas":   dict(rgba=(0.10, 0.08, 0.06, 0.15), alpha=0.15, rough=0.05),  # stove door
    "Leinen":     dict(rgba=(0.78, 0.74, 0.66, 1), rough=0.9),               # mattress
    "Bettwaesche": dict(rgba=(0.92, 0.91, 0.88, 1), rough=0.9),              # duvet, pillows
    "Creme":      dict(rgba=(0.84, 0.72, 0.50, 1), rough=0.9),              # Ofen mattress
    "Boucle":     dict(speck=((0.93, 0.85, 0.70), (0.46, 0.23, 0.07), 55)),    # armchairs: cream with brown flecks
    "Paspel":     dict(rgba=(0.38, 0.23, 0.11, 1), rough=0.6),               # their piping
    "Schiefer":   dict(rgba=(0.14, 0.13, 0.12, 1), rough=0.5),               # dark stone behind the Flur sink
    "Klavierlack": dict(rgba=(0.015, 0.015, 0.017, 1), rough=0.12),          # grand piano
    "Schrift":    dict(rgba=(0.80, 0.76, 0.66, 1), rough=0.6),               # cream, reads on oak
    "Keramik":    dict(rgba=(0.90, 0.90, 0.88, 1), rough=0.08),
    "Fliese":     dict(speck=((0.018, 0.075, 0.032), (0.030, 0.115, 0.050), 8), hue=0.03, rough=0.12),   # WC tiles
    "Fugengrau":  dict(rgba=(0.42, 0.42, 0.40, 1)),                         # their grout
    "Spiegel":    dict(rgba=(0.92, 0.92, 0.92, 1), metal=1.0, rough=0.02),
    "Eisen":      dict(rgba=(0.018, 0.018, 0.02, 1), metal=0.4, rough=0.45),
    "Metall":     dict(rgba=(0.60, 0.60, 0.62, 1), metal=1.0, rough=0.3),
    "Gitter":     dict(rgba=(0.72, 0.67, 0.55, 1), rough=0.6),
    "Emaille":    dict(rgba=(0.86, 0.86, 0.84, 1), rough=0.2),
"Herd":       dict(rgba=(0.15, 0.16, 0.15, 1), metal=0.5, rough=0.35),   # Wamsler: grey enamelled steel
    "Weide":      dict(speck=((0.30, 0.19, 0.08), (0.62, 0.45, 0.22), 150)),     # wicker laundry baskets
    "Jeans":      dict(rgba=(0.12, 0.18, 0.30, 1), rough=0.9),               # folded clothes
    "Wolle":      dict(rgba=(0.45, 0.14, 0.10, 1), rough=0.95),
    "Gluehfaden": dict(rgba=(1.0, 0.55, 0.2, 1), emit=25.0, night=True),   # viewer: lit at dusk only
    "GluehfadenAn": dict(rgba=(1.0, 0.55, 0.2, 1), emit=25.0),              # switched-on lamp (Ofen bed)
    "Alu":        dict(rgba=(0.72, 0.72, 0.74, 1), metal=0.15, rough=0.35),   # desk: MacBook, keyboard, monitor stands
    "Tasten":     dict(rgba=(0.93, 0.93, 0.92, 1), rough=0.45),             # white keys, trackpad glass
    "Apfel":      dict(rgba=(0.95, 0.95, 0.97, 1), emit=0.5, rough=0.3),   # the softly lit logo on the closed MacBook
    # image: screenshot under web/public/ (2560 x 1440, made once from input/2026-11-06 input/ with
    # sips: downscaled, padded to 16:9); size: the pane's w, h in metres. The pane is its own object
    # with the pivot at its lower-left corner; object-space x/w, z/h map to the image
    "Bildschirm_A12":     dict(rgba=(0.55, 0.60, 0.66, 1), image="textures/screen_a12.jpg", size=(0.697, 0.392), emit=0.8, rough=0.2),
    "Bildschirm_Pilcrow": dict(rgba=(0.70, 0.72, 0.70, 1), image="textures/screen_pilcrow.jpg", size=(0.697, 0.392), emit=0.8, rough=0.2),
}
# RAL colours (sRGB 0-255) that override the base colour of plain materials (paint.py, viewer):
# facade and windows RAL 9010 Reinweiß, shutters RAL 5014 Taubenblau
RAL_9010, RAL_5014 = (241, 236, 225), (99, 125, 150)
PAINT = {"Putz": RAL_9010, "Rahmen": RAL_9010, "Laden": RAL_5014}

GEO = {}      # (collection, object) -> {"v": [...], "f": [...], "m": [...], "r": [...]}
SMOOTH = set()  # objects shaded smooth
PIVOT = {}    # object -> origin (for parts that get animated, e.g. the entrance door)
TURN = {}     # object -> its rotation about the vertical through its PIVOT, degrees (counter-
              # clockwise from above): the backends store its mesh unturned (local()) and turn the
              # object, so object space runs along it (the desk's angled screen panes)
SLIDE = {}    # object -> (dx, dy, dz) to its other end of travel (the Bad's sliding leaves): the
              # sub-model viewer rolls it there and back


def local(p, piv, turn=0.0):
    """World point p in the object space of an object with origin piv, turned by `turn` degrees."""
    a = math.radians(-turn)
    x, y, z = p[0] - piv[0], p[1] - piv[1], p[2] - piv[2]
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z)
OPENINGS = []  # exterior wall openings, used by the west cladding
FIRES = []     # fire beds for the animated fire component (code/fire.py): dict(base, u, w, h, d)
LEAVES = []    # opened interior door leaves (collection, [corner, corner]) – for clash checks
GABLE_WIN = []
PARTS = {}     # (collection, object) -> [(first_face, n_faces), ...]: one closed solid per add()


def add(coll, obj, mat, verts, faces, rnd=None):
    g = GEO.setdefault((coll, obj), {"v": [], "f": [], "m": [], "r": []})
    PARTS.setdefault((coll, obj), []).append((len(g["f"]), len(faces)))
    off = len(g["v"])
    g["v"] += verts
    r = random.random() if rnd is None else rnd
    for f in faces:
        g["f"].append([i + off for i in f])
        g["m"].append(mat)
        g["r"].append(r)


def box(coll, obj, mat, x0, x1, y0, y1, z0, z1, rnd=None):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    if min(x1 - x0, y1 - y0, z1 - z0) < 1e-4:
        return
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    add(coll, obj, mat, v, f, rnd)


def prism_x(coll, obj, mat, x0, x1, prof, rnd=None):
    """Extrude a (y, z) profile polygon from x0 to x1."""
    n = len(prof)
    v = [(x0, y, z) for y, z in prof] + [(x1, y, z) for y, z in prof]
    f = [list(range(n))[::-1], list(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    add(coll, obj, mat, v, f, rnd)


def roof_profile(ya, yb, fb, ft):
    ys = [ya] + ([RIDGE_Y] if ya < RIDGE_Y < yb else []) + [yb]
    return [(y, fb(y)) for y in ys] + [(y, ft(y)) for y in reversed(ys)]


# Local frames: u runs along a wall, t across it, z up. P maps (u, t, z) to world.
def frame(ax):
    return (lambda u, t, z: (u, t, z)) if ax == "x" else (lambda u, t, z: (t, u, z))


def lbox(coll, obj, mat, P, u0, u1, t0, t1, z0, z1, rnd=None):
    a, b = P(u0, t0, z0), P(u1, t1, z1)
    box(coll, obj, mat, a[0], b[0], a[1], b[1], a[2], b[2], rnd)


def sweep(coll, obj, mat, P, pairs, t0, t1, rnd=None):
    """Closed band through a list of ((u, z) bottom, (u, z) top) cross sections, extruded t0..t1.
    Covers arches (bottom = arc), sloped board tops, scalloped edges and annulus sectors."""
    if len(pairs) < 2:
        return
    v = []
    for (ub, zb), (ut, zt) in pairs:
        v += [P(ub, t0, zb), P(ub, t1, zb), P(ut, t0, zt), P(ut, t1, zt)]
    f = []
    for i in range(len(pairs) - 1):
        a, b = 4 * i, 4 * i + 4
        f += [(a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1),
              (a, a + 1, b + 1, b), (a + 2, b + 2, b + 3, a + 3)]
    e = 4 * (len(pairs) - 1)
    f += [(0, 2, 3, 1), (e, e + 1, e + 3, e + 2)]
    add(coll, obj, mat, v, f, rnd)


def column(coll, obj, mat, P, u0, u1, zb, zt, t0, t1, rnd=None):
    """Board between u0..u1 whose bottom/top follow zb(u)/zt(u) (evaluated at both ends)."""
    sweep(coll, obj, mat, P, [((u, zb(u)), (u, zt(u))) for u in (u0, u1)], t0, t1, rnd)


def prism(coll, obj, mat, P, pts, t0, t1, rnd=None):
    """Extrude a (u, z) polygon (may be concave, e.g. a board with notches) from t0 to t1."""
    n = len(pts)
    v = [P(u, t0, z) for u, z in pts] + [P(u, t1, z) for u, z in pts]
    f = [list(range(n))[::-1], list(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    add(coll, obj, mat, v, f, rnd)


def const(c):
    return lambda u: c


def boards(coll, obj, mat, P, u0, u1, zb, zt, t0, t1, bw, holes=(), cuts=(), alt=0.004):
    """Vertical boards side by side from u0 to u1, bottom/top zb(u)/zt(u), skipping holes.

    holes: (ua, ub, lo(u), hi(u), curved) – the board part between lo and hi is left out.
    Curved holes are sampled every 2 cm so their outline stays smooth. cuts: extra u values
    where boards are split (e.g. the ridge, where the top line kinks). Every other board
    stands `alt` proud on both faces so the joints read as shadow lines."""
    edges = [u0 + k * bw for k in range(int((u1 - u0) / bw) + 1)] + [u1]
    edges = sorted(set(round(e, 5) for e in edges if u0 <= e <= u1))
    for k, (ba, bb) in enumerate(zip(edges[:-1], edges[1:])):
        if bb - ba < 0.005:
            continue
        pts = {ba, bb} | {c for c in cuts if ba < c < bb}
        for ua, ub, lo, hi, curved in holes:
            pts |= {p for p in (ua, ub) if ba < p < bb}
            if curved:
                n = int((min(bb, ub) - max(ba, ua)) / 0.02)
                pts |= {max(ba, ua) + (min(bb, ub) - max(ba, ua)) * i / (n + 1) for i in range(1, n + 1)}
        pts = sorted(pts)
        r, d = random.random(), alt * (k % 2)
        for p, q in zip(pts[:-1], pts[1:]):
            m = (p + q) / 2
            segs = [(zb, zt)]
            for ua, ub, lo, hi, _ in holes:
                if not (ua - 1e-6 <= p and q <= ub + 1e-6):
                    continue
                new = []
                for fb, ft in segs:
                    if lo(m) > fb(m) + 1e-4:
                        new.append((fb, (lambda u, ft=ft, lo=lo: min(ft(u), lo(u)))))
                    if hi(m) < ft(m) - 1e-4:
                        new.append(((lambda u, fb=fb, hi=hi: max(fb(u), hi(u))), ft))
                segs = new
            for fb, ft in segs:
                if ft(m) - fb(m) > 1e-3:
                    column(coll, obj, mat, P, p, q, fb, ft, t0 - d, t1 + d, r)


# ---------------------------------------------------------------- walls with openings
def wall(coll, x0, x1, y0, y1, z0, z1, ops=(), out=0, mat="Putz"):
    """Straight wall (axis-aligned box) with openings.

    ops: (a, b, sill, head, kind[, shutters]) along the wall's long axis.
    kind: W window, FD french door, GD glazed terrace door (larch, 4x2 panes per leaf), D solid
          door, I opening without fill (filled by a dedicated door builder).
    out: +1 / -1 = side of the thin axis that faces outside (for shutters).
    Windows / french doors after window_from_outside.jpeg: larch frame, one or two sashes,
    each divided by glazing bars (windows 2 panes high, french doors 3).
    """
    obj, fo = coll + "_Waende", coll + "_Fenster_Tueren"
    ax = "x" if (x1 - x0) >= (y1 - y0) else "y"
    u0, u1, t0, t1 = (x0, x1, y0, y1) if ax == "x" else (y0, y1, x0, x1)

    # all parts of one opening share one "rnd" value: frame pieces overlap at the corners in
    # the same plane, so they must shade identically or they z-fight
    st = {"r": None}

    def B(m, ua, ub, ta, tb, za, zb, o=obj):
        if ax == "x":
            box(coll, o, m, ua, ub, ta, tb, za, zb, st["r"])
        else:
            box(coll, o, m, ta, tb, ua, ub, za, zb, st["r"])

    cur = u0
    for op in sorted(ops):
        st["r"] = random.random()
        a, b, sill, head, kind = op[:5]
        sh = len(op) > 5 and op[5]
        if out:
            OPENINGS.append(dict(ax=ax, face=t0 if out < 0 else t1, a=a, b=b, sill=sill, head=head,
                                 kind=kind))
        B(mat, cur, a, t0, t1, z0, z1)
        B(mat, a, b, t0, t1, z0, sill)
        if head < z1:
            B(mat, a, b, t0, t1, head, z1)
        cur = b
        if kind == "I":
            continue
        tm, fd, fw = (t0 + t1) / 2, 0.04, 0.06
        if kind == "GD":
            glazed_door(B, fo, a, b, sill, head, tm)
            continue
        F = "Laerche"
        B(F, a, a + fw, tm - fd, tm + fd, sill, head, fo)
        B(F, b - fw, b, tm - fd, tm + fd, sill, head, fo)
        B(F, a, b, tm - fd, tm + fd, head - fw, head, fo)
        if kind == "D":
            B("Tuer", a + fw, b - fw, tm - 0.025, tm + 0.025, sill, head - fw, fo)
        else:
            B(F, a, b, tm - fd, tm + fd, sill, sill + fw, fo)
            za, zb = sill + fw, head - fw
            n = 2 if b - a > 0.75 else 1
            rows = 3 if zb - za > 1.48 else 2
            sw, sf, gb = (b - a - 2 * fw) / n, 0.05, 0.03
            for k in range(n):                                   # sashes
                sa, sb = a + fw + k * sw, a + fw + (k + 1) * sw
                B(F, sa, sa + sf, tm - 0.03, tm + 0.03, za, zb, fo)
                B(F, sb - sf, sb, tm - 0.03, tm + 0.03, za, zb, fo)
                B(F, sa, sb, tm - 0.03, tm + 0.03, za, za + sf * 1.4, fo)
                B(F, sa, sb, tm - 0.03, tm + 0.03, zb - sf, zb, fo)
                g0, g1 = za + sf * 1.4, zb - sf
                for r in range(1, rows):
                    zr = g0 + (g1 - g0) * (0.52 if rows == 2 else r / rows)
                    B(F, sa + sf, sb - sf, tm - 0.02, tm + 0.02, zr - gb / 2, zr + gb / 2, fo)
                B("Glas", sa + sf, sb - sf, tm - 0.004, tm + 0.004, g0, g1, fo)
        if sh and out:
            w = (b - a) / 2
            ta, tb = (t1, t1 + 0.03) if out > 0 else (t0 - 0.03, t0)
            B("Laden", a - w, a - 0.02, ta, tb, sill, head, coll + "_Laeden")
            B("Laden", b + 0.02, b + w, ta, tb, sill, head, coll + "_Laeden")
    B(mat, cur, u1, t0, t1, z0, z1)


def glazed_door(B, fo, a, b, sill, head, tm):
    """Terrace door after glass_door_to_terrasse.jpg: larch frame, leaves of ~0.95 m (at least
    two), each with 2 x 4 panes. Also used for the big west windows."""
    M, fw = "Laerche", 0.07
    B(M, a, a + fw, tm - 0.045, tm + 0.045, sill, head, fo)
    B(M, b - fw, b, tm - 0.045, tm + 0.045, sill, head, fo)
    B(M, a, b, tm - 0.045, tm + 0.045, head - fw, head, fo)
    B(M, a, b, tm - 0.045, tm + 0.045, sill, sill + 0.03, fo)
    n = max(2, round((b - a) / 0.95))
    lw = (b - a - 2 * fw) / n
    za, zb = sill + 0.03, head - fw
    for k in range(n):
        la, lb = a + fw + k * lw, a + fw + (k + 1) * lw
        st, tr, br = 0.07, 0.07, 0.12
        B(M, la, la + st, tm - 0.035, tm + 0.035, za, zb, fo)
        B(M, lb - st, lb, tm - 0.035, tm + 0.035, za, zb, fo)
        B(M, la, lb, tm - 0.035, tm + 0.035, zb - tr, zb, fo)
        B(M, la, lb, tm - 0.035, tm + 0.035, za, za + br, fo)
        ga, gb, g0, g1 = la + st, lb - st, za + br, zb - tr
        B("Glas", ga, gb, tm - 0.004, tm + 0.004, g0, g1, fo)
        c = (ga + gb) / 2
        B(M, c - 0.017, c + 0.017, tm - 0.025, tm + 0.025, g0, g1, fo)
        for r in (1, 2, 3):
            zr = g0 + (g1 - g0) * r / 4
            B(M, ga, gb, tm - 0.025, tm + 0.025, zr - 0.017, zr + 0.017, fo)


def interior(coll, x0, x1, y0, y1, doors=(), z0=0.0, z1=Z_EG_TOP, head=DOOR_H, ops=()):
    """doors: (a, b) = open passage, or (a, b, swing, hinge[, flat]) = opening with an opened
    door leaf; swing +1/-1 = room side along the thin axis, hinge "a"/"b" = which jamb carries
    the leaf, flat=False: leaf at 90 deg instead of against the wall (see panel_door).
    ops: further wall() openings, e.g. the fire window."""
    wall(coll, x0, x1, y0, y1, z0, z1, [(d[0], d[1], z0, z0 + head, "I") for d in doors] + list(ops))
    ax = "x" if (x1 - x0) >= (y1 - y0) else "y"
    t0, t1 = (y0, y1) if ax == "x" else (x0, x1)
    for d in doors:
        if len(d) > 2:
            panel_door(coll, ax, d[0], d[1], t0, t1, z0, z0 + head, *d[2:])


# ---------------------------------------------------------------- doors
def panel_door(coll, ax, a, b, t0, t1, z0, head, swing, hinge, flat=True, style="panel", mat="Innentuer"):
    """Interior door after door_inside_1st_floor.jpg: pine, six panels (2 small on top,
    2 tall, 2 lower), lining + architraves. The leaf is opened fully and lies flat against
    the room-side wall face next to the hinge jamb, so the walkthrough camera passes freely;
    flat=False (a room corner is too close for that): opened 90 deg into the room.
    hinge "ab" = double door (one leaf on each jamb). style "glazed" = Windfang door after
    door_windfang.jpg: frosted 2 x 2 panes above, two raised panels below, heavy head casing."""
    P, o, lin, arc, LT = frame(ax), coll + "_Innentueren", 0.025, 0.07, 0.04
    # thick walls keep a plaster reveal; the frame only lines the room-side 12 cm
    d = min(t1 - t0, 0.12)
    la, lb = (t1 - d, t1) if swing > 0 else (t0, t0 + d)
    for ua, ub in ((a, a + lin), (b - lin, b)):
        lbox(coll, o, mat, P, ua, ub, la, lb, z0, head)
    lbox(coll, o, mat, P, a, b, la, lb, head - lin, head)
    faces = [(t0 - 0.015, t0), (t1, t1 + 0.015)] if d == t1 - t0 else \
        [(t1, t1 + 0.015)] if swing > 0 else [(t0 - 0.015, t0)]
    for ta, tb in faces:
        lbox(coll, o, mat, P, a - arc, a + lin, ta, tb, z0, head + arc)
        lbox(coll, o, mat, P, b - lin, b + arc, ta, tb, z0, head + arc)
        lbox(coll, o, mat, P, a - arc, b + arc, ta, tb, head - lin, head + arc)
        if style == "glazed":                                      # heavy head board on top
            tp = (ta - 0.02, tb) if ta < t0 else (ta, tb + 0.02)
            lbox(coll, o, mat, P, a - arc - 0.03, b + arc + 0.03, *tp, head + arc, head + arc + 0.10)
    hinges = ["a", "b"] if hinge == "ab" else [hinge]
    LW, LH = (b - a - 2 * lin) / len(hinges) - 0.006, head - lin - z0 - 0.015
    tf = t1 if swing > 0 else t0
    zl = z0 + 0.01
    for hg in hinges:
        rl = 0.8 + 0.2 * random.random()                          # stiles/rails light, panels darker
        if flat:
            uh, su = (a, -1) if hg == "a" else (b, 1)             # leaf runs away from the opening
            off = 0.017 + LT / 2                                  # clear of the architrave
            L = lambda w, d, uh=uh, su=su, off=off: (uh + su * w, tf + swing * (off + d))
        else:
            uh, su = (a + lin, 1) if hg == "a" else (b - lin, -1)
            L = lambda w, d, uh=uh, su=su: (uh + su * (d + LT / 2), tf + swing * w)

        def part(w0, w1, d0, d1, za, zb, r=rl, m=mat, L=L):     # leaf-local: w from hinge, d across
            (ua, ta), (ub, tb) = L(w0, d0), L(w1, d1)
            lbox(coll, o, m, P, ua, ub, ta, tb, zl + za, zl + zb, r)

        LEAVES.append((coll, [P(*L(0, -LT / 2), zl), P(*L(LW, LT / 2), zl + LH)]))
        (glazed_leaf if style == "glazed" else six_panel_leaf)(part, LW, LH)


def six_panel_leaf(part, LW, LH):
    part(0, LW, -0.012, 0.012, 0, LH, 0.05)                        # core = panel ground
    rows = [0.091, 0.271, 0.112, 0.31, 0.05, 0.149, 0.046]         # bottom -> top, from the photo
    s = LH / sum(rows)
    zs = [0]
    for r in rows:
        zs.append(zs[-1] + r * s)
    st, mu = 0.09 / 0.82 * LW, 0.13 / 0.82 * LW
    cols = [(st, (LW - mu) / 2), ((LW + mu) / 2, LW - st)]
    part(0, st, -0.02, 0.02, 0, LH)
    part(LW - st, LW, -0.02, 0.02, 0, LH)
    part((LW - mu) / 2, (LW + mu) / 2, -0.02, 0.02, 0, LH)
    for i in (0, 2, 4, 6):                                         # rails
        part(st, LW - st, -0.02, 0.02, zs[i], zs[i + 1])
    for i in (1, 3, 5):                                            # raised fields
        for wa, wb in cols:
            part(wa + 0.03, wb - 0.03, -0.016, 0.016, zs[i] + 0.03, zs[i + 1] - 0.03, 0.4)


def glazed_leaf(part, LW, LH):
    """door_windfang.jpg, bottom -> top: rail, panel, rail, panel, lock rail, frosted glass
    (2 x 2 panes, top row short), top rail."""
    rows = [0.07, 0.13, 0.04, 0.13, 0.09, 0.47, 0.07]
    s = LH / sum(rows)
    zs = [0]
    for r in rows:
        zs.append(zs[-1] + r * s)
    st = 0.13 * LW
    part(0, st, -0.02, 0.02, 0, LH)
    part(LW - st, LW, -0.02, 0.02, 0, LH)
    for i in (0, 2, 4, 6):                                         # rails
        part(st, LW - st, -0.02, 0.02, zs[i], zs[i + 1])
    for i in (1, 3):                                               # panels: ground + raised field
        part(st, LW - st, -0.012, 0.012, zs[i], zs[i + 1], 0.05)
        part(st + 0.03, LW - st - 0.03, -0.016, 0.016, zs[i] + 0.03, zs[i + 1] - 0.03, 0.4)
    g0, g1 = zs[5], zs[6]
    part(st, LW - st, -0.003, 0.003, g0, g1, m="Milchglas")
    c = LW / 2
    part(c - 0.015, c + 0.015, -0.015, 0.015, g0, g1)                        # glazing bars
    zb = g0 + (g1 - g0) * 0.76
    part(st, LW - st, -0.015, 0.015, zb - 0.015, zb + 0.015)
    for dd in (-1, 1):                                                       # black lever handles
        h = LW - st / 2                                                      # on the free-edge stile
        part(h - 0.02, h + 0.02, dd * 0.02, dd * 0.03, zs[4], zs[4] + 0.16, 0.5, "Eisen")
        part(h - 0.14, h, dd * 0.03, dd * 0.045, zs[4] + 0.10, zs[4] + 0.12, 0.5, "Eisen")


def entrance_door():
    """Main entrance (east wall) after entrance_door_from_outside.png / main_door_seen_from_inside:
    round-arched opening with a thick plaster surround, dark stained board door with a small
    square window and black iron fittings. The leaf is its own object (pivot = hinge) so the
    film can swing it open."""
    c, P = "EG", frame("y")
    a, b, head, t0, t1 = 6.458, 7.507, 2.2, 14.575, W_OUT
    R, uc, tm, fw = (b - a) / 2, (a + b) / 2, (t0 + t1) / 2, 0.07
    zs = head - R
    arc = lambda r, n=32: [(uc - r * math.cos(math.pi * i / n), zs + r * math.sin(math.pi * i / n))
                           for i in range(n + 1)]
    # plaster between the rectangular wall opening and the arch
    sweep(c, "EG_Waende", "Putz", P, [(p, (p[0], head)) for p in arc(R)], t0, t1)
    # raised plaster surround on the outside face
    sweep(c, "EG_Waende", "Putz", P, list(zip(arc(R), arc(R + 0.16))), t1, t1 + 0.04)
    lbox(c, "EG_Waende", "Putz", P, a - 0.16, a, t1, t1 + 0.04, 0, zs)
    lbox(c, "EG_Waende", "Putz", P, b, b + 0.16, t1, t1 + 0.04, 0, zs)
    # frame
    o = "EG_Fenster_Tueren"
    lbox(c, o, "Tuer", P, a, a + fw, tm - 0.05, tm + 0.05, 0, zs)
    lbox(c, o, "Tuer", P, b - fw, b, tm - 0.05, tm + 0.05, 0, zs)
    sweep(c, o, "Tuer", P, list(zip(arc(R - fw), arc(R))), tm - 0.05, tm + 0.05)
    # leaf: vertical boards clipped by the arch, square window
    o, ri = "EG_Haustuer", R - fw - 0.004
    top = lambda u: zs + math.sqrt(max(ri * ri - (u - uc) ** 2, 0))
    wa, wb, w0, w1 = uc - 0.14, uc + 0.14, 1.46, 1.81
    boards(c, o, "Tuer", P, a + fw + 0.004, b - fw - 0.004, const(0.01), top,
           tm - 0.025, tm + 0.025, 0.095, holes=[(wa, wb, const(w0), const(w1), False)], alt=0.01,
           cuts=[uc - ri + 0.01 * i for i in range(1, 12)] + [uc + ri - 0.01 * i for i in range(1, 12)])
    lbox(c, o, "Glas", P, wa, wb, tm - 0.003, tm + 0.003, w0, w1)
    for s in (1, -1):
        ts = tm + s * 0.025
        tt = ts + s * 0.012
        lbox(c, o, "Tuer", P, wa - 0.03, wb + 0.03, ts, tt, w0 - 0.03, w0)       # window moulding
        lbox(c, o, "Tuer", P, wa - 0.03, wb + 0.03, ts, tt, w1, w1 + 0.03)
        lbox(c, o, "Tuer", P, wa - 0.03, wa, ts, tt, w0, w1)
        lbox(c, o, "Tuer", P, wb, wb + 0.03, ts, tt, w0, w1)
        hu = b - fw - 0.09                                                     # handle side = north
        lbox(c, o, "Eisen", P, hu - 0.025, hu + 0.025, ts, ts + s * 0.01, 0.92, 1.2)
        lbox(c, o, "Eisen", P, hu - 0.012, hu + 0.012, ts, ts + s * 0.05, 1.10, 1.125)
        lbox(c, o, "Eisen", P, hu - 0.13, hu + 0.012, ts + s * 0.04, ts + s * 0.055, 1.10, 1.125)
    lbox(c, o, "Metall", P, b - fw - 0.11, b - fw - 0.05, tm + 0.025, tm + 0.04, 1.40, 1.45)
    PIVOT[o] = P(a + fw, tm, 0)


def back_door():
    """Back door (west wall) after back_door_of_the_house.jpg: heavy dark frame, weathered
    plank leaf with an oval window behind four cream iron bars."""
    c, P = "EG", frame("y")
    a, b, head = 7.408, 8.377, 2.3
    fw, o = 0.09, "EG_Fenster_Tueren"
    lbox(c, o, "Holz", P, a, a + fw, -0.05, 0.08, 0, head)
    lbox(c, o, "Holz", P, b - fw, b, -0.05, 0.08, 0, head)
    lbox(c, o, "Holz", P, a, b, -0.05, 0.08, head - fw, head)
    o = "EG_Hintertuer"
    la, lb, lt = a + fw + 0.004, b - fw - 0.004, head - fw - 0.004
    uc, zc, ea, eb = (la + lb) / 2, 0.82 * lt, 0.19, 0.28
    half = lambda u: eb * math.sqrt(max(1 - ((u - uc) / ea) ** 2, 0))
    boards(c, o, "Holz", P, la, lb, const(0.01), const(lt), 0.0, 0.05, 0.135,
           holes=[(uc - ea, uc + ea, lambda u: zc - half(u), lambda u: zc + half(u), True)])
    lbox(c, o, "Milchglas", P, uc - ea - 0.02, uc + ea + 0.02, 0.024, 0.026, zc - eb - 0.02, zc + eb + 0.02)
    ring = [(uc + ea * math.cos(2 * math.pi * i / 48), zc + eb * math.sin(2 * math.pi * i / 48))
            for i in range(49)]
    ring2 = [(uc + (ea + 0.035) * math.cos(2 * math.pi * i / 48),
              zc + (eb + 0.035) * math.sin(2 * math.pi * i / 48)) for i in range(49)]
    sweep(c, o, "Holz", P, list(zip(ring, ring2)), -0.012, 0.0)
    for du in (-0.13, -0.045, 0.045, 0.13):                                  # bars
        lbox(c, o, "Gitter", P, uc + du - 0.015, uc + du + 0.015, -0.022, -0.012,
             zc - eb - 0.06, zc + eb + 0.06)
    lbox(c, o, "Eisen", P, la, lb, -0.008, 0.0, 0.97, 1.03)                  # strap
    lbox(c, o, "Metall", P, la + 0.06, la + 0.14, -0.02, 0.0, 1.02, 1.12)     # lock (south side)
    # black lever handles at the lock, pointing towards the hinge (north): outside on the lock
    # plate, inside on a backplate. Fixed rnd (plain colour), so no later part's random value shifts
    hu, zh = la + 0.10, 1.06
    lbox(c, o, "Eisen", P, hu - 0.025, hu + 0.025, 0.05, 0.06, 0.93, 1.19, 0.5)
    for f, s in ((-0.02, -1), (0.06, 1)):                                      # face, outward
        lbox(c, o, "Eisen", P, hu - 0.012, hu + 0.012, f, f + s * 0.05, zh - 0.0125, zh + 0.0125, 0.5)
        lbox(c, o, "Eisen", P, hu - 0.012, hu + 0.13, f + s * 0.035, f + s * 0.05, zh - 0.0125, zh + 0.0125, 0.5)


def stube_niche():
    """Door between corridor and Stube after shape_door_into_stuben.jpeg: a deep niche with a
    shallow segmental arch on the corridor side; the door (frame + leaf, opened into the Stube)
    sits in the remaining thin wall layer on the Stube side."""
    c, P = "EG", frame("x")
    da, db = 11.004, 11.803                  # door opening (from the plan)
    na, nb = da - 0.20, db + 0.20            # niche, wider than the door
    y0, ys, y1 = 5.849, 5.97, 6.349          # Stube face / back of niche / corridor face
    crown, rise = 2.30, 0.28
    Rn, uc = ((nb - na) ** 2 / 4 + rise ** 2) / (2 * rise), (na + nb) / 2
    arch = lambda u: crown - Rn + math.sqrt(max(Rn * Rn - (u - uc) ** 2, 0))
    us = [na + (nb - na) * i / 24 for i in range(25)]
    sweep(c, "EG_Waende", "Putz", P, [((u, arch(u)), (u, Z_EG_TOP)) for u in us], ys, y1)
    wall(c, na, nb, y0, ys, 0, Z_EG_TOP, [(da, db, 0, DOOR_H, "I")])
    panel_door(c, "x", da, db, y0, ys, 0, DOOR_H, -1, "b")


# ---------------------------------------------------------------- EG
def build_eg():
    c, z0, z1 = "EG", 0.0, Z_EG_TOP
    # exterior walls (segments = PDF vector wall fills, gaps = openings)
    wall(c, 0, W_OUT, 12.473, D_OUT, z0, z1, [
        (1.109, 2.008, 0, 2.0, "FD", 1), (3.866, 4.765, 0, 2.0, "FD", 1),
        (6.953, 7.852, 1.0, 2.0, "W", 1), (10.020, 10.919, 0, 2.0, "FD", 1),
        (12.867, 13.766, 0, 2.0, "FD", 1)], out=+1)
    wall(c, 2.358, W_OUT, 0, 0.415, z0, z1, [
        (3.831, 4.730, 1.03, 2.0, "W", 1), (6.618, 7.917, 0, 2.0, "FD", 1),
        (9.785, 13.741, 0, 2.2, "GD")], out=-1)
    wall(c, 14.575, W_OUT, 6.349, 12.473, z0, z1, [
        (6.458, 7.507, 0, 2.2, "I"), (8.007, 8.476, 1.2, 2.1, "W"),
        (10.315, 11.214, 1.0, 2.0, "W", 1)], out=+1)
    wall(c, 14.351, W_OUT, 0.415, 6.349, z0, z1, [(1.254, 4.880, 0, 2.2, "GD")], out=+1)
    wall(c, 0, 0.31, 5.145, 12.473, z0, z1, [
        (5.724, 6.324, 1.57, 2.17, "W"), (7.408, 8.377, 0, 2.3, "I"),
        (9.12, 9.69, 1.57, 2.17, "W")], out=-1)      # WC Großeltern ("Fenster wird verschoben")
    wall(c, 0.31, 2.358, 5.145, 5.475, z0, z1)              # WC south (towards the annex)
    wall(c, 2.358, 2.772, 0.415, 5.849, z0, z1)             # west wall Speis/Essen
    entrance_door(); back_door()
    # interior walls; doors: (a, b, swing, hinge) get an opened leaf, (a, b) stay open passages
    interior(c, 6.024, 6.174, 8.876, 12.473)
    interior(c, 2.657, 14.575, 8.576, 8.876,
             [(4.406, 5.335, 1, "a"), (7.333, 8.282, 1, "a"), (13.517, 14.575, 1, "b", False)])   # Büro: hinge as in the plan, leaf along the east wall (bookcase)
    # 9.78-10.72 is pink-hatched wall in the plan (closed up), not an opening – it sat behind the stair
    interior(c, 0.31, 2.358, 8.506, 8.656)              # Flur / WC Großeltern: door closed up (plan)
    interior(c, 0.31, 2.358, 6.574, 6.723, [(1.419, 2.218, -1, "a")])
    # Großeltern: the Bad is open to the bedroom from its niche front (code/bad.py) to the shaft
    interior(c, 2.358, 2.657, 6.349, 12.473, [(7.408, 8.506, -1, "a", False, "glazed"), (9.856, 12.33)])   # back Windfang
    interior(c, 2.358, 10.804, 5.849, 6.349, [(6.10, 6.96, -1, "a", False)],   # Küche door as built (photo,
             # speis_kueche_v6.svg): hinged west, opened 90 deg into the Küche beside the Besenschrank
             ops=[ofen.back_opening()])                                   # the Ofen's back door (Flur)
    stube_niche()                                                         # 10.804 .. 12.003
    interior(c, 12.003, 14.351, 5.849, 6.349)
    interior(c, 8.557, 9.056, 0.415, 5.849, [(0.54, 2.938)])
    interior(c, 5.240, 5.490, 3.13, 5.849, [(4.33, 5.249)])  # Speis / Küche: ends at the cabinet C, open
    speis()                                                 # over the aisle (sliding leaf on the Küche side)
    interior(c, 9.051, 9.351, 8.876, 9.585)                 # offener Kamin – wall ends
    interior(c, 9.051, 9.351, 12.213, 12.473)
    bad.bad_neu(c, *bad.BAD_AT)                             # Bad Großeltern with its WC / Schrank niche
    interior(c, 12.25, 12.38, 6.349, 8.576, [(6.5, 8.45, 1, "ab", False, "glazed")])  # Windfang
    ofen.ofen_im_haus()
    ofen.werkstattofen("EG", 9.351 + 0.10 + 0.21 * 2 ** 0.5, 8.876 + 0.10 + 0.21 * 2 ** 0.5, 0.0, -45)   # Bibliothek:
    # corner of the Flur wall and the wall stub, turned 45° to face the room (request 2026-11-08)
    build_stairs()
    for x0, x1 in ((4.26, 6.05), (6.05, 7.85)):             # dining table (plan: two joined tables)
        table("EG", x0 + 0.002, x1 - 0.002, 1.18, 1.91)
    for x in (4.58, 5.15, 5.73, 6.39, 6.95, 7.53):          # 14 chairs as in the plan
        chair("EG", x, 2.12, 0, -1)
        chair("EG", x, 0.97, 0, 1)
    chair("EG", 4.05, 1.545, 1, 0)
    chair("EG", 8.06, 1.545, -1, 0)
    kueche.kueche_neu("EG", *kueche.KUECHE_AT)               # sink run, Herd, peninsula, Besenschrank
    box(c, "EG_Waende", "Putz", 2.04, 2.358, 12.12, 12.471, z0, z1)   # shaft in the Bad Großeltern (plan 2026-10)


# ---------------------------------------------------------------- sanitary (positions from the plans)
def xy_prism(coll, obj, mat, pts, z0, z1, rnd=None):
    """Extrude a horizontal (x, y) outline from z0 to z1."""
    n = len(pts)
    v = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    f = [list(range(n))[::-1], list(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    add(coll, obj, mat, v, f, rnd)


def at_wall(wx, wy, fx, fy):
    """Map (u along the wall, v into the room) to world, from wall point (wx, wy) facing (fx, fy)."""
    return lambda u, v: (wx + fx * v - fy * u, wy + fy * v + fx * u)


def rounded(M, w, d, v0=0.0, n=12):
    """Outline with a straight back at v0 and a semi-elliptic front (width w, depth d)."""
    r = min(d, w / 2)
    pts = [M(-w / 2, v0), M(w / 2, v0)]
    pts += [M(w / 2 * math.cos(math.pi * i / n), v0 + d - r + r * math.sin(math.pi * i / n)) for i in range(n + 1)]
    return pts


def toilet(coll, wx, wy, fx, fy, z=0.0):
    """Floor-standing toilet with a close-coupled cistern and a chrome side lever, lid down, after
    bad_mallnitz.jpeg (input/2026-11-08 input/); stands on the WC tiles (all toilets are in the WCs)."""
    T = WC_TILE_T
    o, M = coll + "_Sanitaer", at_wall(wx + fx * T, wy + fy * T, fx, fy)
    rect = lambda u0, u1, v0, v1: [M(u0, v0), M(u1, v0), M(u1, v1), M(u0, v1)]
    xy_prism(coll, o, "Keramik", rounded(M, 0.26, 0.42, 0.13), z + 0.014, z + 0.05)         # foot
    xy_prism(coll, o, "Keramik", rounded(M, 0.20, 0.36, 0.16), z + 0.05, z + 0.32)          # pedestal
    xy_prism(coll, o, "Keramik", rounded(M, 0.36, 0.52, 0.16), z + 0.32, z + 0.40)          # bowl
    xy_prism(coll, o, "Keramik", rect(-0.12, 0.12, 0.04, 0.19), z + 0.30, z + 0.42)        # back
    xy_prism(coll, o, "Keramik", rounded(M, 0.37, 0.49, 0.20), z + 0.40, z + 0.42)          # seat
    xy_prism(coll, o, "Keramik", rounded(M, 0.35, 0.47, 0.21), z + 0.42, z + 0.445)         # lid
    xy_prism(coll, o, "Keramik", rect(-0.20, 0.20, 0.0, 0.19), z + 0.42, z + 0.78)         # cistern
    xy_prism(coll, o, "Keramik", rect(-0.215, 0.215, 0.0, 0.21), z + 0.78, z + 0.81)       # its lid
    xy_prism(coll, o, "Metall", rect(0.20, 0.215, 0.15, 0.18), z + 0.72, z + 0.75)         # lever
    xy_prism(coll, o, "Metall", rect(0.215, 0.27, 0.16, 0.17), z + 0.73, z + 0.745)


def basin(coll, wx, wy, fx, fy, w=0.60, d=0.46, z=0.0, mirror=True):
    """Washbasin (rounded front) with tap and a mirror above."""
    o, M = coll + "_Sanitaer", at_wall(wx, wy, fx, fy)
    xy_prism(coll, o, "Keramik", rounded(M, w * 0.7, d * 0.8), z + 0.66, z + 0.80)
    xy_prism(coll, o, "Keramik", rounded(M, w, d), z + 0.80, z + 0.86)
    xy_prism(coll, o, "Metall", [M(-0.02, 0.03), M(0.02, 0.03), M(0.02, 0.14), M(-0.02, 0.14)], z + 0.86, z + 0.97)
    if mirror:
        (xa, ya), (xb, yb) = M(-w / 2, 0.0), M(w / 2, 0.008)
        box(coll, o, "Spiegel", xa, xb, ya, yb, z + 1.10, z + 1.75)


def wc_basin(coll, wx, wy, fx, fy, w=0.40, d=0.28, z=0.0):
    """Hand basin of the WCs after bad_mallnitz.jpeg (input/2026-11-08 input/): open ceramic bowl on two
    chrome console legs with a towel rail, pillar mixer, chrome trap; above the tiles a mirror
    in a stepped black frame."""
    T = WC_TILE_T
    o, M = coll + "_Sanitaer", at_wall(wx + fx * T, wy + fy * T, fx, fy)
    rect = lambda u0, u1, v0, v1: [M(u0, v0), M(u1, v0), M(u1, v1), M(u0, v1)]
    P = lambda u, v, h: (*M(u, v), z + h)
    K = lambda *a: xy_prism(coll, o, "Keramik", rect(*a[:4]), z + a[4], z + a[5])
    K(-w / 2 + 0.02, w / 2 - 0.02, 0.0, d - 0.02, 0.70, 0.76)                    # bowl bottom
    K(-w / 2, w / 2, 0.0, 0.08, 0.70, 0.85)                                       # tap deck
    K(-w / 2, w / 2, d - 0.03, d, 0.70, 0.85)                                     # front rim
    for s in (-1, 1):
        K(*sorted((s * w / 2, s * (w / 2 - 0.03))), 0.08, d - 0.03, 0.70, 0.85)  # side rims
    turned(coll, o, "Metall", P(0, d / 2 + 0.03, 0.76), P(0, d / 2 + 0.03, 0.763), [(0.025, 0), (0.025, 1)])
    turned(coll, o, "Metall", P(0, 0.045, 0.85), P(0, 0.045, 0.95), [(0.018, 0), (0.016, 1)])   # mixer
    turned(coll, o, "Metall", P(0, 0.045, 0.94), P(0, 0.13, 0.92), [(0.009, 0), (0.008, 1)])    # spout
    turned(coll, o, "Metall", P(0, 0.045, 0.95), P(0, 0.02, 1.00), [(0.006, 0), (0.005, 1)])    # lever
    turned(coll, o, "Metall", P(0, d / 2 + 0.03, 0.70), P(0, d / 2 + 0.03, 0.46), [(0.02, 0), (0.02, 1)])
    turned(coll, o, "Metall", P(0, d / 2 + 0.03, 0.47), P(0, 0.0, 0.47), [(0.016, 0), (0.016, 1)])
    lu, lv = w / 2 - 0.04, d - 0.04
    for s in (-1, 1):                                                             # console legs
        turned(coll, o, "Metall", P(s * lu, lv, 0.014), P(s * lu, lv, 0.70), [(0.014, 0), (0.014, 1)])
        turned(coll, o, "Metall", P(s * lu, lv, 0.014), P(s * lu, lv, 0.02), [(0.025, 0), (0.025, 1)])
        turned(coll, o, "Metall", P(s * lu, lv, 0.25), P(s * lu, 0.0, 0.25), [(0.009, 0), (0.009, 1)])
    turned(coll, o, "Metall", P(-lu, lv + 0.02, 0.62), P(lu, lv + 0.02, 0.62), [(0.008, 0), (0.008, 1)])  # rail
    for s in (-1, 1):
        turned(coll, o, "Metall", P(s * lu, lv, 0.62), P(s * lu, lv + 0.02, 0.62), [(0.008, 0), (0.008, 1)])
    M = at_wall(wx, wy, fx, fy)                                                   # mirror on the plaster
    z0, z1, mw, fw = z + 1.22, z + 2.05, 0.30, 0.07
    F = lambda u0, u1, v1, za, zb: box(coll, o, "Eisen", *[c for p in zip(M(u0, 0.0), M(u1, v1)) for c in sorted(p)], za, zb)
    F(-mw, mw, 0.035, z0, z0 + fw); F(-mw, mw, 0.035, z1 - fw, z1)
    F(-mw, -mw + fw, 0.035, z0, z1); F(mw - fw, mw, 0.035, z0, z1)
    i = mw - fw                                                                   # raised inner bead
    F(-i, i, 0.05, z0 + fw, z0 + fw + 0.02); F(-i, i, 0.05, z1 - fw - 0.02, z1 - fw)
    F(-i, -i + 0.02, 0.05, z0 + fw, z1 - fw); F(i - 0.02, i, 0.05, z0 + fw, z1 - fw)
    (xa, ya), (xb, yb) = M(-i, 0.0), M(i, 0.012)
    box(coll, o, "Spiegel", xa, xb, ya, yb, z0 + fw, z1 - fw)


def shower(coll, x0, x1, y0, y1, glass, head, z=0.0):
    """Shower tray, glass panels [(xa, ya, xb, yb) along an open edge], head on wall `head`
    = (wx, wy, fx, fy)."""
    o = coll + "_Sanitaer"
    box(coll, o, "Keramik", x0, x1, y0, y1, z + 0.015, z + 0.045)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    box(coll, o, "Metall", cx - 0.05, cx + 0.05, cy - 0.05, cy + 0.05, z + 0.045, z + 0.047)
    for xa, ya, xb, yb in glass:
        box(coll, o, "Glas", xa - 0.004, xb + 0.004, ya - 0.004, yb + 0.004, z + 0.045, z + 2.0)
        box(coll, o, "Metall", xa - 0.012, xb + 0.012, ya - 0.012, yb + 0.012, z + 2.0, z + 2.02)
    M = at_wall(*head)
    (xa, ya), (xb, yb) = M(-0.012, 0.0), M(0.012, 0.03)
    box(coll, o, "Metall", xa, xb, ya, yb, z + 1.0, z + 2.05)                      # riser
    (xa, ya), (xb, yb) = M(-0.012, 0.03), M(0.012, 0.30)
    box(coll, o, "Metall", xa, xb, ya, yb, z + 2.03, z + 2.05)                     # arm
    k, (hx, hy) = 16, M(0, 0.30)
    xy_prism(coll, o, "Metall", [(hx + 0.12 * math.cos(2 * math.pi * i / k), hy + 0.12 * math.sin(2 * math.pi * i / k))
                                 for i in range(k)], z + 2.00, z + 2.02)


def flur_sink(coll, wx, wy, z):
    """Deep ceramic sink on a dark stone panel (waschbecken-briol.jpeg) on a wall facing north at
    (wx, wy), but one wall-mounted single-lever mixer instead of the photo's two taps."""
    o, M = coll + "_Sanitaer", at_wall(wx, wy, 0, 1)
    rect = lambda u0, u1, v0, v1: [M(u0, v0), M(u1, v0), M(u1, v1), M(u0, v1)]
    xy_prism(coll, o, "Schiefer", rect(-0.40, 0.40, 0.0, 0.02), z + 0.50, z + 1.62)        # stone panel,
    xy_prism(coll, o, "Schiefer", rect(-0.33, 0.33, 0.0, 0.02), z + 0.012, z + 0.50)       # narrower below
    for u0, u1, v0, v1, z0 in ((-0.30, 0.30, 0.02, 0.47, 0.58), (-0.30, 0.30, 0.44, 0.47, 0.62),   # bottom, front,
                               (-0.30, 0.30, 0.02, 0.05, 0.62), (-0.30, -0.27, 0.05, 0.44, 0.62),  # back, sides
                               (0.27, 0.30, 0.05, 0.44, 0.62)):
        xy_prism(coll, o, "Keramik", rect(u0, u1, v0, v1), z + z0, z + (0.62 if z0 < 0.6 else 0.86))
    P = lambda u, v, h: (*M(u, v), z + h)
    turned(coll, o, "Metall", P(0, 0.245, 0.62), P(0, 0.245, 0.623), [(0.03, 0), (0.03, 1)])   # drain
    turned(coll, o, "Metall", P(0, 0.245, 0.30), P(0, 0.245, 0.58), [(0.02, 0), (0.02, 1)])
    turned(coll, o, "Metall", P(0, 0.02, 0.30), P(0, 0.265, 0.30), [(0.02, 0), (0.02, 1)])
    turned(coll, o, "Metall", P(0, 0.02, 1.10), P(0, 0.03, 1.10), [(0.035, 0), (0.035, 1)])    # rosette
    turned(coll, o, "Metall", P(0, 0.03, 1.10), P(0, 0.10, 1.10), [(0.025, 0), (0.025, 1)])    # mixer body
    turned(coll, o, "Metall", P(0, 0.09, 1.09), P(0, 0.22, 1.06), [(0.012, 0), (0.010, 1)])    # spout
    turned(coll, o, "Metall", P(0, 0.215, 1.065), P(0, 0.215, 1.035), [(0.011, 0), (0.011, 1)])
    turned(coll, o, "Metall", P(0, 0.08, 1.12), P(0, 0.05, 1.20), [(0.007, 0), (0.006, 1)])    # lever


WC_TILE_T = 0.010            # tile face in front of the plaster (WC fixtures stand on it)
WCS = [  # (collection, floor z, interior rectangle, door span left free on the north wall)
    ("EG", 0.0, (0.31, 2.358, 5.475, 6.574), (1.349, 2.288)),     # WC by the back hall (architraves)
    ("OG", Z_OG, (0.31, 1.57, 5.46, 6.44), (0.48, 1.42)),         # WC 2,26
    ("OG", Z_OG, (8.72, 9.92, 3.98, 6.06), (8.69, 9.72))]         # WC 2,30


def wainscot(coll, z, x0, x1, y0, y1, door):
    """Green subway tiles (7.5 x 15 cm, running bond, 14 rows) with a stepped cap row on all four
    walls of a WC, after input/2026-11-08 input/bad_mallnitz.jpeg.
    Grout backing 2 mm off the plaster; the y walls stop short of the x walls' tiles in the
    corners; the north wall leaves `door` free. Own random stream, so later parts don't shift."""
    o, rng, TL, TH, J = coll + "_Fliesen", random.Random(11), 0.15, 0.075, 0.003
    zb, zt = z + 0.015, z + 0.015 + 14 * TH                       # above the oak floor
    T = WC_TILE_T
    for side in "snwe":
        along_x = side in "sn"
        face, n = {"s": (y0, 1), "n": (y1, -1), "w": (x0, 1), "e": (x1, -1)}[side]
        ua, ub = (x0, x1) if along_x else (y0, y1)
        spans = [(ua, door[0]), (door[1], ub)] if side == "n" else [(ua, ub)]

        def B(m, a, b, t0, t1, za, zc, r, cut=0.0):              # u in [a, b], t in front of the face
            if not along_x:                                       # y walls: clear of the x walls
                a, b = max(a, y0 + cut), min(b, y1 - cut)
            if b - a < 0.005:
                return
            ta, tb = face + n * t0, face + n * t1
            if along_x:
                box(coll, o, m, a, b, ta, tb, za, zc, r)
            else:
                box(coll, o, m, ta, tb, a, b, za, zc, r)

        for sa, sb in spans:
            sa, sb = max(sa, ua), min(sb, ub)
            B("Fugengrau", sa, sb, 0.002, 0.007, zb, zt, 0.5, T + 0.001)
            for k in range(14):
                u = ua - (TL / 2 if k % 2 else 0)
                while u < sb:
                    a, b = max(u, sa), min(u + TL, sb)
                    if b > a:
                        B("Fliese", a + J / 2, b - J / 2, 0.004, T, zb + k * TH + J / 2, zb + (k + 1) * TH - J / 2,
                          rng.random(), T + 0.001)
                    u += TL
            u = ua
            while u < sb:                                         # cap row: stepped bullnose
                a, b, r = max(u, sa) + J / 2, min(u + TL, sb) - J / 2, rng.random()
                if b > a:
                    B("Fliese", a, b, 0.004, 0.014, zt + J / 2, zt + 0.035, r, 0.015)
                    B("Fliese", a, b, 0.004, 0.011, zt + 0.035, zt + 0.05, r, 0.015)
                u += TL


def build_sanitary():
    """Bathrooms and toilets after the fixtures drawn in grundriss_eg/og.png (the Bad Großeltern
    with its WC: code/bad.py, built in build_eg())."""
    zo = Z_OG + 0.0
    for c, z, rect, door in WCS:
        wainscot(c, z, *rect, door)
    # EG WC by the back hall
    toilet("EG", 1.325, 5.475, 0, 1)
    # OG Bad NW: basin on the north wall, shower in the south alcove
    basin("OG", 0.885, 8.57, 0, -1, w=0.62, d=0.48, z=zo)
    shower("OG", 1.67, 2.57, 5.46, 6.44, [(2.10, 6.44, 2.57, 6.44)], (2.12, 5.46, 0, 1), z=zo)
    # OG WC 2,26: toilet on the west wall below the window
    toilet("OG", 0.31, 6.0, 1, 0, z=zo)
    # OG Bad S: corner shower NW, basin on the south wall
    shower("OG", 5.59, 6.57, 1.64, 2.62, [(6.57, 1.64, 6.57, 2.62), (5.59, 1.64, 6.05, 1.64)],
           (6.08, 2.62, 0, -1), z=zo)
    basin("OG", 6.11, 0.40, 0, 1, w=0.62, d=0.48, z=zo)
    # OG WC 2,30: toilet on the south wall, hand basin on the east wall
    toilet("OG", 9.26, 3.98, 0, 1, z=zo)
    wc_basin("OG", 9.92, 5.2, -1, 0, z=zo)
    # OG Flur: sink right of the Waschküche door (plan: basin symbol), after waschbecken-briol.jpeg
    flur_sink("OG", 6.45, 6.35, zo)


# ---------------------------------------------------------------- furniture
def post(coll, obj, mat, p0, p1, w, rnd=None):
    """Square post of width w from bottom centre p0 to top centre p1 (may lean)."""
    v = [(p[0] + sx * w / 2, p[1] + sy * w / 2, p[2]) for p in (p0, p1)
         for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    add(coll, obj, mat, v, f, rnd)


def turned(coll, obj, mat, p0, p1, prof, k=16, rnd=None):
    """Round solid along the axis p0 -> p1: prof = [(radius, t), ...] with t from 0 (p0) to 1 (p1)."""
    ax = [b - a for a, b in zip(p0, p1)]
    n = math.sqrt(sum(c * c for c in ax))
    ax = [c / n for c in ax]
    e1 = (1, 0, 0) if abs(ax[0]) < 0.9 else (0, 1, 0)
    a = [ax[1] * e1[2] - ax[2] * e1[1], ax[2] * e1[0] - ax[0] * e1[2], ax[0] * e1[1] - ax[1] * e1[0]]
    m = math.sqrt(sum(c * c for c in a))
    a = [c / m for c in a]
    b = [ax[1] * a[2] - ax[2] * a[1], ax[2] * a[0] - ax[0] * a[2], ax[0] * a[1] - ax[1] * a[0]]
    v = [tuple(p0[j] + t * (p1[j] - p0[j]) + r * (math.cos(2 * math.pi * i / k) * a[j] + math.sin(2 * math.pi * i / k) * b[j])
               for j in range(3)) for r, t in prof for i in range(k)]
    nr = len(prof)
    f = [list(range(k))[::-1], list(range((nr - 1) * k, nr * k))]
    f += [(j * k + i, j * k + (i + 1) % k, (j + 1) * k + (i + 1) % k, (j + 1) * k + i) for j in range(nr - 1) for i in range(k)]
    add(coll, obj, mat, v, f, rnd)


def table(coll, x0, x1, y0, y1, h=0.76):
    """Inn table after tisch-briol.png: a top of three spruce boards on an apron set back from its
    edge, legs splayed out along the length (a little across), standing on a flat foot frame that
    rests on corner blocks just above the floor."""
    o, tt, lw = coll + "_Tisch", 0.045, 0.065                                   # top thickness, leg width
    bw = (y1 - y0) / 3
    for k in range(3):                                                         # top boards
        box(coll, o, "FichteX", x0, x1, y0 + k * bw, y0 + (k + 1) * bw, h - tt, h)
    tix, tiy, fix, fiy = 0.17, 0.10, 0.06, 0.07                                # leg centre inset top / foot
    zr = (0.065, 0.09)                                                         # foot frame
    feet = []
    for sx, sy in ((0, 0), (1, 0), (1, 1), (0, 1)):
        tx, ty = (x1 - tix, x0 + tix)[sx == 0], (y1 - tiy, y0 + tiy)[sy == 0]
        fx, fy = (x1 - fix, x0 + fix)[sx == 0], (y1 - fiy, y0 + fiy)[sy == 0]
        post(coll, o, "FichteZ", (fx, fy, zr[1]), (tx, ty, h - tt), lw)
        box(coll, o, "FichteZ", fx - 0.04, fx + 0.04, fy - 0.04, fy + 0.04, 0.012, zr[0])   # corner block
        feet.append((fx, fy))
    ax0, ax1, ay0, ay1 = x0 + tix - lw / 2, x1 - tix + lw / 2, y0 + tiy - lw / 2, y1 - tiy + lw / 2
    za, e = (h - tt - 0.11, h - tt), 0.005                                     # apron 5 mm inside the legs' faces
    for ya, yb in ((ay0 + e, ay0 + e + 0.025), (ay1 - e - 0.025, ay1 - e)):
        box(coll, o, "FichteX", ax0 + e, ax1 - e, ya, yb, *za)
    for xa, xb in ((ax0 + e, ax0 + e + 0.025), (ax1 - e - 0.025, ax1 - e)):
        box(coll, o, "FichteY", xa, xb, ay0 + e + 0.025, ay1 - e - 0.025, *za)
    r, (fx0, fy0), (fx1, fy1) = random.random(), feet[0], feet[2]              # frame: one rnd (it meets)
    for y in (fy0, fy1):
        box(coll, o, "FichteX", fx0 - 0.05, fx1 + 0.05, y - 0.045, y + 0.045, *zr, r)
    for x in (fx0, fx1):
        box(coll, o, "FichteY", x - 0.045, x + 0.045, fy0 + 0.045, fy1 - 0.045, *zr, r)


def chair(coll, cx, cy, fx, fy):
    """Spruce board chair after stuhl.png, centred at (cx, cy), facing the table in direction
    (fx, fy): plank seat on two battens, four splayed tapering stick legs (no stretchers), one tall
    backrest board leaning back with a pointed heart cut out, its tenon wedged under the seat."""
    o, W = coll + "_Stuehle", 0.42
    Q = lambda u, v, z: (cx + fx * (W / 2 - v) - fy * u, cy + fy * (W / 2 - v) + fx * u, z)   # u across, v from the front
    grain = (lambda m: {"FichteX": "FichteY", "FichteY": "FichteX"}.get(m, m)) if fx else (lambda m: m)

    def part(m, u0, u1, v0, v1, z0, z1):
        (xa, ya, _), (xb, yb, _) = Q(u0, v0, 0), Q(u1, v1, 0)
        box(coll, o, grain(m), xa, xb, ya, yb, z0, z1, r)

    r, h = random.random(), W / 2                                              # one draw per chair
    part("FichteX", -h, h, 0, 0.40, 0.41, 0.46)                                # seat plank
    for s in (-1, 1):
        part("FichteY", s * 0.10, s * 0.16, 0.03, 0.37, 0.38, 0.41)            # battens
        for vt, vb in ((0.07, 0.015), (0.33, 0.40)):                           # legs: splayed out, tapering
            ut, ub = s * 0.13, s * 0.19
            v = [Q(ub + a * 0.0175, vb + b * 0.0175, 0) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            v += [Q(ut + a * 0.0225, vt + b * 0.0225, 0.40) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            add(coll, o, "FichteZ", v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], r)
    part("FichteZ", -0.06, 0.06, 0.335, 0.375, 0.33, 0.41)                     # backrest tenon + wedge
    # backrest board: (a across, b up the board) in its plane, leaning back 12°, t through it
    sn, cs = math.sin(math.radians(12)), math.cos(math.radians(12))
    PB = lambda a, t, b: Q(a, 0.335 + t + b * sn, 0.46 + b * cs)
    b0, top, w0, w1 = -0.05, 0.50, 0.15, 0.17                                 # into the seat; height, half widths
    hy, ha, hc, hw = top - 0.06, top - 0.07, top - 0.19, 0.055                 # heart: top edge, corners, point
    edge = lambda b: w0 + (w1 - w0) * b / top
    for pts in ([(-edge(b0), b0), (-hw, b0), (-hw, ha), (-hw * 0.6, hy), (-hw * 0.6, top), (-edge(top), top)],
                [(hw, b0), (edge(b0), b0), (edge(top), top), (hw * 0.6, top), (hw * 0.6, hy), (hw, ha)],
                [(-hw * 0.6, hy), (hw * 0.6, hy), (hw * 0.6, top), (-hw * 0.6, top)],
                [(-hw, b0), (hw, b0), (hw, ha), (0, hc), (-hw, ha)]):
        prism(coll, o, "FichteZ", PB, pts, 0, 0.035, r)


def speis():
    """Speis after the agreed drawing input/2026-11-09 input/speis_kueche_v6.svg, from the Flur wall
    south: shelf A (60, open), the aisle (91.9, west end free), shelf B (60, open to the aisle) and,
    back to back with it, cabinet C (60, doors to the Essen) in place of the former Speis/Essen
    wall; all to the ceiling, spruce like the kitchen. The Speis door: a sliding leaf on the Küche
    side of the wall, slid open to the south (left as seen from the Küche), under its rail. Own
    random stream, like the sub-models."""
    c, o, rng = "EG", "EG_Speis", random.Random(9)
    x0, x1, top = 2.774, 5.238, Z_EG_TOP - 0.003

    def shelves(ya, yb):                     # uprights at the ends and about every 0.9 m, seven boards
        n = round((x1 - x0) / 0.9)
        for k in range(n + 1):
            ua = x0 + (x1 - x0 - 0.02) * k / n
            box(c, o, "FichteZ", ua, ua + 0.02, ya, yb, 0.012, top, rng.random())
        for zb in (0.10, 0.48, 0.86, 1.24, 1.62, 2.00, 2.38):
            box(c, o, "FichteX", x0 + 0.002, x1 - 0.002, ya + 0.005, yb - 0.005, zb - 0.025, zb, rng.random())

    shelves(5.249, 5.847)                                                     # A
    shelves(3.732, 4.33)                                                      # B
    yd, yc = 3.13, 3.15                                                       # C: doors / carcass front
    box(c, o, "FichteZ", x0, x1, yc, 3.728, 0.10, top, rng.random())
    box(c, o, "Fuge", x0, x1, yc + 0.06, 3.728, 0.005, 0.10, rng.random())
    n = 4
    for k in range(n):
        a, b = x0 + (x1 - x0) * k / n, x0 + (x1 - x0) * (k + 1) / n
        for za, zb in ((0.105, 1.995), (2.005, top - 0.003)):               # tall door, top door
            box(c, o, "FichteZ", a + 0.003, b - 0.003, yd, yc, za, zb, rng.random())
        hx = b - 0.06 if k % 2 == 0 else a + 0.045
        box(c, o, "Metall", hx, hx + 0.015, yd - 0.025, yd, 0.95, 1.10, rng.random())
    # sliding leaf on the Küche face (x 5.49), 1.00 wide, open over the wall south of the opening
    ys, tc, LT, zl, LH = 3.28, 5.52, 0.04, 0.005, DOOR_H + 0.025
    rl = 0.8 + 0.2 * rng.random()

    def part(w0, w1, d0, d1, za, zb, r=rl, m="Innentuer"):
        box(c, "EG_Innentueren", m, tc + d0, tc + d1, ys + w0, ys + w1, zl + za, zl + zb, r)

    six_panel_leaf(part, 1.00, LH)
    LEAVES.append((c, [(tc - LT / 2, ys, zl), (tc + LT / 2, ys + 1.00, zl + LH)]))
    box(c, "EG_Innentueren", "Metall", 5.495, 5.56, 3.26, 5.29, zl + LH + 0.005, zl + LH + 0.045, rng.random())   # rail


# ---------------------------------------------------------------- stairs
ST_X0, ST_Y0, ST_Y1, ST_RUN, ST_RISE, ST_N = 11.19, 7.56, 8.45, 0.255, 0.18, 15


def stair_line(x):
    """Nosing line of the stair (rises westwards from x = ST_X0 to the OG floor)."""
    return ST_RISE + (ST_X0 - x) * ST_RISE / ST_RUN


def baluster(coll, obj, x, y, z0, z1):
    """Turned baluster (8-sided lathe) after stairs_indoor.png: square-ish ends, rings, bulbs."""
    prof = [(0, 0.021), (0.10, 0.021), (0.11, 0.013), (0.14, 0.018), (0.17, 0.012), (0.34, 0.017),
            (0.52, 0.011), (0.58, 0.016), (0.62, 0.011), (0.80, 0.014), (0.86, 0.018),
            (0.89, 0.021), (1, 0.021)]
    k = 8
    rings = [[(x + r * math.cos(2 * math.pi * (j + 0.5) / k), y + r * math.sin(2 * math.pi * (j + 0.5) / k),
               z0 + (z1 - z0) * s) for j in range(k)] for s, r in prof]
    v = [p for r in rings for p in r]
    f = [(i * k + j, i * k + (j + 1) % k, (i + 1) * k + (j + 1) % k, (i + 1) * k + j)
         for i in range(len(rings) - 1) for j in range(k)]
    f += [list(range(k))[::-1], list(range((len(rings) - 1) * k, len(rings) * k))]
    add(coll, obj, "Kiefer", v, f)


def build_stairs():
    """Straight stair (15 x 18.0/25.5, from the plan) after stairs_indoor.png: warm treads and
    risers, closed stringer on the open (south) side with turned balusters, sloping handrail,
    plank newel post with a rounded top; the same railing runs round the stairwell in the OG.
    The space under the stair stays open (stepped underside, second stringer along the wall)."""
    c, o, g, P = "EG", "EG_Treppe", "EG_Gelaender", frame("x")
    ys0, ys1 = ST_Y0, ST_Y0 + 0.05                        # stringer on the open side
    for i in range(1, ST_N):
        xe = ST_X0 - (i - 1) * ST_RUN                     # riser position of step i
        box(c, o, "Stufe", xe - ST_RUN, xe + 0.03, ys1, ST_Y1, i * ST_RISE - 0.04, i * ST_RISE)
        box(c, o, "Stufe", xe - 0.02, xe, ys1, ST_Y1, (i - 1) * ST_RISE, i * ST_RISE - 0.04)
    xt = ST_X0 - (ST_N - 1) * ST_RUN                      # top: OG floor edge
    xk = ST_X0 - (0.32 - ST_RISE) * ST_RUN / ST_RISE      # stringer bottom meets the floor
    bot = lambda x: max(stair_line(x) - 0.32, 0.0)
    for ya, yb in ((ys0, ys1), (ST_Y1, 8.57)):            # open side / wall side (up to the wall)
        sweep(c, o, "Kiefer", P, [((x, bot(x)), (x, stair_line(x) + 0.10)) for x in (xt, xk, ST_X0 + 0.04)],
              ya, yb)
    # balusters, handrail, newel
    yb, hr = (ys0 + ys1) / 2, 0.90                        # handrail height above the nosing line
    n = int((ST_X0 - 0.25 - xt) / 0.13)
    for k in range(n + 1):
        x = ST_X0 - 0.25 - (ST_X0 - 0.25 - xt) * k / n
        baluster(c, g, x, yb, stair_line(x) + 0.10, stair_line(x) + hr - 0.04)
    column(c, g, "Kiefer", P, xt, ST_X0 + 0.02, lambda x: stair_line(x) + hr - 0.04,
           lambda x: stair_line(x) + hr + 0.02, yb - 0.03, yb + 0.03)
    np_top = stair_line(ST_X0) + hr + 0.12
    newel = [(ST_X0 - 0.04, 0.0), (ST_X0 + 0.16, 0.0), (ST_X0 + 0.16, np_top - 0.25)]
    newel += [(ST_X0 + 0.06 + 0.10 * math.cos(math.pi / 2 * i / 8), np_top - 0.25 + 0.25 * math.sin(math.pi / 2 * i / 8))
              for i in range(1, 9)]
    newel += [(ST_X0 - 0.04, np_top - 0.05)]
    prism(c, g, "Kiefer", P, newel, yb - 0.03, yb + 0.03)
    # OG: railing on the slab edge along the whole south edge of the stairwell (next to the
    # rising stair handrail, 6 cm apart) and along the east edge
    hx0, hx1, hy0, hy1 = STAIR_HOLE
    zf, o = Z_OG + 0.01, "OG_Gelaender"
    xg = hx0 + 0.04
    # edge boards stand 6 mm proud into the opening so the slab edge face is hidden (no z-fight)
    box("OG", o, "Kiefer", hx0, hx1 + 0.045, hy0 - 0.045, hy0 + 0.006, Z_EG_TOP - 0.02, zf + 0.10)
    box("OG", o, "Kiefer", hx1 - 0.006, hx1 + 0.045, hy0 + 0.006, hy1, Z_EG_TOP - 0.02, zf + 0.10)
    for x0_, y0_, x1_, y1_ in ((xg, hy0 - 0.022, hx1 + 0.022, hy0 - 0.022),
                               (hx1 + 0.022, hy0 + 0.1, hx1 + 0.022, hy1)):
        m = int(math.dist((x0_, y0_), (x1_, y1_)) / 0.13)
        for k in range(m + 1):
            baluster("OG", o, x0_ + (x1_ - x0_) * k / m, y0_ + (y1_ - y0_) * k / m, zf + 0.10, zf + hr - 0.04)
    box("OG", o, "Kiefer", xg - 0.03, hx1 + 0.052, hy0 - 0.052, hy0 + 0.008, zf + hr - 0.04, zf + hr + 0.02)
    box("OG", o, "Kiefer", hx1 - 0.008, hx1 + 0.052, hy0, hy1, zf + hr - 0.04, zf + hr + 0.02)


# ---------------------------------------------------------------- OG
def build_og():
    c, z0, z1 = "OG", Z_OG, Z_OG_TOP
    fd = lambda a, b: (a, b, z0, 4.60, "FD", 1)
    win = lambda a, b, sh=1: (a, b, 3.62, 4.60, "W", sh)
    wall(c, 0, W_OUT, 12.485, D_OUT, z0, z1,
         [fd(3.88, 4.78), fd(6.97, 7.87), fd(10.03, 10.95), fd(12.91, 13.80)], out=+1)
    wall(c, 0, 0.31, 5.12, 12.485, z0, z1, [
        (11.26, 12.23, z0 + 0.75, z1, "W"), (8.96, 9.95, z0 + 0.75, z1, "W"),   # wall below, up to
        (6.77, 7.76, z0 + 0.75, z1, "W"), (5.72, 6.32, 4.18, 4.78, "W")], out=-1)   # the ceiling (request)
    wall(c, 0.31, 2.71, 5.12, 5.46, z0, z1)
    wall(c, 2.37, 2.71, 0, 5.12, z0, z1, [(2.03, 2.92, 3.70, 4.70, "W", 1)], out=-1)
    wall(c, 2.71, W_OUT, 0, 0.40, z0, z1,
         [win(3.85, 4.70), win(6.84, 7.72), fd(9.84, 10.70), win(12.84, 13.70)], out=-1)
    wall(c, 14.575, W_OUT, 6.40, 12.485, z0, z1, [
        fd(9.86, 10.78), (8.17, 8.47, 3.87, 4.30, "W"), (6.50, 7.50, z0, 4.60, "FD", 1)], out=+1)   # balcony doors
    wall(c, 14.35, W_OUT, 0.40, 6.40, z0, z1, [fd(1.74, 2.67), fd(4.15, 5.04)], out=+1)        # (on request)
    # eave band between OG wall top and roof (north / south)
    box(c, "OG_Waende", "Putz", 0, W_OUT, 12.485, D_OUT, z1, roof_under(D_OUT))
    box(c, "OG_Waende", "Putz", 2.37, W_OUT, 0, 0.40, z1, roof_under(0))
    # interior
    H = DOOR_H
    interior(c, 0.31, 14.575, 8.57, 8.86,
             [(3.17, 4.15, 1, "b"), (7.28, 8.17, 1, "a", False), (12.30, 13.18, 1, "a", False)], z0, z1, H)
    interior(c, 6.05, 6.21, 8.86, 12.485, (), z0, z1)
    interior(c, 9.08, 9.25, 8.86, 12.485, (), z0, z1)
    interior(c, 2.57, 2.71, 5.46, 8.57, [(7.66, 8.47, -1, "a")], z0, z1, H)
    interior(c, 2.71, 14.35, 6.06, 6.35,
             [(4.02, 4.87, -1, "a", False), (7.15, 8.17, -1, "a"), (8.76, 9.65, -1, "b", False),
              (10.66, 11.51, -1, "a", False)], z0, z1, H)
    interior(c, 0.31, 1.57, 6.44, 6.54, [(0.55, 1.35, -1, "b", False)], z0, z1, H)   # WC 2,26
    interior(c, 1.57, 1.67, 5.46, 6.44, (), z0, z1)
    interior(c, 5.44, 5.59, 0.40, 6.06, (), z0, z1)
    interior(c, 5.59, 8.59, 2.62, 2.79, (), z0, z1)                  # HWR / Bad (new)
    interior(c, 8.59, 8.72, 0.40, 6.06, [(1.65, 2.58, -1, "a")], z0, z1, H)    # Bad door opens inwards (plan)
    interior(c, 9.92, 10.07, 3.84, 6.06, (), z0, z1)                 # WC 2,30: 1.20 wide (plan)
    interior(c, 8.72, 9.92, 3.84, 3.98, (), z0, z1)
    box(c, "OG_Waende", "Putz", 11.48, 11.63, 0.98, 3.98, z0, z0 + 1.20)   # Schlafen SE: wall behind the bed head
    ofen.werkstattofen(c, 8.72 + 0.10 + 0.21 * 2 ** 0.5, 3.84 - 0.10 - 0.21 * 2 ** 0.5, z0, -135)   # corner Bad / WC


# ---------------------------------------------------------------- west cladding
def build_cladding():
    """The west side takes the weather, so the whole west face (EG, OG, gable and the part
    above the annex) is clad with vertical larch boards, after
    outside_wall_structure_back_of_the_house.png; the east gable is boarded too (elevations
    2026-10-19). Openings get board trims; the small windows get vertical iron bars; the
    boards run on over the gable windows as spaced slats."""
    c, M, bw, T = "Dach", "Laerche", 0.17, 0.025
    top = lambda y: roof_under(y) - SOFFIT
    # (object, frame, face coordinate, outward direction, u range, bottom)
    faces = [
        ("Verschalung_West", "y", 0.0, -1, 5.145, D_OUT, 0.25),        # main west face
        ("Verschalung_West", "y", 2.358, -1, 0.0, 5.12, ANNEX_TOP),    # above the annex
        ("Verschalung_Ost", "y", W_OUT, 1, 0.0, D_OUT, Z_OG_TOP),      # east gable
    ]
    for o, ax, face, sd, u0, u1, zb in faces:
        P = frame(ax)
        tt = lambda d0, d1: sorted((face + sd * d0, face + sd * d1))   # t range, d = depth outwards
        ops = [op for op in OPENINGS if op["ax"] == ax and abs(op["face"] - face) < 0.03
               and u0 - 0.01 <= op["a"] and op["b"] <= u1 + 0.01 and op["head"] > zb]
        holes = [(op["a"], op["b"], const(op["sill"]), const(op["head"]), False) for op in ops]
        for gx, ya, yb, zw, woff in GABLE_WIN:
            if abs(gx - face) < 0.03:
                holes.append((ya, yb, const(zw), (lambda u, w=woff: roof_top(u) - w), False))
                r = random.random()
                for ua, ub in ((ya - 0.09, ya), (yb, yb + 0.09)):
                    column(c, o, M, P, ua, ub, const(zw - 0.09),
                           lambda u, w=woff: roof_top(u) - w + 0.09, *tt(T, T + 0.02), r)
                lbox(c, o, M, P, ya - 0.09, yb + 0.09, *tt(T, T + 0.02), zw - 0.09, zw, r)
                column(c, o, M, P, ya, yb, lambda u, w=woff: roof_top(u) - w,
                       lambda u, w=woff: roof_top(u) - w + 0.09, *tt(T, T + 0.02), r)
                n = round((yb - ya) / bw)                  # the boards run on over the glass as
                for k in range(n):                         # slats with 6 cm gaps (elevations)
                    ua, ub = ya + (yb - ya) * k / n + 0.03, ya + (yb - ya) * (k + 1) / n - 0.03
                    us, r = [ua] + ([RIDGE_Y] if ua < RIDGE_Y < ub else []) + [ub], random.random()
                    for p, q in zip(us[:-1], us[1:]):          # split at the ridge kink
                        column(c, o, M, P, p, q, const(zw), lambda u, w=woff: roof_top(u) - w,
                               *tt(0, T), r)
        boards(c, o, M, P, u0, u1, const(zb), top, *tt(0, T), bw, holes, cuts=[RIDGE_Y])
        for op in ops:
            if op["kind"] == "I":                 # the back door has its own heavy frame
                continue
            a, b, s, h = op["a"], op["b"], op["sill"], op["head"]
            tr, r = tt(T, T + 0.02), random.random()                  # one rnd per trim (see wall)
            lbox(c, o, M, P, a - 0.09, a, *tr, max(s - 0.09, zb), h + 0.09, r)
            lbox(c, o, M, P, b, b + 0.09, *tr, max(s - 0.09, zb), h + 0.09, r)
            lbox(c, o, M, P, a, b, *tr, h, h + 0.09, r)
            if s > zb + 0.1:
                lbox(c, o, M, P, a - 0.09, b + 0.09, *tt(T, T + 0.05), s - 0.06, s, r)
            if op["kind"] == "W" and h - s < 1.1:            # small windows only
                n = max(2, int((b - a) / 0.2))
                for k in range(1, n + 1):
                    u = a + (b - a) * k / (n + 1)
                    lbox(c, o, "Eisen", P, u - 0.007, u + 0.007, *tt(-0.02, -0.034), s, h)
    # south-facing return above the annex (closes the gap between annex roof and roof)
    P = frame("x")
    boards(c, "Verschalung_West", M, P, -T, 2.358, const(ANNEX_TOP), const(top(5.12)), 5.12 - T, 5.12, bw)


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


CORRIDOR_EG = [(2.657, 14.575, 6.349, 8.576), (0.31, 2.358, 6.723, 8.506)]   # Flur/Windfang, back hall
BAD_EG = (bad.BAD_AT[0], bad.BAD_AT[0] + bad.W, bad.BAD_AT[1], bad.BAD_AT[1] + bad.D)   # the Bad Großeltern
                                         # lays its own floor (code/bad.py): left out of the EG's
# OG Bad NW (with the shower alcove) and Bad S
BATHS_OG = [(0.31, 2.57, 6.54, 8.57), (1.67, 2.57, 5.46, 6.54), (5.59, 8.59, 0.40, 2.62)]


def tiles(coll, obj, mat, x0, x1, y0, y1, z0, z1, widths, lengths, joint, excl=(), rng=random):
    """Rows along x (row widths cycling through `widths`), pieces of random length, skipping
    the exclusion rectangles. Rows are split at exclusion edges so pieces never overlap them.
    Lengths and rnd come from rng (a sub-model passes its own generator)."""
    y, i = y0, 0
    while y1 - y > 0.02:
        ya, yb = y, min(y + widths[i % len(widths)], y1)
        y, i = yb, i + 1
        cuts = sorted({ya, yb} | {e for r in excl for e in r[2:] if ya + 1e-6 < e < yb - 1e-6})   # no sliver rows
        for ra, rb in zip(cuts[:-1], cuts[1:]):
            gaps = sorted((r[0], r[1]) for r in excl if r[2] <= ra + 1e-6 and rb <= r[3] + 1e-6)
            spans, cur = [], x0
            for ga, gb in gaps:
                if ga > cur:
                    spans.append((cur, min(ga, x1)))
                cur = max(cur, gb)
            if cur < x1:
                spans.append((cur, x1))
            for sa, sb in spans:
                l = sa - rng.uniform(0, lengths[1])               # stagger the joints row by row
                while l < sb:
                    la, lb = max(l, sa), min(l + rng.uniform(*lengths), sb)
                    l = lb if lb > l else sb
                    if lb - la > 0.01:
                        box(coll, obj, mat, la + joint / 2, lb - joint / 2, ra + joint / 2, rb - joint / 2, z0, z1,
                            rng.random())


def floor_cover(coll, z, corridors, hole=None):
    """Floors after inside_floor_rooms.jpg (oak planks in all rooms) and
    stone_floor_corridor.jpg (limestone slabs in the EG corridors, the bathrooms and the WCs);
    dark base shows in the joints."""
    o, ex = coll + "_Bodenbelag", [hole] if hole else []
    for x0, x1, y0, y1 in FOOT:
        tiles(coll, o, "Eiche", x0, x1, y0, y1, z + 0.002, z + 0.014, [0.2], (1.2, 2.4), 0.003,
              corridors + ex)
    for x0, x1, y0, y1 in corridors:
        tiles(coll, o, "Kalkstein", x0, x1, y0, y1, z + 0.002, z + 0.018, [0.5, 0.4, 0.55, 0.45],
              (0.35, 0.8), 0.006, ex)


def build_slabs():
    slab("EG", "EG_Bodenplatte", "Decke", -0.30, 0.0)
    slab("EG", "EG_Boden", "Fuge", 0.0, 0.01, inset=0.2)
    slab("OG", "OG_Decke_EG", "Decke", Z_EG_TOP, Z_OG, hole=STAIR_HOLE)
    slab("OG", "OG_Boden", "Fuge", Z_OG, Z_OG + 0.01, inset=0.2, hole=STAIR_HOLE)
    wcs = lambda c: [r for k, _, r, _ in WCS if k == c]     # all toilets: stone floors
    floor_cover("EG", 0.0, CORRIDOR_EG + wcs("EG"), BAD_EG)
    floor_cover("OG", Z_OG, BATHS_OG + wcs("OG"), STAIR_HOLE)   # OG corridor: oak like the rooms
    slab("Dach", "Decke_OG", "Decke", Z_OG_TOP, Z_ATTIC)


# ---------------------------------------------------------------- roof & gables
def gable(x0, x1, y0, y1, windows=(), woff=0.7):
    c = "Dach"
    zb = Z_OG_TOP
    cuts = sorted(windows)
    edges, cur = [], y0
    for ya, yb, zw in cuts:
        edges.append((cur, ya, None)); edges.append((ya, yb, zw)); cur = yb
        GABLE_WIN.append((x0 if x0 < W_OUT / 2 else x1, ya, yb, zw, woff))    # outer face
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
            r = random.random()                  # shared by the frame pieces (see wall)
            prism_x(c, "Giebel_Fenster", "Glas", xm - 0.005, xm + 0.005,
                    roof_profile(ya, yb, lambda y: zw, top_w))
            prism_x(c, "Giebel_Fenster", "Laerche", xm - 0.04, xm + 0.04,
                    roof_profile(ya, yb, lambda y: zw, lambda y: zw + 0.06), r)
            prism_x(c, "Giebel_Fenster", "Laerche", xm - 0.04, xm + 0.04,
                    roof_profile(ya, yb, lambda y: top_w(y) - 0.06, top_w), r)
            for yy in (ya, yb - 0.06):
                prism_x(c, "Giebel_Fenster", "Laerche", xm - 0.04, xm + 0.04,
                        roof_profile(yy, yy + 0.06, lambda y: zw, top_w), r)


def build_roof():
    for ya, yb in [(-EAVE_OH, RIDGE_Y), (RIDGE_Y, D_OUT + EAVE_OH)]:
        prism_x("Dach", "Dach", "Dach", -GABLE_OH, W_OUT + GABLE_OH,
                [(ya, roof_top(ya)), (yb, roof_top(yb)), (yb, roof_under(yb)), (ya, roof_under(ya))])
    gable(14.575, W_OUT, 0, D_OUT, [(4.26, 6.21, 5.0), (6.90, 8.88, 5.0)], woff=0.78)   # Osten
    gable(0, 0.31, 5.145, D_OUT, [(5.69, 7.66, 5.0), (7.85, 9.83, 5.0)], woff=0.60)     # Westen
    gable(2.358, 2.772, 0, 5.475)                                                     # Westen, Rücksprung
    build_eaves()


def build_eaves():
    """Visible roof structure after terrasse_and_outside_lamps / outdoor_lamp: spruce soffit
    boards under the whole roof, rafter tails in the eave overhangs, purlin heads in the
    gable overhangs."""
    c, xa, xb = "Dach", -GABLE_OH, W_OUT + GABLE_OH
    ru = lambda y: roof_under(y)
    ys = [-EAVE_OH + 0.14 * k for k in range(int((D_OUT + 2 * EAVE_OH) / 0.14) + 1)] + [D_OUT + EAVE_OH]
    ys = sorted(set(ys + [RIDGE_Y]))
    for ya, yb in zip(ys[:-1], ys[1:]):
        prism_x(c, "Dach_Untersicht", "FichteX", xa, xb,
                [(ya, ru(ya)), (yb, ru(yb)), (yb, ru(yb) - SOFFIT), (ya, ru(ya) - SOFFIT)])
    n = round((xb - xa - 0.2) / 0.9)
    for k in range(n + 1):
        x = xa + 0.1 + (xb - xa - 0.2) * k / n
        for y0, y1 in ((-EAVE_OH, 0.0), (D_OUT, D_OUT + EAVE_OH)):
            prism_x(c, "Dach_Sparren", "FichteY", x - 0.06, x + 0.06,
                    [(y0, ru(y0) - SOFFIT), (y1, ru(y1) - SOFFIT),
                     (y1, ru(y1) - SOFFIT - 0.16), (y0, ru(y0) - SOFFIT - 0.16)])
    for y in [RIDGE_Y + s * d for d in (2.1, 4.2, 6.3) for s in (-1, 1)] + [RIDGE_Y]:
        prof = [(y - 0.08, ru(y - 0.08) - SOFFIT), (y + 0.08, ru(y + 0.08) - SOFFIT),
                (y + 0.08, ru(y) - SOFFIT - 0.22), (y - 0.08, ru(y) - SOFFIT - 0.22)]
        prism_x(c, "Dach_Sparren", "FichteX", xa, 0.0 if y >= 5.12 else 2.358, prof)
        prism_x(c, "Dach_Sparren", "FichteX", W_OUT, xb, prof)


# ---------------------------------------------------------------- balconies, terrace, surroundings
def baluster_cut(s):
    """Half width (m) of the baluster-shaped cut-out at relative height s (0 = top, 1 = bottom),
    after balcony_structure.png: point, small knob, neck, main bulb, neck, drop, lower knob, point."""
    prof = [(0, 0), (0.05, 0.008), (0.11, 0.017), (0.17, 0.007), (0.30, 0.021), (0.42, 0.007),
            (0.55, 0.014), (0.70, 0.011), (0.83, 0.019), (0.93, 0.006), (1, 0)]
    for (s0, w0), (s1, w1) in zip(prof[:-1], prof[1:]):
        if s <= s1:
            t = (s - s0) / (s1 - s0)
            return w0 + (w1 - w0) * (0.5 - 0.5 * math.cos(math.pi * t))
    return 0.0


def balcony(name, x0, x1, y0, y1, ztop, sides, ph=0.95):
    """After balcony_structure.png: larch boards with a baluster-shaped cut-out at every joint,
    horizontal rail boards at top and bottom, flat handrail, heavy edge beam over the slab
    with the joist heads showing underneath, spruce underside."""
    c, M = "Balkone", "Laerche"
    box(c, name, "Putz", x0, x1, y0, y1, ztop - 0.25, ztop)
    edge = {"N": ("x", x0, x1, lambda u, d, z: (u, y1 + d, z)),
            "S": ("x", x0, x1, lambda u, d, z: (u, y0 - d, z)),
            "E": ("y", y0, y1, lambda u, d, z: (x1 + d, u, z)),
            "W": ("y", y0, y1, lambda u, d, z: (x0 - d, u, z))}
    corner = {"N": "WE", "S": "WE", "E": "SN", "W": "SN"}   # side met at u0 / at u1
    raised = ztop > 0.1
    zr0 = ztop - (0.02 if raised else 0.0)                   # boards stand on the edge beam
    zr1 = ztop + ph - 0.045                                  # handrail on top
    rb = 0.10                                                # height of the rail boards
    for s in sides:
        ax, u0, u1, P = edge[s]
        lo, hi = corner[s]
        e0, e1 = (0.07 if lo in sides else 0), (0.07 if hi in sides else 0)
        u0e, u1e = u0 - e0, u1 + e1
        if raised:
            lbox(c, name, M, P, u0e, u1e, 0.0, 0.07, ztop - 0.27, zr0)          # edge beam
        bw = 0.12
        nb = max(1, round((u1e - u0e) / bw))
        bw = (u1e - u0e) / nb
        ct, cb = zr1 - rb - 0.06, zr0 + rb + 0.06                           # cut-out top / bottom
        ss = [i / 24 for i in range(25)]
        for j in range(nb):
            ua, ub = u0e + j * bw, u0e + (j + 1) * bw
            right = [(ub, zr0)]
            if j < nb - 1:
                right += [(ub - baluster_cut(q), ct - (ct - cb) * q) for q in reversed(ss)]
            right += [(ub, zr1)]
            left = [(ua, zr1)]
            if j > 0:
                left += [(ua + baluster_cut(q), ct - (ct - cb) * q) for q in ss]
            left += [(ua, zr0)]
            prism(c, name, M, P, right + left, 0.0, 0.028)
        lbox(c, name, M, P, u0e, u1e, 0.028, 0.05, zr0, zr0 + rb)                 # bottom rail
        lbox(c, name, M, P, u0e, u1e, 0.028, 0.05, zr1 - rb, zr1)                 # top rail
        lbox(c, name, M, P, u0e - 0.03, u1e + 0.03, -0.05, 0.08, zr1, zr1 + 0.045)  # handrail
    if raised:
        box(c, name, "FichteX", x0, x1, y0, y1, ztop - 0.27, ztop - 0.25)
        zj = (ztop - 0.41, ztop - 0.27)
        if "E" in sides and "W" not in sides:            # east balcony: joists run east-west
            n = int((y1 - y0) / 1.1)
            for k in range(n + 1):
                y = y0 + 0.1 + (y1 - y0 - 0.2) * k / n
                box(c, name, "FichteX", x0, x1 + 0.12, y - 0.06, y + 0.06, *zj)
        else:                                             # north / south: joists run north-south
            n = int((x1 - x0) / 1.1)
            ya, yb = (y0, y1 + 0.12) if "N" in sides else (y0 - 0.12, y1)
            for k in range(n + 1):
                x = x0 + 0.1 + (x1 - x0 - 0.2) * k / n
                box(c, name, "FichteY", x - 0.06, x + 0.06, ya, yb, *zj)


OUTSIDE_LIGHTS = []   # (x, y, z) filament centre of every wall lamp: the viewer lights them at dusk
LAMP_LIGHTS = []      # (x, y, z) filament centre of the switched-on lamps inside (always lit)


def lamp(x, y, z, nx, ny, c="Umgebung", o="Aussenleuchten", scale=1.0, outside=True):
    """Gooseneck wall lamp after outdoor_lamp.jpeg: black arm, flat enamel shade (white
    inside), clear bulb with a warm filament. Outside: one of the OUTSIDE_LIGHTS (lit at dusk);
    inside (outside=False, e.g. small via scale): switched on, one of the LAMP_LIGHTS."""
    sx, sy = -ny, nx
    W = lambda n, s, h: (x + (nx * n + sx * s) * scale, y + (ny * n + sy * s) * scale, z + h * scale)
    (OUTSIDE_LIGHTS if outside else LAMP_LIGHTS).append(W(0.38, 0, -0.085))
    ring = lambda n, h, r, k=16: [W(n + r * math.cos(2 * math.pi * i / k), r * math.sin(2 * math.pi * i / k), h)
                                  for i in range(k)]

    def loft(rings, mat, cap=True):
        v = [p for r in rings for p in r]
        k = len(rings[0])
        f = [(i * k + j, i * k + (j + 1) % k, (i + 1) * k + (j + 1) % k, (i + 1) * k + j)
             for i in range(len(rings) - 1) for j in range(k)]
        if cap:
            f += [list(range(k))[::-1], list(range((len(rings) - 1) * k, len(rings) * k))]
        add(c, o, mat, v, f)

    # rosette: disc on the wall (axis = wall normal)
    disc = lambda n: [W(n, 0.05 * math.cos(2 * math.pi * i / 16), 0.05 * math.sin(2 * math.pi * i / 16))
                      for i in range(16)]
    loft([disc(0.0), disc(0.03)], "Eisen")
    # arm: horizontal, quarter bend up, straight up, half bend over, down into the shade
    path = [(0.03, 0.0), (0.10, 0.0)]
    path += [(0.10 + 0.12 * math.sin(math.pi / 2 * i / 8), 0.12 - 0.12 * math.cos(math.pi / 2 * i / 8))
             for i in range(1, 9)]
    path += [(0.22, 0.20)]
    path += [(0.30 - 0.08 * math.cos(math.pi * i / 12), 0.20 + 0.08 * math.sin(math.pi * i / 12))
             for i in range(1, 13)]
    path += [(0.38, 0.06)]
    rings = []
    for i, (n, h) in enumerate(path):
        pa, pb = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        tn, th = pb[0] - pa[0], pb[1] - pa[1]
        ln = math.hypot(tn, th)
        nn, nh = -th / ln, tn / ln                      # normal in the (n, h) plane
        r = 0.012
        rings.append([W(n + r * math.cos(2 * math.pi * j / 10) * nn, r * math.sin(2 * math.pi * j / 10),
                        h + r * math.cos(2 * math.pi * j / 10) * nh) for j in range(10)])
    loft(rings, "Eisen")
    loft([ring(0.38, 0.06, 0.05), ring(0.38, 0.02, 0.06)], "Eisen")
    loft([ring(0.38, 0.02, 0.06, 32), ring(0.38, -0.03, 0.18, 32)], "Eisen", cap=False)
    loft([ring(0.38, 0.016, 0.055, 32), ring(0.38, -0.034, 0.175, 32)], "Emaille", cap=False)
    bulb = [ring(0.38, -0.02 - 0.075 * (1 - math.cos(math.pi * i / 8)), 0.05 * math.sin(math.pi * i / 8) + 0.001, 12)
            for i in range(9)]
    loft(bulb, "Glas")
    loft([ring(0.38, -0.06, 0.006, 6), ring(0.38, -0.11, 0.006, 6)], "Gluehfaden" if outside else "GluehfadenAn")


def build_terrace():
    """After terrasse_and_outside_lamps.jpeg: granite slabs of mixed size in rows along the
    wall, a pebble strip against the wall, soil beds for the bushes (garden.py plants them).
    South part as drawn in the plan (from the annex, 3.0 m deep), running on into the east paving."""
    c = "Umgebung"
    tw, td, tx, strip = 4.0, 3.0, ANNEX[1], 0.25            # east width, south depth, west end
    bed_e = (W_OUT, W_OUT + strip + 0.6, 7.9, 12.8)          # east, north of the entrance
    bed_w = (-0.70, -0.025, 8.7, 12.8)                       # west, north of the back door
    door = (6.3, 7.7)                                        # threshold in front of the entrance
    box(c, "Terrasse", "Fuge", tx, W_OUT + tw, -td, 0, -0.10, -0.025)
    box(c, "Terrasse", "Fuge", W_OUT, W_OUT + tw, 0, D_OUT, -0.10, -0.025)
    rows = [0.6, 0.45, 0.6, 0.5, 0.6, 0.45, 0.55, 0.6]

    def slabs(axis, r0, r1, l0, l1):
        """Rows across r (r0 -> r1), slabs of random length along l. axis "x": l = x, r = y."""
        r, i = r0, 0
        step = 1 if r1 > r0 else -1
        while (r1 - r) * step > 0.05:
            d = min(rows[i % len(rows)], abs(r1 - r))
            ra, rb = sorted((r, r + step * d))
            l = l0
            while l1 - l > 0.05:
                ln = random.uniform(0.55, 1.05)
                if l1 - (l + ln) < 0.3:
                    ln = l1 - l
                la, lb, l, g = l, l + ln, l + ln, 0.006
                if axis == "x":
                    box(c, "Terrasse", "Granit", la + g, lb - g, ra + g, rb - g, -0.05, -0.01)
                else:
                    box(c, "Terrasse", "Granit", ra + g, rb - g, la + g, lb - g, -0.05, -0.01)
            r += step * d
            i += 1

    slabs("x", -strip, -td, tx, W_OUT + tw)
    slabs("x", 0, -strip, W_OUT + strip, W_OUT + tw)                  # SE corner, strip row
    slabs("y", W_OUT + strip, bed_e[1], 0, bed_e[2])                  # first row stops at the bed
    slabs("y", bed_e[1], W_OUT + tw, 0, D_OUT)
    box(c, "Terrasse", "Granit", W_OUT, W_OUT + strip, door[0], door[1], -0.05, -0.01)
    # pebble strip (gravel bed + pebbles)
    strips = [(tx, W_OUT + strip, -strip, 0), (W_OUT, W_OUT + strip, 0, door[0]),
              (W_OUT, W_OUT + strip, door[1], bed_e[2])]
    for x0, x1, y0, y1 in strips:
        box(c, "Kiesstreifen", "Kies", x0, x1, y0, y1, -0.10, -0.035)
        n = int((x1 - x0) * (y1 - y0) * 260)
        for _ in range(n):
            pebble(random.uniform(x0 + 0.02, x1 - 0.02), random.uniform(y0 + 0.02, y1 - 0.02))
    for name, (x0, x1, y0, y1) in (("Beet_Ost", bed_e), ("Beet_West", bed_w)):
        box(c, name, "Erde", x0, x1, y0, y1, -0.10, -0.02)          # brown soil, above the joint base


def pebble(x, y):
    r = random.uniform(0.018, 0.035)
    sx, sy, sz = r * random.uniform(1.0, 1.5), r * random.uniform(0.8, 1.1), r * random.uniform(0.45, 0.65)
    a = random.uniform(0, math.pi)
    ca, sa = math.cos(a), math.sin(a)
    v = []
    for i in range(5):                                        # 5 latitude rings x 8
        th = math.pi * (i + 0.5) / 5
        for j in range(8):
            ph = 2 * math.pi * j / 8
            px, py, pz = sx * math.sin(th) * math.cos(ph), sy * math.sin(th) * math.sin(ph), sz * math.cos(th)
            v.append((x + px * ca - py * sa, y + px * sa + py * ca, -0.035 + pz * 0.8))
    f = [(i * 8 + j, i * 8 + (j + 1) % 8, (i + 1) * 8 + (j + 1) % 8, (i + 1) * 8 + j)
         for i in range(4) for j in range(8)]
    f += [list(range(8))[::-1], list(range(32, 40))]
    add("Umgebung", "Kiesel", "Kiesel", v, f)


def build_outside():
    balcony("Balkon_OG_Nord", 0.17, 14.45, D_OUT, 14.17, Z_OG, "NEW")
    balcony("Balkon_OG_Ost", W_OUT, 16.085, 0.95, 11.75, Z_OG, "NES")
    balcony("Balkon_OG_Sued", 9.00, 12.93, -1.10, 0, Z_OG, "SEW")
    balcony("Balkon_EG_Nord", 0.17, 5.86, D_OUT, 14.08, 0.0, "NEW", ph=0.90)
    build_terrace()
    for x in (5.55, 8.85, 14.3):                             # south terrace wall
        lamp(x, 0.0, 1.95, 0, -1)
    for y in (0.7, 5.7, 9.3):                                # east terrace wall
        lamp(W_OUT, y, 1.95, 1, 0)
    for y in (7.05, 8.73):                                   # either side of the back door (west)
        lamp(-0.025, y, 1.95, -1, 0)
    c = "Umgebung"
    build_annex()
    box(c, "Gelaende", "Wiese", -20, 35, -25, 35, -0.30, -0.05)
    SMOOTH.update({"Kiesel", "Aussenleuchten"})


def build_annex():
    """Elektroraum (north) and Heizung (south) in the SW corner, after the plan of 2026-10-19
    (replaces the shed): timber-framed walls (plan: wood hatching, 0.20 m) clad with vertical
    larch boards, flat roof with overhang (OG plan, top from the elevations; object Dach_Anbau),
    plank door in the west wall, panel door from the Elektroraum to the Heizung."""
    c, o, M, T, t = "EG", "EG_Anbau", "Laerche", 0.025, 0.20
    x0, x1, y0, y1 = ANNEX
    zr, ym = ANNEX_TOP - 0.15, 2.59                         # roof underside, partition (south face)
    door, dh, fw = (3.50, 4.30), 2.10, 0.07                 # outside door (west wall)
    box(c, o, "Decke", x0, x1, y0, y1, -0.30, 0.0)          # floor slab
    box(c, o, "Putz", x0, x0 + t, y0, door[0], 0, zr)       # west wall with door
    box(c, o, "Putz", x0, x0 + t, door[1], y1, 0, zr)
    box(c, o, "Putz", x0, x0 + t, door[0], door[1], dh, zr)
    box(c, o, "Putz", x0 + t, x1, y0, y0 + t, 0, zr)        # south
    box(c, o, "Putz", x0 + t, x1, y1 - t, y1, 0, zr)        # north (against the WC wall east of x=0)
    box(c, o, "Putz", x1 - t, x1, y0 + t, y1 - t, 0, zr)    # east, against the house
    da, db = -1.14, -0.34                                   # partition with door
    box(c, o, "Putz", x0 + t, da, ym, ym + t, 0, zr)
    box(c, o, "Putz", db, x1 - t, ym, ym + t, 0, zr)
    box(c, o, "Putz", da, db, ym, ym + t, DOOR_H, zr)
    panel_door(c, "x", da, db, ym, ym + t, 0, DOOR_H, -1, "b")
    # boards outside: west (round the SW corner), south, the free part of the north face
    PY, PX = frame("y"), frame("x")
    boards(c, o, M, PY, y0 - T, y1 + T, const(0.02), const(zr), x0 - T, x0, 0.17,
           holes=[(door[0] - fw, door[1] + fw, const(0.0), const(dh + fw), False)])
    boards(c, o, M, PX, x0, x1, const(0.02), const(zr), y0 - T, y0, 0.17)
    boards(c, o, M, PX, x0, -T, const(0.02), const(zr), y1, y1 + T, 0.17)
    # plank door: trim in the board layer, leaf in the wall
    r = random.random()
    for ua, ub in ((door[0] - fw, door[0]), (door[1], door[1] + fw)):
        lbox(c, o, M, PY, ua, ub, x0 - T - 0.02, x0, 0.0, dh + fw, r)
    lbox(c, o, M, PY, door[0], door[1], x0 - T - 0.02, x0, dh, dh + fw, r)
    boards(c, o, "Tuer", PY, door[0] + 0.004, door[1] - 0.004, const(0.01), const(dh - 0.004),
           x0 + 0.02, x0 + 0.06, 0.13)
    lbox(c, o, "Eisen", PY, door[0] + 0.08, door[0] + 0.12, x0 + 0.005, x0 + 0.02, 1.0, 1.15)
    # flat roof with overhang; it stops at the house wall, west of the house it overlaps it
    xr, yr0, yr1 = x0 - 0.30, y0 - 0.32, y1 + 0.27
    # (own object in the Dach collection, so "Ohne Dach" / "Nur EG" open the annex too)
    xy_prism("Dach", "Dach_Anbau", "Dach", [(xr, yr0), (x1, yr0), (x1, y1), (-T, y1), (-T, yr1), (xr, yr1)],
             zr, ANNEX_TOP)


# ---------------------------------------------------------------- furniture (plans of 2026-10-19)
# Loose furniture appears in the viewer's last stage "Eingerichtet" (Blueprint.furniture); the
# built-ins (kitchen, sanitary, Ofen) belong to the house. Positions from the plan, snapped
# to the model's wall faces. Built last, so the random shading of everything else stays as it was.
FURNITURE = {"EG_Tisch", "EG_Stuehle", "EG_Moebel", "OG_Moebel", "EG_Geraete", "EG_Bildschirm_L", "EG_Bildschirm_R"}


def _grain(ax):
    return "FichteX" if ax == "x" else "FichteY"


def bed(c, x0, x1, y0, y1, head, z=0.0, n=1):
    """Spruce bed on four legs with a headboard on side head ("N"/"S"/"E"/"W"), n mattresses
    side by side, duvet and pillows."""
    o, ax = c + "_Moebel", "x" if head in "EW" else "y"
    P, G = frame(ax), _grain(ax)
    u0, u1, t0, t1 = (x0, x1, y0, y1) if ax == "x" else (y0, y1, x0, x1)
    s, uh = (1, u0) if head in "WS" else (-1, u1)               # head end, direction to the foot
    uf = u1 if s > 0 else u0
    zf, zm = z + 0.30, z + 0.50                                  # frame top / mattress top
    for ua in (u0 + 0.02, u1 - 0.08):                            # legs, inset from the frame edges
        for ta in (t0 + 0.02, t1 - 0.08):
            lbox(c, o, "FichteZ", P, ua, ua + 0.06, ta, ta + 0.06, z + 0.012, z + 0.12)
    lbox(c, o, G, P, u0, u1, t0, t1, z + 0.12, zf)
    lbox(c, o, G, P, uh - s * 0.005, uh + s * 0.04, t0 - 0.01, t1 + 0.01, z + 0.10, z + 0.90)   # headboard
    ma, mb = uh + s * 0.045, uf - s * 0.03
    w = (t1 - t0 - 0.06 - 0.01 * (n - 1)) / n
    for k in range(n):
        ta = t0 + 0.03 + k * (w + 0.01)
        lbox(c, o, "Leinen", P, ma, mb, ta, ta + w, zf, zm)
        pc = ta + w / 2
        lbox(c, o, "Bettwaesche", P, ma + s * 0.04, ma + s * 0.39, pc - 0.25, pc + 0.25, zm, zm + 0.10)
    lbox(c, o, "Bettwaesche", P, ma + s * 0.45, mb + s * 0.02, t0 + 0.01, t1 - 0.01, zm, zm + 0.06)   # duvet


def nightstand(c, x0, x1, y0, y1, z=0.0):
    o = c + "_Moebel"
    box(c, o, "FichteZ", x0 + 0.01, x1 - 0.01, y0 + 0.01, y1 - 0.01, z + 0.012, z + 0.48)
    box(c, o, "FichteX", x0, x1, y0, y1, z + 0.48, z + 0.50)


def cabinet(c, x0, x1, y0, y1, front, cuts, z=0.0, h=2.0):
    """Wardrobe / cupboard: carcass, doors between the cuts (along the front), handles.
    front = side the doors face ("N"/"S"/"E"/"W")."""
    o, ax = c + "_Moebel", "x" if front in "NS" else "y"
    P = frame(ax)
    t0, t1 = (y0, y1) if ax == "x" else (x0, x1)
    f, s = (t0, 1) if front in "SW" else (t1, -1)               # front plane, direction inwards
    if s > 0:
        t0 += 0.02
    else:
        t1 -= 0.02
    lbox(c, o, "FichteZ", P, cuts[0], cuts[-1], t0, t1, z + 0.012, z + h)
    for a, b in zip(cuts[:-1], cuts[1:]):
        r = random.random()
        lbox(c, o, "FichteZ", P, a + 0.003, b - 0.003, f, f + s * 0.02, z + 0.06, z + h - 0.01, r)
        m = b - 0.06 if (cuts.index(a) % 2 == 0) else a + 0.06
        lbox(c, o, "Metall", P, m - 0.008, m + 0.008, f - s * 0.025, f, z + min(1.0, h / 2), z + min(1.0, h / 2) + 0.20)


def bunk_bed(c, x0, x1, y0, y1, ladder, z):
    """Spruce bunk bed along y, head at the south (wall) end: corner posts, two frames with
    mattress, duvet and pillow, end boards, guard rails up top, ladder at the north end on the
    room side ("E"/"W")."""
    o = c + "_Moebel"
    zb = z + 0.012
    for xa in (x0, x1 - 0.07):
        for ya in (y0, y1 - 0.07):
            box(c, o, "FichteZ", xa, xa + 0.07, ya, ya + 0.07, zb, z + 1.80)
    for zf in (z + 0.20, z + 1.15):
        for xa in (x0 + 0.01, x1 - 0.04):                        # side rails
            box(c, o, "FichteY", xa, xa + 0.03, y0 + 0.07, y1 - 0.07, zf, zf + 0.14)
        for ya in (y0 + 0.01, y1 - 0.04):                        # end boards
            box(c, o, "FichteX", x0 + 0.07, x1 - 0.07, ya, ya + 0.03, zf, zf + 0.45)
        box(c, o, "FichteX", x0 + 0.04, x1 - 0.04, y0 + 0.04, y1 - 0.04, zf + 0.02, zf + 0.04)   # base
        zm = zf + 0.18
        box(c, o, "Leinen", x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, zf + 0.04, zm)
        cx = (x0 + x1) / 2
        box(c, o, "Bettwaesche", cx - 0.25, cx + 0.25, y0 + 0.09, y0 + 0.44, zm, zm + 0.10)
        box(c, o, "Bettwaesche", x0 + 0.06, x1 - 0.06, y0 + 0.50, y1 - 0.04, zm, zm + 0.06)
    xw, xr = (x0 + 0.01, x1 - 0.04) if ladder == "E" else (x1 - 0.04, x0 + 0.01)   # wall / room side
    box(c, o, "FichteY", xw, xw + 0.03, y0 + 0.07, y1 - 0.07, z + 1.48, z + 1.58)    # guard rails
    box(c, o, "FichteY", xr, xr + 0.03, y0 + 0.07, y1 - 0.52, z + 1.48, z + 1.58)
    xl = x1 if ladder == "E" else x0 - 0.04                      # ladder outside the room-side rail
    for ya in (y1 - 0.50, y1 - 0.12):
        box(c, o, "FichteZ", xl, xl + 0.04, ya, ya + 0.05, zb, z + 1.60)
    for k in range(5):
        zr = z + 0.40 + 0.26 * k
        box(c, o, "FichteY", xl + 0.005, xl + 0.035, y1 - 0.45, y1 - 0.12, zr, zr + 0.03)


def ngon_x(c, o, m, xa, xb, yc, zc, r, k=20):
    """Disc of radius r in the y-z plane, from x = xa to xb."""
    v = [(x, yc + r * math.cos(2 * math.pi * i / k), zc + r * math.sin(2 * math.pi * i / k))
         for x in (xa, xb) for i in range(k)]
    f = [list(range(k))[::-1], list(range(k, 2 * k))] + [(i, (i + 1) % k, k + (i + 1) % k, k + i) for i in range(k)]
    add(c, o, m, v, f)


def machine(c, x0, x1, y0, y1, z):
    """Front loader (washer or dryer) against an east wall, door facing west."""
    o = c + "_Moebel"
    box(c, o, "Emaille", x0, x1, y0, y1, z + 0.012, z + 0.85)
    yc = (y0 + y1) / 2
    ngon_x(c, o, "Metall", x0 - 0.02, x0, yc, z + 0.45, 0.20)
    ngon_x(c, o, "Eisen", x0 - 0.025, x0 - 0.02, yc, z + 0.45, 0.15)
    box(c, o, "Eisen", x0 - 0.005, x0, y0 + 0.05, y1 - 0.05, z + 0.74, z + 0.82)    # control panel


def wicker_basket(c, o, x0, x1, y0, y1, z, h=0.35):
    """Coarsely woven wicker basket on the outline x0..x1, y0..y1: bottom, a core wall, vertical
    stakes about 9 cm apart, round weavers swelling in the middle, each centred on a stake and in
    front of it or behind it in a checker (the stake shows where the weaver passes behind), a
    round rim."""
    wt, pitch = 0.012, 0.028
    box(c, o, "Weide", x0, x1, y0, y1, z, z + wt)                              # bottom
    r = random.random()
    for xa in (x0 + 0.022, x1 - 0.030):                                        # core
        box(c, o, "Weide", xa, xa + 0.008, y0 + 0.022, y1 - 0.022, z + wt, z + h, r)
    for ya in (y0 + 0.022, y1 - 0.030):
        box(c, o, "Weide", x0 + 0.030, x1 - 0.030, ya, ya + 0.008, z + wt, z + h, r)
    rows = round((h - wt) / pitch)
    pz = (h - wt) / rows
    prof = [(0.008, 0), (0.0135, 0.5), (0.008, 1)]
    walls = (("x", x0, -1, (y0, y1)), ("x", x1, 1, (y0, y1)), ("y", y0, -1, (x0, x1)), ("y", y1, 1, (x0, x1)))
    P = lambda ax, t, u, zz: (t, u, zz) if ax == "x" else (u, t, zz)
    for ax, edge, s, (u0, u1) in walls:
        n = max(1, round((u1 - u0) / 0.09))
        L = (u1 - u0) / n
        for i in range(1, n):                                                  # stakes (corners: none)
            t = edge - s * 0.010
            turned(c, o, "Weide", P(ax, t, u0 + i * L, z + wt), P(ax, t, u0 + i * L, z + h), [(0.007, 0), (0.007, 1)], 6, r)
    for j in range(rows):
        zc, rr = z + wt + (j + 0.5) * pz, random.random()                      # one weaver per row
        for ax, edge, s, (u0, u1) in walls:
            n = max(1, round((u1 - u0) / 0.09))
            L = (u1 - u0) / n
            for i in range(n + 1):                                             # centred on stake i
                ua, ub = max(u0 + 0.012, u0 + (i - 0.5) * L), min(u1 - 0.012, u0 + (i + 0.5) * L)
                t = edge - s * (0.002 if (i + j) % 2 == 0 else 0.020)          # in front / behind
                turned(c, o, "Weide", P(ax, t, ua, zc), P(ax, t, ub, zc), prof, 6, rr)
    zr, rim = z + h + 0.013, [(0.015, 0), (0.015, 1)]                          # rim
    for pa, pb in (((x0 + 0.006, y0, zr), (x0 + 0.006, y1, zr)), ((x1 - 0.006, y0, zr), (x1 - 0.006, y1, zr)),
                   ((x0, y0 + 0.006, zr), (x1, y0 + 0.006, zr)), ((x0, y1 - 0.006, zr), (x1, y1 - 0.006, zr))):
        turned(c, o, "Weide", pa, pb, rim, 8, r)


def basket_cupboard(c, x0, x1, y0, y1, z):
    """Open spruce cupboard against a west wall, facing east: back panel, two sides, continuous
    shelves, on each shelf three wicker laundry baskets holding a heap of laundry."""
    o, h, xb = c + "_Moebel", 2.0, x0 + 0.025                          # back panel 1 cm off the wall
    box(c, o, "FichteZ", x0 + 0.01, xb, y0, y1, z + 0.012, z + h)
    for ya in (y0, y1 - 0.02):                                         # sides
        box(c, o, "FichteZ", xb, x1, ya, ya + 0.02, z + 0.012, z + h - 0.02)
    box(c, o, "FichteY", xb, x1, y0, y1, z + h - 0.02, z + h)            # top
    n, bw = 3, 0.66                                                    # baskets per shelf, their width
    gap = (y1 - y0 - 0.04 - n * bw) / (n + 1)
    cl = ("Leinen", "Bettwaesche", "Creme")
    for j, zs in enumerate((0.10, 0.72, 1.34)):                        # board tops
        box(c, o, "FichteY", xb, x1 - 0.005, y0 + 0.02, y1 - 0.02, z + zs - 0.02, z + zs)
        for k in range(n):
            bx0, bx1, by0, zb = xb + 0.05, x1 - 0.04, y0 + 0.02 + gap + k * (bw + gap), z + zs + 0.001
            by1 = by0 + bw
            wicker_basket(c, o, bx0, bx1, by0, by1, zb)
            zl = zb + 0.24 + 0.06 * ((k + 2 * j) % 3)                  # laundry heap, some above the rim
            box(c, o, cl[(k + j) % 3], bx0 + 0.035, bx1 - 0.035, by0 + 0.035, by1 - 0.035, zb + 0.012, zl)
            box(c, o, cl[(k + j + 1) % 3], bx0 + 0.07, bx1 - 0.10, by0 + 0.08 + 0.05 * j, by1 - 0.14 + 0.04 * k,
                zl, zl + 0.07)


def folded_stack(c, x, y, z, mats):
    """Neatly folded clothes piled on each other, centred on (x, y), from the bottom up."""
    o = c + "_Moebel"
    for i, m in enumerate(mats):
        w, d, t = 0.32 + 0.01 * (i % 3 - 1), 0.26 + 0.008 * ((i + 1) % 3 - 1), 0.035 + 0.005 * (i % 2)
        box(c, o, m, x - w / 2, x + w / 2, y - d / 2, y + d / 2, z, z + t)
        z += t


def grand_piano():
    """Grand piano in the Musikraum after the plan symbol: case outline, lid, three legs,
    keyboard towards the south, bench in front; turned 30° to the left (counter-clockwise, on
    request) about the case centre, then 180° about the centre of its footprint (on request
    2026-11-08: keyboard and bench to the north; about the case centre it would hit the wall)."""
    c, o = "EG", "EG_Moebel"
    n0 = len(GEO.get((c, o), {"v": []})["v"])
    a, b, cx, yb = 0.585, 0.43, 8.385, 11.75
    pts = [(7.80, 10.48), (9.03, 10.48), (9.03, 11.10), (8.95, 11.22), (8.86, 11.36), (8.88, 11.55), (8.97, 11.72)]
    pts += [(cx + a * math.cos(math.pi * i / 12), yb + b * math.sin(math.pi * i / 12)) for i in range(13)]
    xy_prism(c, o, "Klavierlack", pts, 0.66, 0.96)                               # case
    xy_prism(c, o, "Klavierlack", pts, 0.975, 0.99)                              # lid, a gap above the case
    for x, y in ((7.90, 10.58), (8.86, 10.58), (8.40, 11.95)):
        box(c, o, "Klavierlack", x - 0.04, x + 0.04, y - 0.04, y + 0.04, 0.012, 0.66)
    box(c, o, "Klavierlack", 7.80, 7.86, 10.30, 10.48, 0.62, 0.82)                # key cheeks
    box(c, o, "Klavierlack", 8.97, 9.03, 10.30, 10.48, 0.62, 0.82)
    box(c, o, "Klavierlack", 7.86, 8.97, 10.30, 10.48, 0.62, 0.70)                # key bed
    box(c, o, "Keramik", 7.865, 8.965, 10.31, 10.48, 0.70, 0.72)                 # white keys
    box(c, o, "Klavierlack", 7.865, 8.965, 10.42, 10.48, 0.72, 0.73)              # black keys (row)
    box(c, o, "Klavierlack", 8.30, 8.95, 9.85, 10.20, 0.46, 0.50)                 # bench
    for x in (8.32, 8.89):
        for y in (9.87, 10.14):
            box(c, o, "Klavierlack", x, x + 0.04, y, y + 0.04, 0.012, 0.46)
    g, (px, py), ca, sa = GEO[(c, o)], (8.415, 11.33), math.cos(math.radians(30)), math.sin(math.radians(30))
    g["v"][n0:] = [(px + (x - px) * ca - (y - py) * sa, py + (x - px) * sa + (y - py) * ca, z) for x, y, z in g["v"][n0:]]
    xs, ys = [v[0] for v in g["v"][n0:]], [v[1] for v in g["v"][n0:]]          # then 180° in place: same
    cx, cy = min(xs) + max(xs), min(ys) + max(ys)                              # footprint, keyboard north
    g["v"][n0:] = [(cx - x, cy - y, z) for x, y, z in g["v"][n0:]]


def bookcase():
    """Old-style bookcase in the Bibliothek, floor to ceiling, on the Flur wall opposite the desk:
    from 1 m east of the workshop stove to the Büro door; dark walnut with plinth, three bays,
    five shelves and a stepped cornice, filled with books of random size (some gaps)."""
    c, o, rng = "EG", "EG_Moebel", random.Random(7)
    x0, x1, y0, y1 = 10.861, 13.42, 8.880, 9.24
    t, levels = 0.03, [0.12 + 0.36 * k for k in range(6)]                       # shelf undersides
    box(c, o, "NussZ", x0, x1, y0, y0 + 0.012, 0.012, 2.30)                      # back
    box(c, o, "NussX", x0 + 0.02, x1 - 0.02, y0 + 0.012, y1 - 0.03, 0.012, 0.12)  # plinth
    ups = [x0 + (x1 - x0 - t) * k / 3 for k in range(4)]
    for u in ups:
        box(c, o, "NussZ", u, u + t, y0 + 0.012, y1, 0.012, 2.30)                # sides and uprights
    for a, b in zip(ups, ups[1:]):
        xa, xb = a + t, b
        for z in levels + [2.27]:
            box(c, o, "NussX", xa, xb, y0 + 0.012, y1 - 0.005, z, z + t)          # shelves, top board
        for z, top in zip([z + t for z in levels], levels[1:] + [2.27]):         # books, front-aligned
            x = xa + 0.01
            while True:
                if rng.random() < 0.08:
                    x += rng.uniform(0.04, 0.10)                                   # a gap
                w, h, d = rng.uniform(0.02, 0.05), rng.uniform(0.19, min(0.30, top - z - 0.02)), rng.uniform(0.17, 0.25)
                if x + w > xb - 0.01:
                    break
                box(c, o, "Buecher", x, x + w, y1 - 0.03 - d, y1 - 0.03, z + 0.001, z + h)
                x += w + 0.002
    box(c, o, "NussX", x0 - 0.02, x1 + 0.02, y0, y1 + 0.02, 2.30, 2.35)           # cornice
    box(c, o, "NussX", x0 - 0.02, x1 + 0.02, y0, y1 + 0.04, 2.35, 2.396)


def side_table(c, cx, cy, turn=0.0):
    """Round side table after tischchen.jpeg: top with a thicker rim on an apron ring, turned
    baluster column, three curved feet (the first towards `turn` degrees)."""
    o = c + "_Moebel"
    turned(c, o, "TeakX", (cx, cy, 0.655), (cx, cy, 0.68), [(0.25, 0), (0.25, 1)], 32)            # top
    turned(c, o, "TeakX", (cx, cy, 0.60), (cx, cy, 0.656), [(0.205, 0), (0.205, 0.6), (0.215, 1)], 32)  # apron
    col = [(0.03, 0), (0.05, 0.08), (0.055, 0.10), (0.055, 0.40), (0.065, 0.42), (0.065, 0.46), (0.038, 0.50),
           (0.045, 0.58), (0.065, 0.68), (0.06, 0.74), (0.03, 0.84), (0.045, 0.87), (0.045, 0.90), (0.05, 0.93),
           (0.05, 1)]                                                                            # z 0.06 .. 0.60
    turned(c, o, "TeakZ", (cx, cy, 0.06), (cx, cy, 0.60), col, 20)
    foot = [(0.04, 0.24), (0.07, 0.21), (0.11, 0.15), (0.16, 0.09), (0.22, 0.05), (0.27, 0.03), (0.30, 0.03),
            (0.30, 0.012), (0.25, 0.012), (0.20, 0.03), (0.14, 0.06), (0.09, 0.10), (0.04, 0.12)]
    for k in range(3):
        a, t = math.radians(turn + 120 * k), 0.018
        ca, sa = math.cos(a), math.sin(a)
        pts = [(cx + r * ca - s * t * sa, cy + r * sa + s * t * ca, z) for s in (-1, 1) for r, z in foot]
        n = len(foot)
        add(c, o, "TeakX", pts, [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
            + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)])


def armchair(c, cx, cy, face):
    """Small cocktail armchair after sessel-klein.jpg, seat centred at (cx, cy), facing `face`
    degrees: bouclé seat box with piping and cushion, back curved in plan and flaring towards
    the top, four splayed tapered wooden legs."""
    o, a = c + "_Moebel", math.radians(face)
    W = lambda u, v, z: (cx - u * math.sin(a) + v * math.cos(a), cy + u * math.cos(a) + v * math.sin(a), z)

    def seat(d, z0, z1, mat):
        uv = [(-0.26 - d, -0.27 - d), (0.26 + d, -0.27 - d)]                 # back, then the bowed front
        uv += [((0.31 + d) * math.cos(math.pi * i / 8), 0.26 + (0.05 + d) * math.sin(math.pi * i / 8)) for i in range(9)]
        xy_prism(c, o, mat, [W(u, v, 0)[:2] for u, v in uv], z0, z1)

    for (ut, vt), (uf, vf) in (((0.21, -0.19), (0.28, -0.29)), ((0.23, 0.19), (0.29, 0.28))):
        for s in (-1, 1):
            turned(c, o, "TeakZ", W(s * uf, vf, 0.019), W(s * ut, vt, 0.215), [(0.012, 0), (0.021, 1)], 10)
    seat(0.0, 0.20, 0.40, "Boucle")
    seat(0.006, 0.395, 0.405, "Paspel")
    seat(-0.004, 0.404, 0.45, "Boucle")
    n, v, f = 12, [], []
    for i in range(n + 1):                                       # back: front/back surface, bottom/top row
        s = -1 + 2 * i / n
        zt = 0.80 - 0.08 * s ** 6
        for u, vv, z in ((0.27 * s, -0.20 + 0.06 * s * s, 0.22), (0.27 * s, -0.29 + 0.06 * s * s, 0.22),
                         (0.34 * s, -0.31 + 0.10 * s * s, zt), (0.34 * s, -0.39 + 0.10 * s * s, zt)):
            v.append(W(u, vv, z))
    for i in range(n):
        p, q = 4 * i, 4 * i + 4
        f += [(p, q, q + 2, p + 2), (p + 1, p + 3, q + 3, q + 1), (p + 2, q + 2, q + 3, p + 3), (p, p + 1, q + 1, q)]
    f += [(0, 2, 3, 1), (4 * n, 4 * n + 1, 4 * n + 3, 4 * n + 2)]
    add(c, o, "Boucle", v, f)


def sofa(c, cx, cy, face):
    """Three-seater sofa after sofa.tiff (2.25 x 0.98 m), centred at (cx, cy), facing `face`
    degrees: linen base to the floor, square arms, back frame, three seat and three back cushions
    (leaning back), a scatter pillow at each arm."""
    o, a = c + "_Moebel", math.radians(face)
    W = lambda u, v, z: (cx - u * math.sin(a) + v * math.cos(a), cy + u * math.cos(a) + v * math.sin(a), z)
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]

    def ubox(u0, u1, v0, v1, z0, z1):
        add(c, o, "Leinen", [W(u, v, z) for z in (z0, z1) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))], faces)

    def cushion(u0, u1, prof):                                   # (v, z) profile extruded along u
        n = len(prof)
        add(c, o, "Leinen", [W(u, v, z) for u in (u0, u1) for v, z in prof],
            [list(range(n))[::-1], list(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)])

    ubox(-0.97, 0.97, -0.30, 0.47, 0.012, 0.40)                  # base
    ubox(-0.97, 0.97, -0.49, -0.30, 0.012, 0.64)                 # back frame
    for s in (-1, 1):
        ubox(s * 0.97, s * 1.125, -0.49, 0.49, 0.012, 0.64)      # arms
    seat = [(-0.28, 0.40), (0.48, 0.40), (0.485, 0.50), (0.465, 0.53), (-0.28, 0.53)]
    back = [(-0.30, 0.53), (-0.09, 0.53), (-0.16, 0.83), (-0.20, 0.87), (-0.34, 0.87), (-0.38, 0.83)]
    w = 1.94 / 3
    for k in range(3):
        u0 = -0.97 + k * w
        cushion(u0 + 0.004, u0 + w - 0.004, seat)
        cushion(u0 + 0.004, u0 + w - 0.004, back)
    for s in (-1, 1):                                            # pillows: tilted back, turned in their plane
        t, r = math.radians(18), math.radians(-s * 15)
        e1 = (math.cos(r), -math.sin(r) * math.sin(t), math.sin(r) * math.cos(t))    # (u, v, z)
        e2 = (-math.sin(r), -math.cos(r) * math.sin(t), math.cos(r) * math.cos(t))
        nv = (0, math.cos(t), math.sin(t))
        m = (s * 0.68, -0.08, 0.71)
        pts = [tuple(m[i] + p * 0.18 * e1[i] + q * 0.18 * e2[i] + h * 0.06 * nv[i] for i in range(3))
               for h in (-1, 1) for p, q in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        add(c, o, "Leinen", [W(*p) for p in pts], faces)


def sitzecke():
    """Stube: seating corner between the two big windows (south wall face y 0.415, east wall face
    x 14.351): side table on the corner's diagonal, an armchair either side of it, mirror images
    about that diagonal, each turned 25° towards the other."""
    xc, yc = 14.351, 0.415
    side_table("EG", xc - 0.42, yc + 0.42, -45)
    armchair("EG", xc - 1.22, yc + 0.49, 65)
    armchair("EG", xc - 0.49, yc + 1.22, 205)


def build_furniture():
    zo = Z_OG
    # EG: Großeltern, Musikraum, Büro (dining table and chairs, Speis built-ins: build_eg)
    bed("EG", 3.98, 6.022, 9.89, 11.75, "E", n=2)
    nightstand("EG", 5.62, 6.02, 11.77, 12.25)
    nightstand("EG", 5.62, 6.02, 9.41, 9.87)
    grand_piano()
    desk.desk_neu("EG", *desk.DESK_AT)                      # between the two north french doors, with its devices
    bookcase()
    desk.stuhl("EG", *desk.DESK_AT)
    # OG: Yoga, Jugend (two bunk beds instead of the plan's double bed), Schlafen NE, SW, SE, HWR
    bed("OG", 0.86, 2.45, 8.862, 10.85, "S", zo, n=2)
    bunk_bed("OG", 6.22, 7.17, 8.90, 10.96, "E", zo)
    bunk_bed("OG", 8.13, 9.07, 8.90, 10.96, "W", zo)
    bed("OG", 9.86, 10.78, 8.862, 10.92, "S", zo)
    bed("OG", 10.80, 11.72, 8.862, 10.92, "S", zo)
    nightstand("OG", 9.36, 9.84, 8.865, 9.25, zo)
    nightstand("OG", 11.74, 12.23, 8.865, 9.25, zo)
    cabinet("OG", 13.95, 14.573, 10.95, 12.483, "W", (10.95, 11.44, 11.96, 12.483), zo)
    cabinet("OG", 2.712, 3.35, 3.52, 6.058, "E", (3.52, 4.03, 4.54, 5.0, 5.53, 6.058), zo)
    bed("OG", 3.37, 5.438, 1.01, 2.87, "E", zo, n=2)
    nightstand("OG", 5.02, 5.438, 2.89, 3.37, zo)
    nightstand("OG", 5.02, 5.438, 0.53, 0.99, zo)
    machine("OG", 7.97, 8.588, 4.23, 4.85, zo)
    machine("OG", 7.97, 8.588, 4.23, 4.85, zo + 0.838)                   # dryer on the washer
    machine("OG", 7.97, 8.588, 3.61, 4.21, zo)
    desk.desk("OG", 5.592, 8.588, 2.792, 3.592, zo)                     # full width of the back wall
    folded_stack("OG", 6.45, 3.20, zo + 0.75, ("Jeans", "Jeans", "Wolle", "Bettwaesche", "Creme", "Leinen"))
    folded_stack("OG", 7.15, 3.20, zo + 0.75, ("Bettwaesche", "Creme", "Bettwaesche", "Leinen", "Bettwaesche"))
    basket_cupboard("OG", 5.59, 6.19, 3.612, 5.95, zo)                  # right wall from the door
    bed("OG", 11.63, 13.69, 1.57, 3.43, "W", zo, n=2)
    nightstand("OG", 11.65, 12.02, 3.45, 3.94, zo)
    nightstand("OG", 11.65, 12.02, 1.08, 1.55, zo)
    cabinet("OG", 11.84, 14.348, 5.38, 6.058, "S", (11.84, 12.86, 13.34, 13.85, 14.348), zo)
    sitzecke()
    # Stube sofa: 3/4 of the way from the corner pier between the big windows (room corner) to the
    # Ofen block's room corner (bed included), facing the pier
    (sx, sy), (ox, oy) = (14.351, 0.415), (10.96, 4.64)
    sofa("EG", sx + 0.75 * (ox - sx), sy + 0.75 * (oy - sy), math.degrees(math.atan2(sy - oy, sx - ox)))


# ---------------------------------------------------------------- room names on the floor
# (name, floor, x, y, rotation in degrees so it reads correctly from the room's door)
ROOM_NAMES = [
    ("Stube", "EG", 12.5, 2.3, 180), ("Küche", "EG", 7.0, 4.4, 180), ("Speis", "EG", 3.9, 4.79, 90),
    ("Bibliothek", "EG", 12.9, 10.7, 0), ("Oma & Opa", "EG", 4.3, 10.8, 0),
    ("Nadine & Till", "OG", 11.5, 3.2, 180), ("Waschküche", "OG", 7.1, 4.4, 180),
    ("Saschi", "OG", 4.1, 3.2, 180), ("Bichlach", "OG", 11.9, 10.6, 0), ("Jugend", "OG", 7.6, 10.6, 0),
    ("Yoga", "OG", 3.2, 10.6, 0),
]

# warm fill lights inside the rooms (film.py; dusk in the viewer)
ROOM_LIGHTS = [  # (x, y, floor z)
    (13.5, 7.5, 0), (5.0, 7.4, 0), (10.0, 7.0, 0), (11.7, 3.2, 0), (7.0, 4.5, 0), (5.5, 1.8, 0),
    (13.0, 10.7, 0), (10.2, 10.7, 0), (4.3, 10.7, 0), (7.6, 10.7, 0), (1.3, 11.3, 0),
    (1.3, 7.5, 0), (4.0, 4.79, 0),                  # (4.0, 4.79): Speis, over the aisle
    (5.0, 7.4, Z_OG), (10.0, 7.0, Z_OG), (12.0, 3.0, Z_OG), (4.0, 3.0, Z_OG), (7.0, 4.3, Z_OG),
    (7.0, 1.5, Z_OG), (3.0, 10.7, Z_OG), (7.6, 10.7, Z_OG), (11.8, 10.7, Z_OG), (1.4, 7.4, Z_OG),
]
ROOM_LIGHT_H = 2.1          # light height above its floor


# ---------------------------------------------------------------- shutter cross boards
def build_cross_boards():
    """Two white boards across every shutter (one shutter = one Part of *_Laeden), on both
    faces because the outer side is not recorded per shutter. Each board keeps its shutter's
    rnd, so no random draw is needed and nothing built before shifts."""
    for c in ("EG", "OG"):
        key = (c, c + "_Laeden")
        g = GEO.get(key)
        if not g:
            continue
        for first, n in PARTS[key]:
            pts = [g["v"][i] for f in g["f"][first:first + n] for i in f]
            x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
            y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
            z0, z1 = min(p[2] for p in pts), max(p[2] for p in pts)
            r, h = g["r"][first], z1 - z0
            for zc in (z0 + 0.18 * h, z1 - 0.18 * h):
                bz0, bz1 = zc - 0.05, zc + 0.05
                if (x1 - x0) < (y1 - y0):            # shutter lies in a YZ plane (east/west wall)
                    boxes = [(a, b, y0, y1) for a, b in ((x0 - 0.012, x0), (x1, x1 + 0.012))]
                else:
                    boxes = [(x0, x1, a, b) for a, b in ((y0 - 0.012, y0), (y1, y1 + 0.012))]
                for bx0, bx1, by0, by1 in boxes:          # per storey, so a cutaway can hide the OG
                    o = "Laeden_Querbretter" if c == "EG" else "OG_Laeden_Querbretter"
                    box(c, o, "Rahmen", bx0, bx1, by0, by1, bz0, bz1, r)


# ---------------------------------------------------------------- garden layout
# Shared by garden.py (Blender: Geometry Nodes scatter, leafy shrubs) and the web viewer.
GROUND = (-20, 35, -25, 35, -0.05)          # Gelaende: x0, x1, y0, y1, top
CELL = 0.25                                 # emitter grid
DENSITY = 90                                # grass clumps per m² close to the house
NEAR, FAR, FAR_DENS = 14.0, 28.0, 0.15      # density falls off from NEAR to FAR (relative)
HOUSE_C = (7.44, 6.44)
NO_GRASS = ["EG_Waende", "Terrasse", "Kiesstreifen", "Beet_Ost", "Beet_West", "Dach_Anbau",
            "Balkon_EG_Nord"]
BEDS = ("Beet_Ost", "Beet_West")
WINDROSE_CENTER = (-3.5, -5.0, 0.02)        # compass rose south-west of the house (windrose.py)
WINDROSE_R = 3.0                            # length of its main points
WR_LABEL_HALF = 0.6                         # approx. half size of a letter N/O/S/W at R + 0.9


@dataclass
class GardenLayout:
    ground: tuple
    no_grass: list     # (x0, x1, y0, y1) around house parts
    windrose: list     # (x0, x1, y0, y1): star + 4 letters; Blender keeps grass off, the viewer not
    clump: dict        # one grass clump: "v", "f", "h" (0 root .. 1 tip per vertex)
    shrubs: list       # (x, y, r, h) per shrub


def density(x, y):
    """Relative grass density: 1 near the house, FAR_DENS beyond FAR."""
    r = math.dist((x, y), HOUSE_C)
    t = min(max((r - NEAR) / (FAR - NEAR), 0), 1)
    return 1 - (1 - FAR_DENS) * t


def object_bbox(name):
    pts = [p for (c, o), g in GEO.items() if o == name for p in g["v"]]
    return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))


def grass_clump(rng):
    """One clump: 6 curved, tapering blades 0.3-0.6 m. h = 0 root .. 1 tip."""
    v, f, hs = [], [], []
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi)
        ca, sa = math.cos(a), math.sin(a)
        ox, oy = rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04)
        H, w, bend = rng.uniform(0.3, 0.6), rng.uniform(0.004, 0.007), rng.uniform(0.05, 0.2)
        n = len(v)
        for i in range(4):
            t = i / 3
            d, z, hw = bend * t * t, H * t * (1 - 0.15 * t * t), w * (1 - t) + 0.0005
            px, py = ox + ca * d, oy + sa * d
            v += [(px - sa * hw, py + ca * hw, z), (px + sa * hw, py - ca * hw, z)]
            hs += [t, t]
        f += [(n + 2 * i, n + 2 * i + 1, n + 2 * i + 3, n + 2 * i + 2) for i in range(3)]
    return {"v": v, "f": f, "h": hs}


def plant_beds(rng):
    """Shrubs along the middle of each bed, in groups of three with a gap (like the photo)."""
    shrubs = []
    for bed in BEDS:
        x0, x1, y0, y1 = object_bbox(bed)
        rmax = (x1 - x0) / 2 - 0.02
        y, k = y0 + 0.32, 0
        while y < y1 - 0.25:
            if k % 4 != 3:
                r = rng.uniform(0.85, 1.0) * rmax
                x = (x0 + x1) / 2 + rng.uniform(-0.03, 0.03)
                shrubs.append((x, y, r, rng.uniform(0.42, 0.52)))
            y += rng.uniform(0.58, 0.66)
            k += 1
    return shrubs


def garden_layout():
    m = 0.05
    no_grass = [(x0 - m, x1 + m, y0 - m, y1 + m) for x0, x1, y0, y1 in map(object_bbox, NO_GRASS)]
    cx, cy, _ = WINDROSE_CENTER
    R, d, s = WINDROSE_R, WINDROSE_R + 0.9, WR_LABEL_HALF
    windrose = [(cx - R - m, cx + R + m, cy - R - m, cy + R + m)]
    for lx, ly in ((cx, cy + d), (cx + d, cy), (cx, cy - d), (cx - d, cy)):     # N, O, S, W
        windrose.append((lx - s - m, lx + s + m, ly - s - m, ly + s + m))
    return GardenLayout(GROUND, no_grass, windrose, grass_clump(random.Random(5)),
                        plant_beds(random.Random(6)))


@dataclass
class Blueprint:
    geo: dict          # (collection, object) -> {"v", "f", "m", "r"}
    parts: dict        # (collection, object) -> [(first_face, n_faces), ...]  one per add()
    smooth: set
    pivot: dict
    mat_def: dict
    paint: dict
    room_lights: list
    garden: GardenLayout
    furniture: set     # objects shown only in the viewer's last stage "Eingerichtet"
    dims: list = ()    # dimension lines [(p0, p1, text)] (Ofen sub-model only)
    outside_lights: list = ()   # OUTSIDE_LIGHTS: the wall lamps' filament centres
    lamp_lights: list = ()      # LAMP_LIGHTS: switched-on lamps inside
    fires: list = ()   # FIRES: base (centre of the flame bed, in the flame plane), u (unit along
                       # the width, normal = (-u_y, u_x) towards the viewer), w, h, d
    turn: dict = None  # TURN: object -> degrees about its pivot (None: no turned object)
    slide: dict = None  # SLIDE: object -> (dx, dy, dz) to its other end of travel (None: none)


def build():
    """Run every builder (same order and seed as always) and return the Blueprint."""
    GEO.clear(); PARTS.clear()
    OPENINGS.clear(); GABLE_WIN.clear(); PIVOT.clear(); TURN.clear(); SLIDE.clear(); SMOOTH.clear(); LEAVES.clear()
    OUTSIDE_LIGHTS.clear(); LAMP_LIGHTS.clear(); FIRES.clear()
    random.seed(22)
    build_eg(); build_og(); build_slabs(); build_roof(); build_outside(); build_sanitary()
    build_cladding()
    build_cross_boards()
    build_furniture()
    return Blueprint({k: dict(g) for k, g in GEO.items()}, dict(PARTS), set(SMOOTH), dict(PIVOT),
                     MAT_DEF, PAINT, ROOM_LIGHTS, garden_layout(), set(FURNITURE),
                     outside_lights=list(OUTSIDE_LIGHTS), lamp_lights=list(LAMP_LIGHTS), fires=list(FIRES),
                     turn=dict(TURN), slide=dict(SLIDE))


def build_ofen():
    """The Ofen sub-model alone (web/ofen.html): no house, no garden, plus its dimension lines."""
    GEO.clear(); PARTS.clear(); FIRES.clear(); SMOOTH.clear(); LAMP_LIGHTS.clear()
    random.seed(22)
    dims = ofen.ofen_neu()
    return Blueprint({k: dict(g) for k, g in GEO.items()}, dict(PARTS), set(SMOOTH), {}, MAT_DEF, PAINT,
                     [], None, set(), dims, fires=list(FIRES), lamp_lights=list(LAMP_LIGHTS))


def build_desk():
    """The desk sub-model alone (web/desk.html): desk, devices and chair at the origin, plus its
    dimension lines."""
    GEO.clear(); PARTS.clear(); FIRES.clear(); SMOOTH.clear(); LAMP_LIGHTS.clear(); PIVOT.clear(); TURN.clear(); SLIDE.clear()
    random.seed(22)
    dims = desk.desk_neu()
    desk.stuhl("Desk", 0.0, 0.0)
    return Blueprint({k: dict(g) for k, g in GEO.items()}, dict(PARTS), set(SMOOTH), dict(PIVOT), MAT_DEF, PAINT,
                     [], None, set(), dims, turn=dict(TURN))


def build_kueche():
    """The Küche sub-model alone (web/kueche.html): its furnishings and the flue box at the origin
    (the room's inner NW corner), plus its dimension lines."""
    GEO.clear(); PARTS.clear(); FIRES.clear(); SMOOTH.clear(); LAMP_LIGHTS.clear(); PIVOT.clear(); TURN.clear(); SLIDE.clear()
    LEAVES.clear()
    random.seed(22)
    dims = kueche.kueche_neu()
    return Blueprint({k: dict(g) for k, g in GEO.items()}, dict(PARTS), set(SMOOTH), {}, MAT_DEF, PAINT,
                     [], None, set(), dims, fires=list(FIRES))


def build_bad():
    """The Bad Großeltern sub-model alone (web/bad.html): the room's fixtures, niche and its own
    walls at the origin (the room's inner SW corner), plus its dimension lines."""
    GEO.clear(); PARTS.clear(); FIRES.clear(); SMOOTH.clear(); LAMP_LIGHTS.clear(); PIVOT.clear(); TURN.clear(); SLIDE.clear()
    LEAVES.clear()
    random.seed(22)
    dims = bad.bad_neu()
    return Blueprint({k: dict(g) for k, g in GEO.items()}, dict(PARTS), set(SMOOTH), {}, MAT_DEF, PAINT,
                     [], None, set(), dims, slide=dict(SLIDE))
