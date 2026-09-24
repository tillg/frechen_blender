"""Frechenlehen – Blender model generated from the ALLPLAN PDFs (Grundriss EG/OG, Ansichten, 1:100).

Coordinates in metres: origin = outer SW corner of the main house, +X = east, +Y = north, Z = up.
EG wall segments come from the vector data of "Grundriss Frechenlehen EG.pdf" (gray wall fills);
OG walls and all heights were measured from the plans/elevations (approx. +-5 cm).
Details (doors, balconies, cladding, terrace, lamps, eaves) follow the photos in input/.

Run inside Blender (e.g. via the Blender MCP server):  exec(open(".../code/build_house.py").read())
Re-running replaces the "Haus" collection.
"""
import bpy, math, os, random
from mathutils import Vector

PROJECT = "/Users/tgartner/git/frechen_blender"

W_OUT, D_OUT = 14.885, 12.887           # outer footprint of main house
RIDGE_Y, RIDGE_Z = D_OUT / 2, 7.67      # ridge runs east-west (elevations: 7.65-7.69)
SLOPE, ROOF_T = 0.3635, 0.10            # ~20 deg pitch; thin eave edge as drawn
EAVE_OH, GABLE_OH = 1.34, 1.49          # overhang at eaves (N/S) and gables (E/W), measured
Z_EG_TOP, Z_OG, Z_OG_TOP, Z_ATTIC = 2.40, 2.70, 4.90, 5.10
DOOR_H = 2.0                            # interior door height
SOFFIT = 0.02                           # board layer under the roof
SHED_TOP = 2.53                         # shed roof top where it meets the house


def roof_top(y):
    return RIDGE_Z - SLOPE * abs(y - RIDGE_Y)


def roof_under(y):
    return roof_top(y) - ROOF_T


# ---------------------------------------------------------------- materials
# rgba: plain colour. wood: (dark, light, grain axis) – procedural grain in object space.
# speck: (c1, c2, scale) – speckled stone. bump: (scale, strength). "rnd" face attribute
# (one random value per part) varies brightness so boards and slabs read as single pieces.
WOOD_OLD = ((0.045, 0.032, 0.024), (0.17, 0.12, 0.085))       # weathered balcony / shed
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
    "Glas":       dict(rgba=(0.70, 0.85, 0.95, 0.25), alpha=0.25, rough=0.1),
    "Milchglas":  dict(rgba=(0.90, 0.90, 0.88, 0.85), alpha=0.85, rough=0.4),
    "Wiese":      dict(speck=((0.05, 0.12, 0.025), (0.12, 0.20, 0.04), 3)),
    "Kachel":     dict(rgba=(0.35, 0.47, 0.42, 1), rough=0.35),               # glazed; colour: paint.py
    "Schiefer":   dict(speck=((0.06, 0.065, 0.07), (0.20, 0.21, 0.22), 12), hue=0.03),
    "Feuer":      dict(rgba=(1.0, 0.22, 0.02, 1), emit=1.2),
    "Kies":       dict(speck=((0.30, 0.28, 0.25), (0.62, 0.60, 0.56), 150), bump=(150, 0.5)),
    "Erde":       dict(speck=((0.025, 0.014, 0.008), (0.07, 0.04, 0.022), 60), bump=(60, 0.6)),
    "Granit":     dict(speck=((0.30, 0.29, 0.26), (0.62, 0.58, 0.50), 220), hue=0.06),
    "Fuge":       dict(rgba=(0.16, 0.16, 0.15, 1)),
    "Kiesel":     dict(rgba=(0.52, 0.50, 0.46, 1), rough=0.5),
    "Schrift":    dict(rgba=(0.80, 0.76, 0.66, 1), rough=0.6),               # cream, reads on oak
    "Keramik":    dict(rgba=(0.90, 0.90, 0.88, 1), rough=0.08),
    "Spiegel":    dict(rgba=(0.92, 0.92, 0.92, 1), metal=1.0, rough=0.02),
    "Eisen":      dict(rgba=(0.018, 0.018, 0.02, 1), metal=0.4, rough=0.45),
    "Metall":     dict(rgba=(0.60, 0.60, 0.62, 1), metal=1.0, rough=0.3),
    "Gitter":     dict(rgba=(0.72, 0.67, 0.55, 1), rough=0.6),
    "Emaille":    dict(rgba=(0.86, 0.86, 0.84, 1), rough=0.2),
    "Gluehfaden": dict(rgba=(1.0, 0.55, 0.2, 1), emit=25.0),
}
MAT = {}


