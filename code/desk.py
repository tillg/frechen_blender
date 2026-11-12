"""Frechenlehen – the desk: the plain table builder desk() (OG laundry table) and the desk
sub-model (web/desk.html): the Büro desk in the Bibliothek, a solid cherry top on the cast-iron
crank frame of input/2026-11-12 input/schreibtischgestell.jpg (#10; the viewer cranks it up and
down: LIFT, CRANK), with two LG UltraFine 6K 32"
monitors showing the screenshots of input/2026-11-06 input/ (a12 left, pilcrow right), a MacBook
Pro left of them, a white Magic Keyboard and a white Magic Trackpad.

Pure Python like house_core.py, which imports this module: build_furniture() calls desk_neu() at
DESK_AT and stuhl() at the chair's old place in the build order; house_core.build_desk() wraps
desk_neu() at the origin as the Blueprint of web/desk.html. The primitives and the geometry
accumulator come from house_core (attribute access, because the two modules import each other).
Everything is axis-aligned and built straight into the given collection, so the house and the
sub-model are the same parts, only translated.
"""
import math, random
import house_core as hc

DESK_AT = (10.943, 11.471)                                 # house: SW corner, between the two north
DESK_W, DESK_D, DESK_H = 1.90, 1.00, 0.75                  # french doors of the Bibliothek, centred
                                                           # there, back edge 2 mm off the wall
CHAIR = (DESK_W / 2, -0.23)                                # chair centre, facing the desk (+y)
LIFT_DZ = 0.30                                             # crank travel: 75 -> 105 cm
# The crank frame ("Wien"), sizes read off the photo (assumed): two arched cast-iron legs across the
# depth, 10 cm thick, their west faces at LEG_X; on each two spindle housings and a gearbox between
# them (drive rods from leg to leg), a foot tube; the spindles carry flat bars under the top.
LEG_X, LEG_T, LEG_H = (0.20, 1.60), 0.10, 0.50
GEAR_TOP = 0.62                                            # top of the spindle housings
SPINDLE_Y = (0.35, 0.65)
WHEEL = (1.74, 0.50, 0.55), 0.13                           # hand wheel: hub (east leg, outside), radius
# LG UltraFine 6K 32" (32U990A): body and 31.5" 16:9 pane after the data sheet (assumed: the bezel
# split, the pane's height above the desk, the stand). MacBook Pro 16", Magic Keyboard with Touch
# ID, Magic Trackpad: Apple's dimensions.
MON_W, MON_H, MON_T = 0.714, 0.420, 0.025                  # body, front slab thickness
PANE = (0.697, 0.392)                                      # image area w, h
MON_LIFT = 0.11                                            # slab bottom above the top
MON_J = (CHAIR[0], 0.80)                                   # the monitors' front edges meet here,
MON_ANGLE = 170                                            # in front of the chair, at this angle (°)
MAC_X, MAC_Y, MAC = 0.05, 0.60, (0.3556, 0.2481, 0.0168)   # MacBook, closed: w, d, h; its back part
                                                           # under the left monitor
KB_X, KB_Y, KB = CHAIR[0] - 0.2789 / 2, 0.18, (0.2789, 0.1149, 0.0041, 0.0109)   # keyboard w, d,
                                                           # front/back height; centred on the chair
TP = (0.160, 0.1149, 0.0049, 0.0109)                      # trackpad, 4 cm right of the keyboard


def monitors():
    """(left end of the front edge, unit direction along the width, turn in degrees) of the left
    and the right monitor: front edges meeting at MON_J, both turned towards the chair."""
    a = (180 - MON_ANGLE) / 2
    out = []
    for turn in (a, -a):
        e = (math.cos(math.radians(turn)), math.sin(math.radians(turn)))
        l0 = (MON_J[0] - MON_W * e[0], MON_J[1] - MON_W * e[1]) if turn > 0 else MON_J
        out.append((l0, e, turn))
    return out


