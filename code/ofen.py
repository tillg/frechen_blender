"""Frechenlehen – the stoves: the Ofen sub-model (corner stove with benches and bed, input/2026-11-04 input),
its placement in the Stube, the small workshop stove (werkstattofen.jpeg) and the Wamsler kitchen
cooker (wamsler.jpeg).

Pure Python like house_core.py, which imports this module and calls ofen_im_haus(),
werkstattofen() and wamsler(); house_core.build_ofen() wraps ofen_neu() as the Blueprint of
web/ofen.html.
The primitives and the geometry accumulator come from house_core (attribute access, because the
two modules import each other).
"""
import math, random
import house_core as hc

OFEN_H, OFEN_BED = 1.15, 1.45                              # stove height; bed underside, so one can
                                                           # sit upright on the bench below
OFEN_DOOR_W, OFEN_DOOR_TOP = 0.65, OFEN_H - 0.10           # fire door: centred, 10 cm below the top
OFEN_BANK_D, OFEN_BANK_L = 0.60, 1.60                      # bench depth; length of the left bench
OFEN_BACK = (0.72, 0.48, 0.96)                             # back door (fed from the Flur): centre along
                                                           # the x = 0 face, width, top (sill as the front)
OFEN_AT, WALL_FLUR = (9.06, 5.845), 6.349                  # house: the stove's wall corner; Flur face of
                                                           # the Stube/Flur wall (house_core.build_eg)
OFEN_A = 1.00                                              # #63: a triangle in the corner, legs OFEN_A along both
                                                           # walls, its glass front on the hypotenuse towards the room
                                                           # (#61: 1.20 x 0.50 along the Flur wall; before a corner
                                                           # stove 1.20 x 1.20)
BANK_AT = 1.205                                            # both benches start 1.205 from the corner (as before #63)
OFEN_BED_W = 0.70                                          # the bed: 70 wide, straight (#61)
OLD_DRAWS = 39                                             # global draws of the corner stove in the house (till #61):
                                                           # house_core burns them, so later parts keep their rnd
OFEN_BED_L = 1.90                                          # bed length along the wall (sketches: both
                                                           # 2.00; shortened to fit the Stube, see LOG)
OFEN_ASSUMED = dict(r=0.06, sill=0.40, seat=0.45,          # not given: corner radius (small enough
                    arch=(0.50, 0.30), leg=0.12,           # for the 65 cm door), door sill (above
                    rim=(0.05, 0))                        # the arch), seat height, floor arches
                                                           # width/height, leg thickness, bed rim
                                                           # board width / outward lean in degrees


def filleted(pts, r, at, n=8):
    """Polygon with the vertices `at` replaced by circular fillets of radius r."""
    out = []
    for i, p in enumerate(pts):
        if i not in at:
            out.append(p)
            continue
        a, b = pts[i - 1], pts[(i + 1) % len(pts)]
        u1, u2 = [((q[0] - p[0]) / math.dist(p, q), (q[1] - p[1]) / math.dist(p, q)) for q in (a, b)]
        th = math.acos(u1[0] * u2[0] + u1[1] * u2[1])                         # interior angle
        d, h = r / math.tan(th / 2), r / math.sin(th / 2)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        c = (p[0] + bis[0] / math.hypot(*bis) * h, p[1] + bis[1] / math.hypot(*bis) * h)
        t1, t2 = (p[0] + u1[0] * d, p[1] + u1[1] * d), (p[0] + u2[0] * d, p[1] + u2[1] * d)
        a1, a2 = math.atan2(t1[1] - c[1], t1[0] - c[0]), math.atan2(t2[1] - c[1], t2[0] - c[0])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        out += [(c[0] + r * math.cos(a1 + da * k / n), c[1] + r * math.sin(a1 + da * k / n)) for k in range(n + 1)]
    return out