def make_materials():
    for name, d in MAT_DEF.items():
        m = bpy.data.materials.get("FL_" + name) or bpy.data.materials.new("FL_" + name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        N = nt.nodes.new
        L = nt.links.new
        out = N("ShaderNodeOutputMaterial")
        bsdf = N("ShaderNodeBsdfPrincipled")
        bsdf.name = "Principled BSDF"
        L(bsdf.outputs["BSDF"], out.inputs["Surface"])
        rgba = d.get("rgba") or (*[(a + b) / 2 for a, b in zip(*(d.get("wood") or d["speck"])[:2])], 1)
        m.diffuse_color = rgba
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = d.get("rough", 0.8)
        bsdf.inputs["Metallic"].default_value = d.get("metal", 0.0)
        if "alpha" in d:
            bsdf.inputs["Alpha"].default_value = d["alpha"]
            m.surface_render_method = "BLENDED"
        if "emit" in d:
            bsdf.inputs["Emission Color"].default_value = rgba
            bsdf.inputs["Emission Strength"].default_value = d["emit"]
        coord = N("ShaderNodeTexCoord")
        height = None
        if "wood" in d or "speck" in d:
            c1, c2 = (d.get("wood") or d["speck"])[:2]
            mp = N("ShaderNodeMapping")
            if "wood" in d:
                ax = d["wood"][2]
                mp.inputs["Scale"].default_value = [1.5 if a == ax else 60.0 for a in "xyz"]
            else:
                mp.inputs["Scale"].default_value = [d["speck"][2]] * 3
            noise = N("ShaderNodeTexNoise")
            noise.inputs["Detail"].default_value = 6
            noise.inputs["Roughness"].default_value = 0.6
            ramp = N("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = 0.35, 0.68
            ramp.color_ramp.elements[0].color = (*c1, 1)
            ramp.color_ramp.elements[1].color = (*c2, 1)
            attr = N("ShaderNodeAttribute"); attr.attribute_name = "rnd"
            val = N("ShaderNodeMath"); val.operation = "MULTIPLY_ADD"
            val.inputs[1].default_value, val.inputs[2].default_value = 0.5, 0.75
            hue = N("ShaderNodeMath"); hue.operation = "MULTIPLY_ADD"
            hue.inputs[1].default_value = d.get("hue", 0.0)
            hue.inputs[2].default_value = 0.5 - d.get("hue", 0.0) / 2
            hs = N("ShaderNodeHueSaturation")
            L(coord.outputs["Object"], mp.inputs["Vector"])
            L(mp.outputs["Vector"], noise.inputs["Vector"])
            L(noise.outputs["Fac"], ramp.inputs["Fac"])
            L(ramp.outputs["Color"], hs.inputs["Color"])
            L(attr.outputs["Fac"], val.inputs[0]); L(val.outputs[0], hs.inputs["Value"])
            L(attr.outputs["Fac"], hue.inputs[0]); L(hue.outputs[0], hs.inputs["Hue"])
            L(hs.outputs["Color"], bsdf.inputs["Base Color"])
            if "wood" in d:
                height, strength = noise.outputs["Fac"], 0.15
        if "bump" in d:
            bn = N("ShaderNodeTexNoise")
            bn.inputs["Scale"].default_value = d["bump"][0]
            bn.inputs["Detail"].default_value = 8
            L(coord.outputs["Object"], bn.inputs["Vector"])
            height, strength = bn.outputs["Fac"], d["bump"][1]
        if height:
            bump = N("ShaderNodeBump")
            bump.inputs["Strength"].default_value = strength
            bump.inputs["Distance"].default_value = 0.01
            L(height, bump.inputs["Height"])
            L(bump.outputs["Normal"], bsdf.inputs["Normal"])
        MAT[name] = m


# ---------------------------------------------------------------- geometry accumulator
GEO = {}      # (collection, object) -> {"v": [...], "f": [...], "m": [...], "r": [...]}
SMOOTH = set()  # objects shaded smooth
PIVOT = {}    # object -> origin (for parts that get animated, e.g. the entrance door)
OPENINGS = []  # exterior wall openings, used by the west cladding
LEAVES = []    # opened interior door leaves (collection, [corner, corner]) – for clash checks
GABLE_WIN = []


def add(coll, obj, mat, verts, faces, rnd=None):
    g = GEO.setdefault((coll, obj), {"v": [], "f": [], "m": [], "r": []})
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
    kind: W window, FD french door, GD glazed terrace door (larch, 4x2 panes per leaf),
          D solid door, I opening without fill (filled by a dedicated door builder).
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
            n = 2 if b - a > 0.75 else 1
            rows = 3 if head - sill > 1.6 else 2
            sw, sf, gb = (b - a - 2 * fw) / n, 0.05, 0.03
            za, zb = sill + fw, head - fw
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


def interior(coll, x0, x1, y0, y1, doors=(), z0=0.0, z1=Z_EG_TOP, head=DOOR_H):
    """doors: (a, b) = open passage, or (a, b, swing, hinge[, flat]) = opening with an opened
    door leaf; swing +1/-1 = room side along the thin axis, hinge "a"/"b" = which jamb carries
    the leaf, flat=False: leaf at 90 deg instead of against the wall (see panel_door)."""
    wall(coll, x0, x1, y0, y1, z0, z1, [(d[0], d[1], z0, z0 + head, "I") for d in doors])
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
        (3.831, 4.730, 1.03, 2.0, "W", 1), (6.618, 7.917, 1.03, 2.0, "W", 1),
        (9.785, 13.741, 0, 2.2, "GD")], out=-1)
    wall(c, 14.575, W_OUT, 6.349, 12.473, z0, z1, [
        (6.458, 7.507, 0, 2.2, "I"), (8.007, 8.476, 1.2, 2.1, "W"),
        (10.315, 11.214, 1.0, 2.0, "W", 1)], out=+1)
    wall(c, 14.351, W_OUT, 0.415, 6.349, z0, z1, [(1.254, 4.880, 0, 2.2, "GD")], out=+1)
    wall(c, 0, 0.31, 5.145, 12.473, z0, z1, [
        (5.724, 6.324, 1.57, 2.17, "W"), (7.408, 8.377, 0, 2.3, "I"),
        (9.12, 9.69, 1.57, 2.17, "W")], out=-1)      # WC Großeltern ("Fenster wird verschoben")
    wall(c, 0.31, 2.358, 5.145, 5.475, z0, z1)              # WC south (towards Schuppen)
    wall(c, 2.358, 2.772, 0.415, 5.849, z0, z1)             # west wall Speis/Essen
    entrance_door(); back_door()
    # interior walls; doors: (a, b, swing, hinge) get an opened leaf, (a, b) stay open passages
    interior(c, 6.024, 6.174, 8.876, 12.473)
    interior(c, 2.657, 14.575, 8.576, 8.876,
             [(4.406, 5.335, 1, "a"), (7.333, 8.282, 1, "a"), (13.517, 14.575, 1, "a")])
    # 9.78-10.72 is pink-hatched wall in the plan (closed up), not an opening – it sat behind the stair
    interior(c, 0.31, 2.358, 8.506, 8.656)              # Flur / WC Großeltern: door closed up (plan)
    interior(c, 0.31, 2.358, 6.574, 6.723, [(1.419, 2.218, -1, "a")])
    # Großeltern: WC door from the bedroom; the Bad is open to the bedroom (unhatched in the plan)
    interior(c, 2.358, 2.657, 6.349, 12.473, [(7.408, 8.506, -1, "a", False), (9.02, 9.90, 1, "b", False),
                                              (10.33, 12.33)])
    interior(c, 2.358, 10.804, 5.849, 6.349, [(7.045, 7.944, -1, "a")])   # Küche door
    stube_niche()                                                         # 10.804 .. 12.003
    interior(c, 12.003, 14.351, 5.849, 6.349)
    interior(c, 8.557, 9.056, 0.415, 5.849, [(0.54, 2.938)])
    interior(c, 5.240, 5.490, 3.002, 5.849, [(3.631, 4.580, -1, "b")])
    interior(c, 9.051, 9.351, 8.876, 9.585)                 # offener Kamin – wall ends
    interior(c, 9.051, 9.351, 12.213, 12.473)
    interior(c, 0.31, 2.358, 10.10, 10.25)                  # new: WC (south) / Bad (north) Großeltern
    interior(c, 11.13, 11.28, 8.876, 12.473, [(9.6, 11.9)])  # new: Musikraum / Büro
    interior(c, 2.772, 5.240, 3.13, 3.29)                   # new: Speis / Essen
    interior(c, 12.25, 12.38, 6.349, 8.576, [(6.5, 8.45, 1, "ab", False, "glazed")])  # Windfang
    kachelofen()
    build_stairs()
    for x0, x1 in ((4.26, 6.05), (6.05, 7.85)):             # dining table (plan: two joined tables)
        table("EG", x0 + 0.002, x1 - 0.002, 1.18, 1.91)
    for x in (4.58, 5.15, 5.73, 6.39, 6.95, 7.53):          # 14 chairs as in the plan
        chair("EG", x, 2.12, 0, -1)
        chair("EG", x, 0.97, 0, 1)
    chair("EG", 4.05, 1.545, 1, 0)
    chair("EG", 8.06, 1.545, -1, 0)