def desk(c, x0, x1, y0, y1, z=0.0):
    o = c + "_Moebel"
    hc.box(c, o, "FichteX", x0, x1, y0, y1, z + 0.72, z + 0.75)
    for xa in (x0 + 0.03, x1 - 0.08):
        for ya in (y0 + 0.03, y1 - 0.08):
            hc.box(c, o, "FichteZ", xa, xa + 0.05, ya, ya + 0.05, z + 0.012, z + 0.72)


def ring(cy, cz, r, n=12):
    """(y, z) circle profile for prism_x / (x, y) outline for xy_prism."""
    return [(cy + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def leg_profile(yc):
    """(y, z) outline of a leg about its centre yc: 40 cm block on top, flanks sweeping out in a
    concave curve to the 14 cm feet, a 42 x 22 cm arch between them."""
    flank = [(0.35 - 0.15 * math.cos(a), 0.30 - 0.25 * math.sin(a)) for a in (math.pi / 2 * i / 6 for i in range(7))]
    arch = [(0.21 * math.cos(a), 0.22 * math.sin(a)) for a in (math.pi * i / 12 for i in range(13))]
    half = [(0.20, 0.50)] + flank + [(0.35, 0.0)] + arch[:6]           # right half, from the top down and in
    pts = half + [(0.0, 0.22)] + [(-y, z) for y, z in reversed(half)]
    return [(yc + y, z) for y, z in pts]


def gestell(c, x0, y0, z, rng):
    """The static crank frame (furniture <c>_Moebel): legs, foot tube, housings, gearboxes, rods."""
    o, yc = c + "_Moebel", y0 + DESK_D / 2
    for lx in LEG_X:
        r, xa = rng.random(), x0 + lx
        hc.prism_x(c, o, "Eisen", xa, xa + LEG_T, [(y, z + h) for y, h in leg_profile(yc)], r)
        for sy in SPINDLE_Y:
            hc.box(c, o, "Eisen", xa + 0.005, xa + LEG_T - 0.005, y0 + sy - 0.045, y0 + sy + 0.045,
                   z + LEG_H, z + GEAR_TOP, r)
        hc.box(c, o, "Eisen", xa + 0.01, xa + LEG_T - 0.01, yc - 0.06, yc + 0.06, z + LEG_H, z + 0.58, r)
    xi, xe = x0 + LEG_X[0] + LEG_T, x0 + LEG_X[1]
    hc.prism_x(c, o, "Eisen", xi, xe, [(y, z + h) for y, h in ring(yc, 0.25, 0.04)], rng.random())   # foot tube
    for dy in (-0.03, 0.03):                                                                          # drive rods
        hc.prism_x(c, o, "Eisen", xi, xe, [(y, z + h) for y, h in ring(yc + dy, 0.55, 0.01, 8)], rng.random())


def platte(c, x0, y0, z, rng):
    """The lifted part (<c>_Schreibtisch): cherry top, a flat bar over each leg, four spindles
    reaching into their housings (still 5 mm inside at the top of the travel). The top and the
    spindles draw rnd globally: the five values the old table's top and legs drew."""
    o, T = c + "_Schreibtisch", z + DESK_H
    hc.box(c, o, "Kirschbaum", x0, x0 + DESK_W, y0, y0 + DESK_D, T - 0.04, T)
    for lx in LEG_X:
        xm = x0 + lx + LEG_T / 2
        hc.box(c, o, "Eisen", xm - 0.04, xm + 0.04, y0 + 0.08, y0 + DESK_D - 0.08, T - 0.05, T - 0.04, rng.random())
        for sy in SPINDLE_Y:
            hc.xy_prism(c, o, "Eisen", [(x + xm, y + y0 + sy) for x, y in ring(0, 0, 0.015, 8)],
                        z + GEAR_TOP - LIFT_DZ - 0.005, T - 0.05)
    for o2 in (o, c + "_Geraete", c + "_Bildschirm_L", c + "_Bildschirm_R"):
        hc.LIFT[o2] = LIFT_DZ


def handrad(c, x0, y0, z, rng):
    """Hand wheel on the east leg's outer face (<c>_Handrad, PIVOT at the hub): hub, five spokes,
    rim, a knob to crank it; it turns about x, four turns per stroke (CRANK: more would alias at 30 fps)."""
    o, r = c + "_Handrad", rng.random()
    (hx, hy, hz), R = WHEEL
    hx, hy, hz = x0 + hx, y0 + hy, z + hz
    xf = x0 + LEG_X[1] + LEG_T                                              # the leg's outer face
    hc.prism_x(c, o, "Eisen", xf, hx + 0.02, ring(hy, hz, 0.025), r)          # hub
    n = 24
    for i in range(n):                                                     # rim
        a, b = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        hc.prism_x(c, o, "Eisen", hx - 0.005, hx + 0.01,
                   [(hy + rr * math.cos(t), hz + rr * math.sin(t)) for rr, t in ((R - 0.015, a), (R, a), (R, b), (R - 0.015, b))], r)
    for k in range(5):                                                     # spokes
        t = 2 * math.pi * k / 5 + math.pi / 2
        u, v = (math.cos(t), math.sin(t)), (-math.sin(t) * 0.006, math.cos(t) * 0.006)
        hc.prism_x(c, o, "Eisen", hx - 0.003, hx + 0.008,
                   [(hy + rr * u[0] + s * v[0], hz + rr * u[1] + s * v[1]) for rr, s in ((0.02, -1), (R - 0.01, -1), (R - 0.01, 1), (0.02, 1))], r)
    t = math.radians(200)                                                  # knob
    hc.prism_x(c, o, "Eisen", hx + 0.01, hx + 0.08, ring(hy + (R - 0.008) * math.cos(t), hz + (R - 0.008) * math.sin(t), 0.012, 8), r)
    hc.PIVOT[o], hc.CRANK[o] = (hx, hy, hz), ((1, 0, 0), 4 * 360)


def stuhl(c, x0, y0):
    """The board chair at the desk (house_core.chair)."""
    hc.chair(c, x0 + CHAIR[0], y0 + CHAIR[1], 0, 1)


def obox(c, o, m, p, ex, ey, ez, rnd):
    """Box spanned by the edge vectors ex, ey, ez from corner p."""
    v = [tuple(p[k] + a * ex[k] + b * ey[k] + d * ez[k] for k in range(3))
         for d in (0, 1) for a, b in ((0, 0), (1, 0), (1, 1), (0, 1))]
    hc.add(c, o, m, v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], rnd)


def wedge(c, o, m, x0, x1, y0, d, hf, hb, z, rnd):
    """Apple wedge (keyboard, trackpad): height hf at the front edge y0, hb at the back."""
    hc.prism_x(c, o, m, x0, x1, [(y0, z), (y0 + d, z), (y0 + d, z + hb), (y0, z + hf)], rnd)


def monitor(c, o, side, l0, e, turn, T, img, rnd):
    """LG 32" on its stand, in its own frame (u along the width from the left front edge l0, t
    back into it): black front slab, silver back housing and stand; the pane is its own object,
    pivot at its lower-left corner and turned with the monitor, so the image maps in object space."""
    P = lambda u, t, z: (l0[0] + u * e[0] - t * e[1], l0[1] + u * e[1] + t * e[0], z)

    def fbox(m, o, u0, u1, t0, t1, z0, z1):
        obox(c, o, m, P(u0, t0, z0), ((u1 - u0) * e[0], (u1 - u0) * e[1], 0),
             (-(t1 - t0) * e[1], (t1 - t0) * e[0], 0), (0, 0, z1 - z0), rnd)

    zb, uc = T + MON_LIFT, MON_W / 2
    fbox("Alu", o, uc - 0.12, uc + 0.12, -0.03, 0.17, T, T + 0.012)                              # foot
    fbox("Alu", o, uc - 0.03, uc + 0.03, 0.05, 0.08, T + 0.012, zb + 0.30)                       # column
    fbox("Alu", o, uc - 0.20, uc + 0.20, MON_T, MON_T + 0.03, zb + 0.06, zb + 0.34)              # back housing
    fbox("Eisen", o, 0, MON_W, 0, MON_T, zb, zb + MON_H)                                         # slab
    pu, pz = (MON_W - PANE[0]) / 2, zb + MON_H - (MON_W - PANE[0]) / 2 - PANE[1]               # thin top/sides, chin
    po = c + "_Bildschirm_" + side
    fbox(img, po, pu, pu + PANE[0], -0.002, -0.0005, pz, pz + PANE[1])
    hc.PIVOT[po], hc.TURN[po] = P(pu, -0.002, pz), turn


def apple_logo(n=360):
    """Apple logo outline, about 0.85 wide and 0.95 high (body), top +y, bite on the right: an
    ellipse, wider above than below, with a gentle dip at the top and a smaller one at the bottom,
    minus the bite (a circle); and the leaf, a pointed lens leaning to the right."""
    bx, by, br = 0.50, 0.08, 0.17
    body = []
    for i in range(n):
        th = 2 * math.pi * i / n
        x, y = 0.5 * math.cos(th), 0.47 * math.sin(th)
        x *= 1 + 0.10 * y - (0.12 * -y if y < 0 else 0)                       # wide shoulders, narrow base
        dip = lambda c, w, d: d * math.exp(-(((th - c + math.pi) % (2 * math.pi) - math.pi) / w) ** 2)
        y -= dip(math.pi / 2, 0.22, 0.09) - dip(3 * math.pi / 2, 0.16, -0.04)
        if math.dist((x, y), (bx, by)) < br:                                  # bite: back along the ray
            t = math.hypot(x, y)                                              # from the centre to the circle
            k = (x * bx + y * by) / t
            t = k - math.sqrt(k * k - bx * bx - by * by + br * br) if k * k > bx * bx + by * by - br * br else t
            x, y = x / math.hypot(x, y) * t, y / math.hypot(x, y) * t
        body.append((0.85 * x, y))
    a, L, W = math.radians(55), 0.17, 0.075
    lens = [(L * math.cos(t), W * (1 - math.cos(t) ** 2)) for t in (math.pi * k / 12 for k in range(13))]
    lens += [(x, -y) for x, y in lens[-2:0:-1]]
    leaf = [(0.06 + x * math.cos(a) - y * math.sin(a), 0.60 + x * math.sin(a) + y * math.cos(a)) for x, y in lens]
    return body, leaf


def macbook(c, o, x0, y0, T, rnd):
    """MacBook Pro 16", silver, closed (hinge at the back): on the lid the softly lit Apple logo,
    3 cm high, its top towards the front edge (as it sits on a closed lid)."""
    (w, d, h), x, y = MAC, x0 + MAC_X, y0 + MAC_Y
    hc.box(c, o, "Alu", x, x + w, y, y + d, T, T + h, rnd)
    cx, cy, s = x + w / 2, y + d / 2, 0.03 / 0.86
    for pts in apple_logo():
        hc.xy_prism(c, o, "Apfel", [(cx - s * px, cy - s * py) for px, py in pts], T + h, T + h + 0.0003, rnd)


def keyboard(c, o, x0, y0, T, rnd):
    """Magic Keyboard (Touch ID, no keypad): silver wedge, white keys in six rows (half-height
    function row), 18.6 mm pitch."""
    (w, d, hf, hb), x, y = KB, x0 + KB_X, y0 + KB_Y
    wedge(c, o, "Alu", x, x + w, y, d, hf, hb, T, rnd)
    top = lambda yy: T + hf + (hb - hf) * (yy - y) / d
    rows = [[1, 1, 1, 1.25, 5, 1.25, 1, 1, 1, 1], [2.25] + [1] * 10 + [2.25], [1.75] + [1] * 11 + [1.75],
            [1.5] + [1] * 12 + [1], [1] * 13 + [1.5], [14.5 / 14] * 14]
    pitch, gap = 0.0186, 0.0025
    xs = x + (w - 14.5 * pitch) / 2
    for i, row in enumerate(rows):
        ya = y + 0.0035 + 0.019 * i
        yb = ya + (0.008 if i == 5 else 0.0165)
        xa = xs
        for u in row:
            hc.box(c, o, "Tasten", xa + gap / 2, xa + u * pitch - gap / 2, ya, yb, top(ya) - 0.001, top(yb) + 0.0008, rnd)
            xa += u * pitch


def trackpad(c, o, x0, y0, T, rnd):
    """Magic Trackpad, white: silver wedge with a white glass top."""
    (w, d, hf, hb) = TP
    x, y = x0 + KB_X + KB[0] + 0.04, y0 + KB_Y
    wedge(c, o, "Alu", x, x + w, y, d, hf, hb, T, rnd)
    e, top = 0.0015, lambda yy: T + hf + (hb - hf) * (yy - y) / d
    hc.prism_x(c, o, "Tasten", x + e, x + w - e, [(y + e, top(y + e) - 0.0005), (y + d - e, top(y + d - e) - 0.0005),
                                                  (y + d - e, top(y + d - e) + 0.0008), (y + e, top(y + e) + 0.0008)], rnd)


def desk_neu(c="Desk", x0=0.0, y0=0.0, z=0.0):
    """The Büro desk with its devices at (x0, y0) on floor z: the cherry top on the crank frame
    (gestell(), platte(), handrad()), two monitors along the back right of a MacBook Pro, keyboard
    and trackpad in front of the monitors. Frame and devices draw their rnd from their own
    generators, so the parts built after them keep their random values. Returns the dimension
    lines (sub-model coordinates)."""
    fr = random.Random(18)
    gestell(c, x0, y0, z, fr)
    platte(c, x0, y0, z, fr)
    handrad(c, x0, y0, z, fr)
    o, T, rng = c + "_Geraete", z + DESK_H, random.Random(3)
    for side, (l0, e, turn), img in zip("LR", monitors(), ("Bildschirm_A12", "Bildschirm_Pilcrow")):
        monitor(c, o, side, (x0 + l0[0], y0 + l0[1]), e, turn, T, img, rng.random())
    macbook(c, o, x0, y0, T, rng.random())
    keyboard(c, o, x0, y0, T, rng.random())
    trackpad(c, o, x0, y0, T, rng.random())
    f, W, D, H = 0.15, DESK_W, DESK_D, DESK_H
    zt = H + MON_LIFT + MON_H
    (l0, e, _), (r0, er, _) = monitors()
    re = (r0[0] + MON_W * er[0] + 0.05, r0[1] + MON_W * er[1] - 0.01)                  # right monitor's outer end
    return [((0, -f, 0), (W, -f, 0), "Tisch 190"),
            ((W + f, 0, 0), (W + f, D, 0), "100"),
            ((W + f, -f, 0), (W + f, -f, H), "75–105"),
            ((LEG_X[0], -f / 2, 0), (LEG_X[1] + LEG_T, -f / 2, 0), "Gestell 150 (angenommen)"),
            ((-f, D / 2 - 0.35, 0), (-f, D / 2 + 0.35, 0), "70 (angenommen)"),
            ((l0[0], l0[1] - 0.05, zt + 0.06), (MON_J[0], MON_J[1] - 0.05, zt + 0.06), "LG 32″ 71.4"),
            ((*re, H + MON_LIFT), (*re, zt), "42"),
            ((*re, H), (*re, H + MON_LIFT), "11 (angenommen)"),
            ((MAC_X, MAC_Y - 0.06, H), (MAC_X + MAC[0], MAC_Y - 0.06, H), "MacBook Pro 35.6"),
            ((KB_X, KB_Y - 0.06, H), (KB_X + KB[0], KB_Y - 0.06, H), "27.9"),
            ((KB_X + KB[0] + 0.04, KB_Y - 0.06, H), (KB_X + KB[0] + 0.04 + TP[0], KB_Y - 0.06, H), "16")]