def ofen_neu():
    """The stove after the sketches in input/2026-11-04 input, since #63 (input/2026-11-28 input/ofen_dreieck_optionen.svg,
    variant B) a triangle in the corner: legs OFEN_A along the Flur wall (x = 0) and the west wall (y = 0), the front on
    the hypotenuse facing the room at 45°, 1.15 m high, its top edge along the front rounded. In the front a 65 cm fire
    door, centred, up to 10 cm below the top, the fire behind the glass (the firebox small as before); an arched opening
    at the floor under it (like ofenbett-1200x800.jpg); underneath it is open and stands on legs beside the arch.
    Benches (like the photo, 60 cm deep) where they stood: beside the stove along the Flur wall and OFEN_BANK_L along
    the west wall, both from BANK_AT. Bed above (\"über dem Ofen\", underside at 1.45 m): straight, OFEN_BED_W wide
    along the Flur wall to OFEN_BED_L, on a post at the free end, with a rim board along its free edge (like the photo).
    Returns the dimension lines [(p0, p1, text)] for the viewer."""
    A, o, a = OFEN_ASSUMED, "Ofen_Feuertuer", OFEN_A
    zp, za, zc, W = OFEN_BED, A["sill"], OFEN_DOOR_TOP, OFEN_DOOR_W / 2
    q2, Lh = math.sqrt(0.5), a * math.sqrt(2)                       # the front: from (0, a) to (a, 0), Lh long
    foot = [(0, 0), (0, a), (a, 0)]
    # fire door and the arch: u along the front (0 at its middle, + towards the Flur wall's end), t outward
    PD = lambda u, t, z: (a / 2 + (t - u) * q2, a / 2 + (t + u) * q2, z)
    # body: open underneath, on two legs (thickness tl behind the front) beside the arch, each running to its wall;
    # the arch head between them; the rest above it
    (aw, ah), tl = A["arch"], A["leg"]
    zr = ah + 0.04
    F = lambda u, t: PD(u, t, 0)[:2]
    for u0, u1 in ((-Lh / 2, -aw / 2), (aw / 2, Lh / 2)):
        w0, w1 = (u0 + tl, u1) if u0 < 0 else (u0, u1 - tl)          # the back edge meets the wall tl further in
        hc.xy_prism("Ofen", "Ofen_Koerper", "Putz", [F(u0, 0), F(u1, 0), F(w1, -tl), F(w0, -tl)], 0.0, zr)
    arc = [(-aw / 2 + aw / 2 * (1 - math.cos(math.pi * i / 16)), ah * math.sin(math.pi * i / 16)) for i in range(17)]
    hc.sweep("Ofen", "Ofen_Koerper", "Putz", PD, [((u, z), (u, zr)) for u, z in arc], -tl, 0.0)   # arch head
    R, H = A["r"], OFEN_H
    hc.xy_prism("Ofen", "Ofen_Koerper", "Putz", foot, zr, H - R)
    # top edge along the front rounded: rings with the front inset by dd (their wall ends slide along the walls)
    rings = []
    for k in range(7):
        t = math.pi / 2 * k / 6
        e = a - R * (1 - math.cos(t)) * math.sqrt(2)
        rings.append([(0, 0, H - R + R * math.sin(t)), (0, e, H - R + R * math.sin(t)), (e, 0, H - R + R * math.sin(t))])
    n = 3
    hc.add("Ofen", "Ofen_Koerper", "Putz", [p for ring in rings for p in ring],
        [list(range(n))[::-1], list(range(6 * n, 7 * n))]
        + [(k * n + i, k * n + (i + 1) % n, (k + 1) * n + (i + 1) % n, (k + 1) * n + i) for k in range(6) for i in range(n)])
    rect = lambda u0, u1, z0, z1: [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
    rf = random.random()
    for q in (rect(-W, -W + 0.04, za, zc), rect(W - 0.04, W, za, zc),
              rect(-W, W, za, za + 0.04), rect(-W, W, zc - 0.04, zc)):
        hc.prism("Ofen", o, "Eisen", PD, q, 0.0, 0.03, rf)                           # iron frame
    ia, ib, iz0, iz1 = -W + 0.04, W - 0.04, za + 0.04, zc - 0.04                    # glass opening
    hc.prism("Ofen", o, "Eisen", PD, rect(ia, ib, iz0, iz1), 0.0, 0.004)              # black firebox back
    for k in range(2):                                                             # two logs
        hc.prism("Ofen", o, "Holz", PD, rect(ia + 0.06 + 0.03 * k, ib - 0.08 + 0.03 * k, iz0 + 0.01 + 0.06 * k,
                                          iz0 + 0.07 + 0.06 * k), 0.006 + 0.004 * k, 0.012 + 0.004 * k)
    hc.FIRES.append(dict(base=PD(0, 0.011, iz0 + 0.07), u=(-q2, q2), w=ib - ia - 0.04, h=0.45, d=0.008,
                         collection="Ofen"))  # flames: fire.py
    hc.prism("Ofen", o, "Ofenglas", PD, rect(ia, ib, iz0, iz1), 0.018, 0.022)
    # back door on the wall side (x = 0, t outward = -x): the same iron frame, glass and a fire;
    # in the house it sits in the Flur face of the wall (ofen_im_haus)
    PB, (bc, bw, bt), ob = (lambda u, t, z: (-t, u, z)), OFEN_BACK, "Ofen_Hintertuer"
    rb = random.random()
    for q in (rect(bc - bw / 2, bc - bw / 2 + 0.04, za, bt), rect(bc + bw / 2 - 0.04, bc + bw / 2, za, bt),
              rect(bc - bw / 2, bc + bw / 2, za, za + 0.04), rect(bc - bw / 2, bc + bw / 2, bt - 0.04, bt)):
        hc.prism("Ofen", ob, "Eisen", PB, q, 0.0, 0.03, rb)
    gb = rect(bc - bw / 2 + 0.04, bc + bw / 2 - 0.04, za + 0.04, bt - 0.04)
    hc.prism("Ofen", ob, "Eisen", PB, gb, 0.0, 0.004)
    hc.FIRES.append(dict(base=PB(bc, 0.011, za + 0.06), u=(0.0, 1.0), w=bw - 0.12, h=bt - za - 0.14, d=0.008,
                         back=True, collection="Ofen"))
    hc.prism("Ofen", ob, "Ofenglas", PB, gb, 0.018, 0.022)
    # benches after bank-schlicht.png: plank seat with a rounded free corner, at each leg station
    # two plain square legs (front, back) joined by a stretcher across the depth
    zs = A["seat"]

    def legs(x, ya, yb):
        for yl in (ya + 0.05, yb - 0.11):
            hc.box("Ofen", "Ofen_Bank", "FichteZ", x, x + 0.06, yl, yl + 0.06, 0.0, zs - 0.045)
        hc.box("Ofen", "Ofen_Bank", "FichteY", x + 0.015, x + 0.045, ya + 0.11, yb - 0.11, 0.15, 0.19)

    y0, y1 = BANK_AT, BANK_AT + OFEN_BANK_D                          # along the Flur wall, beside the stove
    hc.xy_prism("Ofen", "Ofen_Bank", "FichteX", filleted([(0, y0), (0.7, y0), (0.7, y1), (0, y1)], 0.08, (2,)),
                zs - 0.045, zs)
    for x in (0.05, 0.59):
        legs(x, y0, y1)
    x0, x1, yl = BANK_AT, BANK_AT + OFEN_BANK_L, 0.005 + OFEN_BANK_D  # along the west wall (y = 0), where it stood
    hc.xy_prism("Ofen", "Ofen_Bank", "FichteX", filleted([(x0, 0.005), (x1, 0.005), (x1, yl), (x0, yl)], 0.08, (2,)),
                zs - 0.045, zs)
    for x in (x0 + 0.85, x1 - 0.12):
        legs(x, 0.005, yl)
    # bed: a straight platform OFEN_BED_W wide (#61), post at the free corner
    BL, BW = OFEN_BED_L, OFEN_BED_W
    bed = [(0, 0), (BW, 0), (BW, BL), (0, BL)]
    hc.xy_prism("Ofen", "Ofen_Bett", "FichteY", bed, zp, zp + 0.04)
    hc.box("Ofen", "Ofen_Bett", "FichteZ", BW - 0.08, BW, BL - 0.08, BL, 0.0, zp)
    for k in (1, 2, 3):                                              # ladder: rungs from the wall to the post
        zk = zp * k / 4
        hc.box("Ofen", "Ofen_Bett", "FichteX", 0.005, BW - 0.08, BL - 0.06, BL - 0.02, zk - 0.02, zk + 0.02)
    # rim: one board along the free long edge, upright (lean 0), square-cut and kept 10 cm clear of the wall and
    # of the foot end
    path, (rw, lean), th = bed[1:3], A["rim"], 0.025
    zb, rise, out = zp + 0.04, rw * math.cos(math.radians(lean)), rw * math.sin(math.radians(lean))
    levels = ((-th, zb), (0.0, zb), (out, zb + rise), (out - th, zb + rise))
    for i, (p, q) in enumerate(zip(path, path[1:])):
        Lp = math.dist(p, q)
        e, nn = ((q[0] - p[0]) / Lp, (q[1] - p[1]) / Lp), ((q[1] - p[1]) / Lp, (p[0] - q[0]) / Lp)
        ring = lambda s_: [(p[0] + s_ * e[0] + o_ * nn[0], p[1] + s_ * e[1] + o_ * nn[1], z) for o_, z in levels]
        s0, s1 = 0.10, Lp - 0.10
        hc.add("Ofen", "Ofen_Bettrand", "FichteY" if abs(nn[0]) > 0.9 else "FichteX", ring(s0) + ring(s1),
            [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    # the house's standard Wandlampe on the head-end wall (y = 0) above the bed (#22: it replaces the
    # small reading lamp); its light is one of the WALL_LIGHTS
    hc.wandlampe("Ofen", 0.35, 0.0, 0, 1, 2.10)
    # bedding: a very thin cream mattress, 1 cm clear of the rim boards. Fixed rnd: a plain colour
    # ignores it, and drawing none leaves every later part's random value unchanged
    gm, mt = th + 0.01, zb + 0.04
    hc.xy_prism("Ofen", "Ofen_Bettzeug", "Creme", filleted(
        [(0.005, 0.005), (BW - gm, 0.005), (BW - gm, BL - 0.01), (0.005, BL - 0.01)], 0.03, range(4)), zb, mt, 0.5)
    f = 0.15                                                        # dimension line offset
    return [((-f, 0, 0), (-f, a, 0), f"Ofen {a * 100:.0f}"),
            ((0, -f, 0), (a, -f, 0), f"{a * 100:.0f}"),
            (PD(-Lh / 2, 0.12, OFEN_H), PD(Lh / 2, 0.12, OFEN_H), f"Front {Lh * 100:.0f}"),
            (PD(-W, 0.12, zc + 0.04), PD(W, 0.12, zc + 0.04), "Tür 65"),
            (PB(bc - bw / 2, 0.12, bt + 0.04), PB(bc + bw / 2, 0.12, bt + 0.04), f"Tür hinten {bw * 100:.0f} (Flur)"),
            (PD(W + 0.12, 0.12, za), PD(W + 0.12, 0.12, zc), f"Tür {za * 100:.0f}–{zc * 100:.0f} (Unterkante angenommen)"),
            ((-f, a, 0), (-f, a, OFEN_H), f"Höhe {OFEN_H * 100:.0f}"),
            ((-f, a, OFEN_H), (-f, a, zp), f"{(zp - OFEN_H) * 100:.0f}"),
            (PD(-aw / 2, 0.05, zr), PD(aw / 2, 0.05, zr), "Bogen 50 × 30 (angenommen)"),
            ((x0, yl + f, zs), (x1, yl + f, zs), f"Bank {OFEN_BANK_L * 100:.0f}"),
            ((x1 + f, 0.005, zs), (x1 + f, yl, zs), "60"),
            ((0.7 + f, y0, zs), (0.7 + f, y1, zs), "Bank 60"),
            ((0.7 + f, y1, 0), (0.7 + f, y1, zs), "Sitz 45 (angenommen)"),
            ((-f, 0, zp), (-f, BL, zp), f"Bett {BL * 100:.0f}"),
            ((0, BL + f, zp), (BW, BL + f, zp), f"{BW * 100:.0f}"),
            ((BW, BL + f, 0), (BW, BL + f, zp), f"Bett-Unterkante {zp * 100:.0f}"),
            ((BW + f + out, BL - 0.10, zb), (BW + f + out, BL - 0.10, zb + rise),
             f"Rand {rw * 100:.0f}" + (f", {lean}° schräg" if lean else ", senkrecht"))]


def back_opening():
    """The back door's opening in the Stube/Flur wall, in house coordinates (an "I" opening)."""
    bc, bw, bt = OFEN_BACK
    return (OFEN_AT[0] + bc - bw / 2, OFEN_AT[0] + bc + bw / 2, OFEN_ASSUMED["sill"], bt, "I")


def ofen_im_haus():
    """The Ofen sub-model built into the Stube's NW corner (plan: "Kachelofen"), 4 mm off the walls:
    sub-model x (along its y = 0 wall) runs south along the Stube west wall, y north-east along the
    north wall, so the bed runs towards the Stube door and the long bench along the west wall.
    Its objects move to EG as EG_<name>; wood grain X/Y swaps with the axes; dimension lines dropped."""
    (x0, y0), swap = OFEN_AT, {"FichteX": "FichteY", "FichteY": "FichteX"}
    n0, nl, sh = len(hc.FIRES), len(hc.WALL_LIGHTS), WALL_FLUR - y0   # back door: moved out to the Flur face
    ofen_neu()
    hc.WALL_LIGHTS[nl:] = [(x0 + y, y0 - x, z) for x, y, z in hc.WALL_LIGHTS[nl:]]
    for f in hc.FIRES[n0:]:
        (x, y, z), (ux, uy) = f["base"], f["u"]
        f.update(base=(x0 + y, y0 - x + (sh if f.get("back") else 0), z), u=(uy, -ux), collection="EG")
    for key in [k for k in hc.GEO if k[0] == "Ofen"]:
        g = hc.GEO.pop(key)
        dy = sh if key[1] == "Ofen_Hintertuer" else 0
        g["v"] = [(x0 + y, y0 - x + dy, z) for x, y, z in g["v"]]
        g["m"] = [swap.get(m, m) for m in g["m"]]
        hc.GEO[("EG", "EG_" + key[1])], hc.PARTS[("EG", "EG_" + key[1])] = g, hc.PARTS.pop(key)
        if key[1] in hc.SMOOTH:
            hc.SMOOTH.discard(key[1]); hc.SMOOTH.add("EG_" + key[1])


def werkstattofen(c, cx, cy, z, turn=0, name="Werkstattofen", rng=random):
    """Small workshop stove after werkstattofen.jpeg (40 x 40 x 105 cm, sizes estimated from the
    photo), centred at (cx, cy) on floor z, front facing north turned by `turn` degrees
    (counter-clockwise): black iron body with a top plate, upper door with the fire behind glass,
    lower ash door, handles. Object c_<name>; its rnd comes from rng."""
    o, W = c + "_" + name, 0.40
    n0 = len(hc.GEO.get((c, o), {"v": []})["v"])
    x0, y0 = cx - W / 2, cy - W / 2
    x1, y1, xm = x0 + W, y0 + W, cx
    hc.box(c, o, "Eisen", x0, x1, y0, y1, z + 0.012, z + 1.03, rng.random())  # body
    hc.box(c, o, "Eisen", x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.01, z + 1.03, z + 1.05, rng.random())  # top plate
    r = rng.random()
    for xa, xb, za, zb in ((xm - 0.13, xm - 0.09, 0.60, 0.98), (xm + 0.09, xm + 0.13, 0.60, 0.98),
                           (xm - 0.13, xm + 0.13, 0.60, 0.64), (xm - 0.13, xm + 0.13, 0.94, 0.98)):
        hc.box(c, o, "Eisen", xa, xb, y1, y1 + 0.02, z + za, z + zb, r)                  # upper door frame
    hc.box(c, o, "Eisen", xm - 0.09, xm + 0.09, y1, y1 + 0.003, z + 0.64, z + 0.94, rng.random())  # firebox back
    hc.box(c, o, "Ofenglas", xm - 0.09, xm + 0.09, y1 + 0.014, y1 + 0.018, z + 0.64, z + 0.94, rng.random())
    hc.box(c, o, "Eisen", xm - 0.11, xm + 0.11, y1, y1 + 0.015, z + 0.17, z + 0.42, rng.random())  # ash door
    hc.box(c, o, "Eisen", xm + 0.135, xm + 0.15, y1 + 0.02, y1 + 0.045, z + 0.72, z + 0.84, rng.random())  # handles
    hc.box(c, o, "Eisen", xm + 0.11, xm + 0.13, y1 + 0.015, y1 + 0.05, z + 0.28, z + 0.30, rng.random())
    g, ca, sa = hc.GEO[(c, o)], math.cos(math.radians(turn)), math.sin(math.radians(turn))
    rot = lambda x, y: (cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca)
    g["v"][n0:] = [(*rot(x, y), zz) for x, y, zz in g["v"][n0:]]
    hc.FIRES.append(dict(base=(*rot(xm, y1 + 0.009), z + 0.66), u=(ca, sa), w=0.14, h=0.24, d=0.006,
                         collection=c))  # fire.py


def wamsler(c, x0, y0, rng, shaft):
    """Wood-fired kitchen cooker after wamsler.jpeg (80 x 58 x 90 cm, sizes estimated from the
    photo), front at x = x0 facing west, south side at y0: stainless steel body on a black plinth,
    steel top with a rail; seen from the front, the fire door with glass top left (north) and the
    ash door below it, the oven door with a window and a small door on the right, a full-width
    drawer; the flue on top at the left (north, over the firebox, #26b), its pipe up to height zc and
    there 90 deg north into the Kaminschacht, whose south face is at y = yf (shaft = (yf, zc)), with a
    rosette on that face. All parts take their rnd from rng, so the rest of the house keeps its
    random shading."""
    o, W, D, y1 = c + "_Herd", 0.80, 0.583, y0 + 0.80
    B = lambda mat, s0, s1, t0, t1, z0, z1, r=None: hc.box(c, o, mat, x0 + t0, x0 + t1, y1 - s1, y1 - s0, z0, z1,
                                                         rng.random() if r is None else r)
    disc = lambda r, n=12: [(r * math.cos(2 * math.pi * (i + 0.5) / n), r * math.sin(2 * math.pi * (i + 0.5) / n))
                            for i in range(n)]

    def bar(s0, s1, z, t=-0.04):                                  # steel bar along y on two posts
        hc.prism(c, o, "Stahl", hc.frame("x"), [(x0 + t + a, z + b) for a, b in disc(0.008, 8)], y1 - s1, y1 - s0,
                 rng.random())
        for s in (s0 + 0.02, s1 - 0.02):
            B("Stahl", s - 0.005, s + 0.005, t, -0.015, z - 0.005, z + 0.005)

    def grip(s, z0, z1, t=-0.035):                                # vertical steel handle on two posts
        hc.xy_prism(c, o, "Stahl", [(x0 + t + a, y1 - s + b) for a, b in disc(0.008, 8)], z0, z1, rng.random())
        for z in (z0 + 0.015, z1 - 0.015):
            B("Stahl", s - 0.005, s + 0.005, t, -0.015, z - 0.005, z + 0.005)

    B("Eisen", 0.02, W - 0.02, 0.04, D - 0.03, 0.005, 0.09)                      # plinth
    B("Stahl", 0, W, 0, D, 0.09, 0.865)                                           # body
    rt = rng.random()
    B("Stahl", -0.005, W + 0.005, -0.02, D, 0.865, 0.885, rt)                     # top plate, raised rim
    for s0, s1, t0 in ((-0.005, W + 0.005, -0.02), (-0.005, 0.025, -0.02), (W - 0.025, W + 0.005, -0.02)):
        B("Stahl", s0, s1, t0, D if s1 - s0 < 0.1 else 0.01, 0.885, 0.90, rt)
    bar(0.03, W - 0.03, 0.835, -0.045)                                           # rail under the top
    B("Stahl", 0.02, W - 0.02, -0.015, 0, 0.10, 0.285)                           # drawer
    bar(0.07, W - 0.07, 0.255)
    B("Stahl", 0.02, 0.27, -0.015, 0, 0.30, 0.53)                                # ash door
    grip(0.25, 0.37, 0.47)
    rf = rng.random()                                                            # fire door: frame round the glass
    for s0, s1, z0, z1 in ((0.02, 0.06, 0.545, 0.795), (0.23, 0.27, 0.545, 0.795),
                           (0.02, 0.27, 0.545, 0.585), (0.02, 0.27, 0.755, 0.795)):
        B("Stahl", s0, s1, -0.015, 0, z0, z1, rf)
    B("Eisen", 0.06, 0.23, -0.004, 0, 0.585, 0.755)                              # firebox back
    B("Ofenglas", 0.06, 0.23, -0.014, -0.011, 0.585, 0.755)
    hc.FIRES.append(dict(base=(x0 - 0.008, y1 - 0.145, 0.595), u=(0.0, 1.0), w=0.13, h=0.14, d=0.005,
                         collection=c))  # fire.py
    grip(0.25, 0.61, 0.73)
    B("Stahl", 0.285, W - 0.02, -0.015, 0, 0.30, 0.43)                           # small door
    B("Stahl", 0.285, W - 0.02, -0.015, 0, 0.445, 0.795)                         # oven door
    B("Eisen", 0.33, W - 0.065, -0.018, -0.015, 0.50, 0.71)                      # its window
    hc.prism(c, o, "Stahl", hc.frame("y"), [(y1 - 0.53 + a, 0.67 + b) for a, b in disc(0.025)],
             x0 - 0.020, x0 - 0.018, rng.random())                               # thermometer
    bar(0.31, W - 0.045, 0.765)
    # flue (left, over the firebox, #26b), its pipe up to zc, there 90 deg north into the Kaminschacht
    (yf, zc), fx, fy = shaft, x0 + 0.42, y1 - 0.14
    hc.xy_prism(c, o, "Eisen", [(fx + a, fy + b) for a, b in disc(0.07, 16)], 0.885, 0.95, rng.random())
    hc.xy_prism(c, o, "Eisen", [(fx + a, fy + b) for a, b in disc(0.06, 16)], 0.95, zc, rng.random())
    hc.prism(c, o, "Eisen", hc.frame("x"), [(fx + a, zc + b) for a, b in disc(0.06, 16)], fy - 0.06, yf + 0.03,
             rng.random())
    hc.prism(c, o, "Eisen", hc.frame("x"), [(fx + a, zc + b) for a, b in disc(0.10, 16)], yf - 0.01, yf,
             rng.random())                                                       # rosette on the shaft's face