# ---------------------------------------------------------------- Kachelofen
def tiles_on(o, P, u0, u1, z0, z1, face, out, tw=0.20, th=0.24):
    """Panel tiles (with a raised field) on a face at t = face, facing direction out (+1/-1)."""
    nu, nz = max(1, round((u1 - u0) / tw)), max(1, round((z1 - z0) / th))
    for i in range(nu):
        for j in range(nz):
            ua, ub = u0 + (u1 - u0) * i / nu + 0.002, u0 + (u1 - u0) * (i + 1) / nu - 0.002
            za, zb = z0 + (z1 - z0) * j / nz + 0.002, z0 + (z1 - z0) * (j + 1) / nz - 0.002
            r = random.random()
            lbox("EG", o, "Kachel", P, ua, ub, face, face + out * 0.015, za, zb, r)
            lbox("EG", o, "Kachel", P, ua + 0.03, ub - 0.03, face + out * 0.015, face + out * 0.022,
                 za + 0.03, zb - 0.03, r)


def cornice(o, x0, x1, y0, y1, z, sides):
    """Stepped tile ledge round a block (sides that face the room: S, E)."""
    for dz, pr in ((0.0, 0.03), (0.04, 0.06)):
        box("EG", o, "Kachel", x0, x1 + (pr if "E" in sides else 0), y0 - (pr if "S" in sides else 0), y1,
            z + dz, z + dz + 0.04)


def kachelofen():
    """Tiled stove in the Stube after ofen_stuben.jpg, tiles in the shutter blue (RAL 5014, set
    in paint.py): white plaster body with firebox, tiled corner column and upper tier, tile
    ledges, wooden stove bench with an arched opening and round tiles, slate hearth.
    Body = plan footprint; the bench runs south along the west wall (east would block the
    Stube door)."""
    o, x0, x1, y0, y1 = "EG_Kachelofen", 9.06, 10.56, 4.34, 5.849
    PX, PY = frame("x"), frame("y")
    box("EG", o, "Putz", x0, x1, y0, y1, 0.02, 1.22)                          # body
    fx0, fx1 = 9.35, 9.90                                                      # firebox (south)
    for ua, ub, za, zb in ((fx0 - 0.05, fx0, 0.30, 1.05), (fx1, fx1 + 0.05, 0.30, 1.05),
                           (fx0, fx1, 0.30, 0.36), (fx0, fx1, 0.99, 1.05)):          # black frame
        lbox("EG", o, "Eisen", PX, ua, ub, y0 - 0.03, y0, za, zb)
    lbox("EG", o, "Feuer", PX, fx0, fx1, y0 - 0.005, y0 - 0.0, 0.36, 0.99)
    lbox("EG", o, "Eisen", PX, fx1 - 0.06, fx1 - 0.04, y0 - 0.06, y0 - 0.025, 0.55, 0.85)   # handle
    tx0, ty1 = 10.16, 4.74                                                     # tiled corner column
    box("EG", o, "Putz", tx0, x1, y0, ty1, 0.02, 1.22)
    tiles_on(o, PX, tx0, x1, 0.04, 1.20, y0, -1)
    tiles_on(o, PY, y0, ty1, 0.04, 1.20, x1, 1)
    cornice(o, x0, x1, y0, y1, 1.22, "SE")
    uy0 = 4.90                                                                 # upper tier (back half)
    box("EG", o, "Putz", x0, x1, uy0, y1, 1.30, 1.80)
    tiles_on(o, PX, x0 + 0.02, x1, 1.32, 1.78, uy0, -1, th=0.23)
    tiles_on(o, PY, uy0, y1, 1.32, 1.78, x1, 1, th=0.23)
    cornice(o, x0, x1, uy0, y1, 1.80, "SE")
    box("EG", o, "Putz", x0, 10.20, 5.25, y1, 1.88, 2.08)                     # top step
    cornice(o, x0, 10.20, 5.25, y1, 2.08, "SE")
    # stove bench along the west wall, warm back wall with round tiles
    bx0, bx1, by0 = 9.06, 9.66, 3.0
    arc = [(3.35 + 0.30 * (1 - math.cos(math.pi * i / 16)), 0.30 * math.sin(math.pi * i / 16) + 0.05)
           for i in range(17)]                                                 # opening under the bench
    box("EG", o, "Putz", bx0, bx1, by0, 3.35, 0.02, 0.42)
    box("EG", o, "Putz", bx0, bx1, 3.95, y0, 0.02, 0.42)
    sweep("EG", o, "Putz", PY, [((u, z), (u, 0.42)) for u, z in arc], bx0, bx1)
    box("EG", o, "Putz", bx0, bx1, 3.35, 3.95, 0.02, 0.05)
    box("EG", o, "Eiche", bx0, bx1 + 0.04, by0, y0, 0.42, 0.47)                 # seat
    box("EG", o, "Putz", bx0, 9.26, by0, y0, 0.47, 1.22)                        # back
    cornice(o, bx0, 9.26, by0, y0, 1.22, "E")
    k = 16
    for yc in (3.35, 3.8, 4.2):
        for r, t in ((0.09, 0.02), (0.06, 0.035)):                             # round bowl tiles
            v = [(9.26 + dt, yc + r * math.cos(2 * math.pi * i / k), 0.85 + r * math.sin(2 * math.pi * i / k))
                 for dt in (0.0, t) for i in range(k)]
            f = [list(range(k))[::-1], list(range(k, 2 * k))]
            f += [(i, (i + 1) % k, k + (i + 1) % k, k + i) for i in range(k)]
            add("EG", o, "Kachel", v, f)
    # slate hearth in front of body and bench
    for xa, xb, ya, yb in ((bx1 + 0.04, x1 + 0.45, 3.5, y0), (x1, x1 + 0.45, y0, y1)):
        tiles("EG", o, "Schiefer", xa, xb, ya, yb, 0.012, 0.022, [0.45, 0.4], (0.4, 0.7), 0.006)


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
    """Wall-hung toilet with a chrome flush plate."""
    o, M = coll + "_Sanitaer", at_wall(wx, wy, fx, fy)
    xy_prism(coll, o, "Keramik", rounded(M, 0.30, 0.46, 0.04), z + 0.22, z + 0.30)
    xy_prism(coll, o, "Keramik", rounded(M, 0.36, 0.55), z + 0.30, z + 0.40)
    xy_prism(coll, o, "Keramik", rounded(M, 0.37, 0.56, 0.02), z + 0.40, z + 0.425)       # seat
    (xa, ya), (xb, yb) = M(-0.12, 0.0), M(0.12, 0.012)
    box(coll, o, "Metall", xa, xb, ya, yb, z + 0.98, z + 1.14)


def basin(coll, wx, wy, fx, fy, w=0.60, d=0.46, z=0.0, mirror=True):
    """Washbasin (rounded front) with tap and a mirror above."""
    o, M = coll + "_Sanitaer", at_wall(wx, wy, fx, fy)
    xy_prism(coll, o, "Keramik", rounded(M, w * 0.7, d * 0.8), z + 0.66, z + 0.80)
    xy_prism(coll, o, "Keramik", rounded(M, w, d), z + 0.80, z + 0.86)
    xy_prism(coll, o, "Metall", [M(-0.02, 0.03), M(0.02, 0.03), M(0.02, 0.14), M(-0.02, 0.14)], z + 0.86, z + 0.97)
    if mirror:
        (xa, ya), (xb, yb) = M(-w / 2, 0.0), M(w / 2, 0.008)
        box(coll, o, "Spiegel", xa, xb, ya, yb, z + 1.10, z + 1.75)


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


def build_sanitary():
    """Bathrooms and toilets after the fixtures drawn in grundriss_eg/og.png."""
    zo = Z_OG + 0.0
    # EG Bad Großeltern (N): corner shower NW, basin on the west wall
    shower("EG", 0.31, 1.10, 11.66, 12.473, [(1.10, 11.66, 1.10, 12.473), (0.31, 11.66, 0.70, 11.66)],
           (0.70, 12.473, 0, -1))
    basin("EG", 0.31, 11.0, 1, 0)
    # EG WC Großeltern (S): toilet on the south wall, hand basin on the north wall
    toilet("EG", 1.455, 8.656, 0, 1)
    basin("EG", 1.45, 10.10, 0, -1, w=0.40, d=0.28)
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
    basin("OG", 10.0, 5.2, -1, 0, w=0.40, d=0.28, z=zo)


# ---------------------------------------------------------------- furniture
def post(coll, obj, mat, p0, p1, w, rnd=None):
    """Square post of width w from bottom centre p0 to top centre p1 (may lean)."""
    v = [(p[0] + sx * w / 2, p[1] + sy * w / 2, p[2]) for p in (p0, p1)
         for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    add(coll, obj, mat, v, f, rnd)


def table(coll, x0, x1, y0, y1, h=0.76):
    """Inn table after table_shape.png: spruce top on an apron, legs splayed outwards,
    foot rail frame just above the floor."""
    o = coll + "_Tisch"
    box(coll, o, "FichteX", x0, x1, y0, y1, h - 0.04, h)                      # top
    ti, fi, lw = 0.13, 0.06, 0.07                                             # leg inset top / foot
    ax0, ax1, ay0, ay1 = x0 + ti - lw / 2, x1 - ti + lw / 2, y0 + ti - lw / 2, y1 - ti + lw / 2
    za = (h - 0.14, h - 0.04)
    for ya, yb in ((ay0, ay0 + 0.025), (ay1 - 0.025, ay1)):                   # apron
        box(coll, o, "FichteX", ax0, ax1, ya, yb, *za)
    for xa, xb in ((ax0, ax0 + 0.025), (ax1 - 0.025, ax1)):
        box(coll, o, "FichteY", xa, xb, ay0, ay1, *za)
    feet = []
    for sx, sy in ((0, 0), (1, 0), (1, 1), (0, 1)):
        tx, ty = (x1 - ti, x0 + ti)[sx == 0], (y1 - ti, y0 + ti)[sy == 0]
        fx, fy = (x1 - fi, x0 + fi)[sx == 0], (y1 - fi, y0 + fi)[sy == 0]
        post(coll, o, "FichteZ", (fx, fy, 0.012), (tx, ty, h - 0.04), lw)
        feet.append((fx, fy))
    zf = (0.03, 0.09)                                                          # foot rails
    (fx0, fy0), (fx1, fy1) = feet[0], feet[2]
    for y in (fy0, fy1):
        box(coll, o, "FichteX", fx0, fx1, y - 0.02, y + 0.02, *zf)
    for x in (fx0, fx1):
        box(coll, o, "FichteY", x - 0.02, x + 0.02, fy0 + 0.02, fy1 - 0.02, *zf)


def chair(coll, cx, cy, fx, fy):
    """Simple spruce chair centred at (cx, cy), facing the table in direction (fx, fy):
    four legs, seat, rear legs running up into the back posts, two back slats, side stretchers."""
    o, W = coll + "_Stuehle", 0.42

    def part(m, u0, u1, v0, v1, z0, z1):                   # u across, v from front (table) to back
        (xa, ya), (xb, yb) = [(cx + fx * (W / 2 - v) - fy * u, cy + fy * (W / 2 - v) + fx * u)
                              for u, v in ((u0, v0), (u1, v1))]
        if abs(fx) > 0:                                     # grain along the part's long axis
            m = {"FichteX": "FichteY", "FichteY": "FichteX"}.get(m, m)
        box(coll, o, m, xa, xb, ya, yb, z0, z1, r)

    r, l, h = random.random(), 0.035, W / 2
    part("FichteX", -h, h, 0, W, 0.43, 0.46)                                   # seat
    for u in (-h, h - l):
        part("FichteZ", u, u + l, 0.01, 0.01 + l, 0, 0.43)                     # front legs
        part("FichteZ", u, u + l, W - l, W, 0, 0.92)                           # rear legs + posts
        part("FichteY", u, u + l, 0.01 + l, W - l, 0.13, 0.16)                 # side stretchers
    for z in (0.62, 0.80):                                                     # back slats
        part("FichteX", -h + l, h - l, W - 0.03, W - 0.01, z, z + 0.08)


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
    # OG: railing on the slab edge of the stairwell, from where the stair handrail has dropped
    # below the OG floor, and along the east edge
    hx0, hx1, hy0, hy1 = STAIR_HOLE
    zf, o = Z_OG + 0.01, "OG_Gelaender"
    xg = ST_X0 - (zf + 0.10 - hr - ST_RISE) * ST_RUN / ST_RISE
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
        (11.26, 12.23, z0, 4.66, "GD"), (8.96, 9.95, z0, 4.66, "GD"),     # like the Stube doors
        (6.77, 7.76, z0, 4.66, "GD"), (5.72, 6.32, 4.18, 4.78, "W")], out=-1)
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
    interior(c, 0.31, 14.575, 8.57, 8.86,
             [(3.17, 4.15, 1, "a"), (7.28, 8.17, 1, "a"), (12.30, 13.18, 1, "a")], z0, z1, H)
    interior(c, 6.05, 6.21, 8.86, 12.485, (), z0, z1)
    interior(c, 9.08, 9.25, 8.86, 12.485, (), z0, z1)
    interior(c, 2.57, 2.71, 5.46, 8.57, [(7.66, 8.47, -1, "a")], z0, z1, H)
    interior(c, 2.71, 14.35, 6.06, 6.35,
             [(4.02, 4.87, -1, "a"), (7.15, 8.17, -1, "a"), (8.76, 9.65, -1, "b", False),
              (10.66, 11.51, -1, "b")], z0, z1, H)
    interior(c, 0.31, 1.57, 6.44, 6.54, [(0.55, 1.35, -1, "b", False)], z0, z1, H)   # WC 2,26
    interior(c, 1.57, 1.67, 5.46, 6.44, (), z0, z1)
    interior(c, 5.44, 5.59, 0.40, 6.06, (), z0, z1)
    interior(c, 5.59, 8.59, 2.62, 2.79, (), z0, z1)                  # HWR / Bad (new)
    interior(c, 8.59, 8.72, 0.40, 6.06, [(1.65, 2.58, -1, "a")], z0, z1, H)    # Bad door opens inwards (plan)
    interior(c, 10.0, 10.15, 3.84, 6.06, (), z0, z1)                 # WC 2,30 (new)
    interior(c, 8.72, 10.0, 3.84, 3.98, (), z0, z1)


# ---------------------------------------------------------------- west cladding
def build_cladding():
    """The west side takes the weather, so the whole west face (EG, OG, gable and the part
    above the shed) is clad with vertical larch boards, after
    outside_wall_structure_back_of_the_house.png. Openings get board trims; the small windows
    get vertical iron bars."""
    c, o, M, bw, T = "Dach", "Verschalung_West", "Laerche", 0.17, 0.025
    top = lambda y: roof_under(y) - SOFFIT
    # (frame, face coordinate, u range, bottom, openings on that face)
    faces = [
        ("y", 0.0, 5.145, D_OUT, 0.25),        # main west face
        ("y", 2.358, 0.0, 5.12, SHED_TOP),     # above the shed
    ]
    for ax, face, u0, u1, zb in faces:
        P = frame(ax)
        ops = [op for op in OPENINGS if op["ax"] == ax and abs(op["face"] - face) < 0.03
               and u0 - 0.01 <= op["a"] and op["b"] <= u1 + 0.01]
        holes = [(op["a"], op["b"], const(op["sill"]), const(op["head"]), False) for op in ops]
        for x0, ya, yb, zw, woff in GABLE_WIN:
            if abs(x0 - face) < 0.03:
                holes.append((ya, yb, const(zw), (lambda u, w=woff: roof_top(u) - w), False))
                r = random.random()
                for ua, ub in ((ya - 0.09, ya), (yb, yb + 0.09)):
                    column(c, o, M, P, ua, ub, const(zw - 0.09),
                           lambda u, w=woff: roof_top(u) - w + 0.09, face - T - 0.02, face - T, r)
                lbox(c, o, M, P, ya - 0.09, yb + 0.09, face - T - 0.02, face - T, zw - 0.09, zw, r)
                column(c, o, M, P, ya, yb, lambda u, w=woff: roof_top(u) - w,
                       lambda u, w=woff: roof_top(u) - w + 0.09, face - T - 0.02, face - T, r)
        boards(c, o, M, P, u0, u1, const(zb), top, face - T, face, bw, holes, cuts=[RIDGE_Y])
        for op in ops:
            if op["kind"] == "I":                 # the back door has its own heavy frame
                continue
            a, b, s, h = op["a"], op["b"], op["sill"], op["head"]
            tr, r = (face - T - 0.02, face - T), random.random()      # one rnd per trim (see wall)
            lbox(c, o, M, P, a - 0.09, a, *tr, max(s - 0.09, zb), h + 0.09, r)
            lbox(c, o, M, P, b, b + 0.09, *tr, max(s - 0.09, zb), h + 0.09, r)
            lbox(c, o, M, P, a, b, *tr, h, h + 0.09, r)
            if s > zb + 0.1:
                lbox(c, o, M, P, a - 0.09, b + 0.09, face - T - 0.05, face - T, s - 0.06, s, r)
            if op["kind"] == "W":
                n = max(2, int((b - a) / 0.2))
                for k in range(1, n + 1):
                    u = a + (b - a) * k / (n + 1)
                    lbox(c, o, "Eisen", P, u - 0.007, u + 0.007, face + 0.02, face + 0.034, s, h)
    # south-facing return above the shed (closes the gap between shed roof and roof)
    P = frame("x")
    boards(c, o, M, P, -T, 2.358, const(SHED_TOP), const(top(5.12)), 5.12 - T, 5.12, bw)


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
CORRIDOR_OG = [(2.71, 14.575, 6.35, 8.57)]


def tiles(coll, obj, mat, x0, x1, y0, y1, z0, z1, widths, lengths, joint, excl=()):
    """Rows along x (row widths cycling through `widths`), pieces of random length, skipping
    the exclusion rectangles. Rows are split at exclusion edges so pieces never overlap them."""
    y, i = y0, 0
    while y1 - y > 0.02:
        ya, yb = y, min(y + widths[i % len(widths)], y1)
        y, i = yb, i + 1
        cuts = sorted({ya, yb} | {e for r in excl for e in r[2:] if ya < e < yb})
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
                l = sa - random.uniform(0, lengths[1])            # stagger the joints row by row
                while l < sb:
                    la, lb = max(l, sa), min(l + random.uniform(*lengths), sb)
                    l = lb if lb > l else sb
                    if lb - la > 0.01:
                        box(coll, obj, mat, la + joint / 2, lb - joint / 2, ra + joint / 2, rb - joint / 2, z0, z1)


def floor_cover(coll, z, corridors, hole=None):
    """Floors after inside_floor_rooms.jpg (oak planks in all rooms) and
    stone_floor_corridor.jpg (limestone slabs in the corridors); dark base shows in the joints."""
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
    floor_cover("EG", 0.0, CORRIDOR_EG)
    floor_cover("OG", Z_OG, CORRIDOR_OG, STAIR_HOLE)
    slab("Dach", "Decke_OG", "Decke", Z_OG_TOP, Z_ATTIC)


# ---------------------------------------------------------------- roof & gables
def gable(x0, x1, y0, y1, windows=(), woff=0.7):
    c = "Dach"
    zb = Z_OG_TOP
    cuts = sorted(windows)
    edges, cur = [], y0
    for ya, yb, zw in cuts:
        edges.append((cur, ya, None)); edges.append((ya, yb, zw)); cur = yb
        GABLE_WIN.append((x0, ya, yb, zw, woff))
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


def lamp(x, y, z, nx, ny):
    """Gooseneck wall lamp after outdoor_lamp.jpeg: black arm, flat enamel shade (white
    inside), clear bulb with a warm filament."""
    c, o = "Umgebung", "Aussenleuchten"
    sx, sy = -ny, nx
    W = lambda n, s, h: (x + nx * n + sx * s, y + ny * n + sy * s, z + h)
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
    loft([ring(0.38, -0.06, 0.006, 6), ring(0.38, -0.11, 0.006, 6)], "Gluehfaden")


def build_terrace():
    """After terrasse_and_outside_lamps.jpeg: granite slabs of mixed size in rows along the
    wall, a pebble strip against the wall, soil beds for the bushes (garden.py plants them)."""
    c = "Umgebung"
    tw, strip = 4.0, 0.25
    bed_e = (W_OUT, W_OUT + strip + 0.6, 7.9, 12.8)          # east, north of the entrance
    bed_w = (-0.70, -0.025, 8.7, 12.8)                       # west, north of the back door
    door = (6.3, 7.7)                                        # threshold in front of the entrance
    box(c, "Terrasse", "Fuge", 0, W_OUT + tw, -tw, 0, -0.10, -0.025)
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

    slabs("x", -strip, -tw, 0, W_OUT + tw)
    slabs("x", 0, -strip, W_OUT + strip, W_OUT + tw)                  # SE corner, strip row
    slabs("y", W_OUT + strip, bed_e[1], 0, bed_e[2])                  # first row stops at the bed
    slabs("y", bed_e[1], W_OUT + tw, 0, D_OUT)
    box(c, "Terrasse", "Granit", W_OUT, W_OUT + strip, door[0], door[1], -0.05, -0.01)
    # pebble strip (gravel bed + pebbles)
    strips = [(0, W_OUT + strip, -strip, 0), (W_OUT, W_OUT + strip, 0, door[0]),
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
    box(c, "Schuppen", "Kies", 0.10, 2.358, 0.20, 5.145, -0.05, -0.01)
    build_shed()
    box(c, "Gelaende", "Wiese", -20, 35, -25, 35, -0.30, -0.05)
    SMOOTH.update({"Kiesel", "Aussenleuchten"})


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


# ---------------------------------------------------------------- room names on the floor
# (name, floor, x, y, rotation in degrees so it reads correctly from the room's door)
ROOM_NAMES = [
    ("Stube", "EG", 11.9, 2.8, 180), ("Küche", "EG", 7.0, 4.4, 180), ("Speis", "EG", 3.9, 4.4, 90),
    ("Bibliothek", "EG", 12.9, 10.7, 0), ("Oma & Opa", "EG", 4.3, 10.8, 0),
    ("Nadine & Till", "OG", 11.5, 3.2, 180), ("Waschküche", "OG", 7.1, 4.4, 180),
    ("Saschi", "OG", 4.1, 3.2, 180), ("Bichlach", "OG", 11.9, 10.6, 0), ("Jugend", "OG", 7.6, 10.6, 0),
    ("Yoga", "OG", 3.2, 10.6, 0),
]


def build_room_names():
    """Names in cream letters on the floor (text converted to mesh, 0.40 m high)."""
    for coll_name in ("EG", "OG"):
        z = (0.0 if coll_name == "EG" else Z_OG) + 0.0153
        me_all = []
        for name, c, x, y, rot in ROOM_NAMES:
            if c != coll_name:
                continue
            cu = bpy.data.curves.new("tmp_name", "FONT")
            cu.body, cu.size, cu.align_x, cu.align_y, cu.extrude = name, 0.40, "CENTER", "CENTER", 0.0008
            tmp = bpy.data.objects.new("tmp_name", cu)
            tmp.location, tmp.rotation_euler.z = (x, y, z), math.radians(rot)
            bpy.context.scene.collection.objects.link(tmp)
            me_all.append(tmp)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        import bmesh
        bm = bmesh.new()
        for tmp in me_all:
            m = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
            m.transform(tmp.matrix_world)
            bm.from_mesh(m)
            bpy.data.meshes.remove(m)
            cu = tmp.data
            bpy.data.objects.remove(tmp)
            bpy.data.curves.remove(cu)
        me = bpy.data.meshes.new(coll_name + "_Raumnamen")
        bm.to_mesh(me); bm.free()
        me.materials.append(MAT["Schrift"])
        coll(coll_name).objects.link(bpy.data.objects.new(coll_name + "_Raumnamen", me))


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
        piv = PIVOT.get(name, (0, 0, 0))
        me.from_pydata([(x - piv[0], y - piv[1], z - piv[2]) for x, y, z in g["v"]], [], g["f"])
        mats = sorted(set(g["m"]))
        for m in mats:
            me.materials.append(MAT[m])
        me.polygons.foreach_set("material_index", [mats.index(m) for m in g["m"]])
        me.attributes.new("rnd", "FLOAT", "FACE").data.foreach_set("value", g["r"])
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        if name in SMOOTH:
            me.shade_smooth()
        ob = bpy.data.objects.new(name, me)
        ob.location = piv
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
    random.seed(22)
    OPENINGS.clear(); GABLE_WIN.clear(); PIVOT.clear(); SMOOTH.clear(); LEAVES.clear()
    make_materials()
    reset_collections()
    build_eg(); build_og(); build_slabs(); build_roof(); build_outside(); build_sanitary()
    build_cladding()
    flush_geometry()
    build_room_names()
    build_references()
    setup_scene()


main()
