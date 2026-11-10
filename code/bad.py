"""Frechenlehen – the Bad Großeltern (EG, NW corner) as a sub-model (web/bad.html), after the user's
sketch input/2026-11-08 input/plan_grosseltern_bad.jpeg and the agreed drawing
input/2026-11-08 input/grosseltern_v4.svg. From north to south: a walk-in shower 0.80 wide in the NW corner
(clear of the north french door), east of it a wall 1.20 m long, 1.00 m high, 12 cm thick and one
L-shaped clear glass pane on its shower edge, flush with the north french door's jamb (above it to
the ceiling, 35 cm from the north wall down to the floor); the Waschtrog (one 1.00 m trough, two
deck mixers) on that wall's east face; in the south a niche 1.20 m deep over the full width, split
by a 12 cm wall into WC (west) and Schrank (east), closed by two interlocking sliding leaves on two
offset tracks (the WC leaf open, slid behind the Schrank leaf). The floor: a limestone strip as wide as the WC along the west wall, oak
elsewhere.

Pure Python like house_core.py, which imports this module: build_eg() calls bad_neu() at BAD_AT;
house_core.build_bad() wraps it at the origin as the Blueprint of web/bad.html. Everything is
axis-aligned and built straight into the given collection, so the house and the sub-model are the
same parts, only translated. Unlike the Ofen and the desk it brings walls of its own (niche wall,
lintel, low wall); the outer walls stay in build_eg().
"""
import math, random
import house_core as hc

BAD_AT = (0.31, 8.656)                       # house: the room's inner SW corner
W, D = 2.048, 3.817                          # room (x, y); ceiling hc.Z_EG_TOP
NICHE, NW, HALF = 1.20, 0.12, 0.964          # niche depth, its middle wall, WC / Schrank width
SHOWER = 0.80                                # walk-in shower width (west)
GLASS = 0.35                                 # thin glass from the north wall
FD_JAMB = 1.109                              # house x: west jamb of the north french door (build_eg)
LOW = (2.267, 3.467, 1.00, 0.12)             # low wall: v from, v to, height, thickness
TROG = (0.50, 1.00, 0.85)                    # Waschtrog: depth, width, top
LIN = 2.05                                   # lintel underside / rail top
CLAD = 2.0                                   # shower's limestone cladding height


def bad_neu(c="Bad", x0=0.0, y0=0.0):
    """The Bad Großeltern with its niche, built into collection c with the room's inner SW corner at
    (x0, y0). The parts draw their rnd from their own generator (the toilet and the WC tiles keep
    theirs). Returns the dimension lines (sub-model coordinates)."""
    rng = random.Random(5)
    H = hc.Z_EG_TOP
    B = lambda o, m, u0, u1, v0, v1, z0, z1, r=None: hc.box(c, c + o, m, x0 + u0, x0 + u1, y0 + v0, y0 + v1, z0, z1, r)
    T = lambda o, m, p0, p1, prof, r=None: hc.turned(c, c + o, m, (x0 + p0[0], y0 + p0[1], p0[2]),
                                                    (x0 + p1[0], y0 + p1[1], p1[2]), prof, rnd=r)
    disc = lambda o, m, u, v, rad, z0, z1, r=None: hc.xy_prism(
        c, c + o, m, [(x0 + u + rad * math.cos(2 * math.pi * i / 16), y0 + v + rad * math.sin(2 * math.pi * i / 16))
                      for i in range(16)], z0, z1, r)

    # walls: niche wall, lintel over the niche (beside the niche wall: no coplanar faces), low wall
    r = rng.random()
    B("_Waende", "Putz", HALF, HALF + NW, 0, NICHE, 0, H, r)
    B("_Waende", "Putz", 0, HALF, NICHE - NW, NICHE, LIN, H, r)
    B("_Waende", "Putz", HALF + NW, W, NICHE - NW, NICHE, LIN, H, r)
    lv0, lv1, lh, lt = LOW
    B("_Waende", "Putz", SHOWER, SHOWER + lt, lv0, lv1, 0, lh, rng.random())

    # glass: one L-shaped pane on the low wall's shower edge, up to the ceiling and 35 cm from the
    # north wall down to the floor; towards the north french door flush with its jamb
    um = FD_JAMB - BAD_AT[0] - 0.006
    hc.prism(c, c + "_Sanitaer", "Glas", lambda u, t, z: (x0 + t, y0 + u, z),
             [(lv0, lh), (lv1, lh), (lv1, 0.0), (D, 0.0), (D, H), (lv0, H)], um - 0.006, um + 0.006, rng.random())
    rng.random()                                 # the second pane's draw: later parts keep their rnd

    # niche: interlocking sliding leaves on two tracks (rear = WC, front = Schrank), both over the
    # Schrank half (the WC leaf open behind the Schrank leaf); closed, the WC leaf spans 0 .. HALF + NW
    LW, LT, zl = HALF + NW, 0.04, 0.005
    LH = LIN - 0.05 - zl - 0.005
    for tc, o in ((NICHE + 0.01 + LT / 2, "_Schiebetuer_hinten"), (NICHE + 0.06 + LT / 2, "_Schiebetuer_vorne")):
        rl = 0.8 + 0.2 * rng.random()

        def part(w0, w1, d0, d1, za, zb, r=rl, m="Innentuer", tc=tc, o=o):
            B(o, m, HALF + w0, HALF + w1, tc + d0, tc + d1, zl + za, zl + zb, r)

        hc.six_panel_leaf(part, LW, LH)
        hc.SLIDE[c + o] = (-HALF, 0.0, 0.0)          # one object each: rolls over the WC half and back
        hc.LEAVES.append((c, [(x0 + HALF, y0 + tc - LT / 2, zl), (x0 + HALF + LW, y0 + tc + LT / 2, zl + LH)]))
    B("_Innentueren", "Metall", 0, W, NICHE, NICHE + 0.11, LIN - 0.05, LIN - 0.005, rng.random())   # rail

    # WC half: the toilet in its middle on the south wall, Taubenblau tiles (north side open)
    hc.toilet(c, x0 + HALF / 2, y0, 0, 1)
    hc.wainscot(c, 0.0, x0, x0 + HALF, y0, y0 + NICHE, (x0, x0 + HALF))

    # Schrank, open, white: back cabinet over the full width with shelves, nothing in front of it
    S, m, u0, r = "_Schrank", "Rahmen", HALF + NW, rng.random()
    B(S, m, u0, W, 0, 0.02, 0.012, LIN, r)                                          # back
    B(S, m, u0, u0 + 0.02, 0.02, 0.60, 0.012, LIN, r)                               # sides
    B(S, m, W - 0.02, W, 0.02, 0.60, 0.012, LIN, r)
    B(S, m, u0 + 0.02, W - 0.02, 0.02, 0.60, LIN - 0.02, LIN, r)                    # top
    for zb in (0.10, 0.48, 0.86, 1.24, 1.62):                                       # bottom + shelves
        B(S, m, u0 + 0.02, W - 0.02, 0.02, 0.59, zb - 0.02, zb, r)

    # walk-in shower: limestone on the west and north walls to 2.0 and on the low wall's west face
    # to 1.0 (dark backing, slabs with joints); floor flush, drain, rain head on an arm
    stone(c, x0, y0, "w", rng)
    stone(c, x0, y0, "n", rng)
    stone(c, x0, y0, "l", rng)
    r = rng.random()
    disc("_Sanitaer", "Metall", SHOWER / 2, 3.294, 0.08, 0.018, 0.021, r)                       # drain
    vw = D - 0.012                                                                               # cladding face
    T("_Sanitaer", "Metall", (SHOWER / 2, vw, 1.05), (SHOWER / 2, vw - 0.06, 1.05), [(0.03, 0), (0.03, 1)], r)   # mixer
    T("_Sanitaer", "Metall", (SHOWER / 2, vw - 0.06, 1.05), (SHOWER / 2, vw - 0.06, 1.12), [(0.008, 0), (0.008, 1)], r)
    B("_Sanitaer", "Metall", SHOWER / 2 - 0.012, SHOWER / 2 + 0.012, vw - 0.03, vw, 1.08, 2.20, r)   # riser
    B("_Sanitaer", "Metall", SHOWER / 2 - 0.012, SHOWER / 2 + 0.012, 3.494, vw - 0.03, 2.18, 2.20, r)   # arm
    disc("_Sanitaer", "Metall", SHOWER / 2, 3.494, 0.15, 2.155, 2.18, r)                        # rain head 30

    # Waschtrog: one ceramic trough hung on the low wall's east face, a deck along the wall with
    # two pillar mixers, one bowl; a drain under each mixer
    td, tw, tt = TROG
    ua, ub, va, vb = SHOWER + lt, SHOWER + lt + td, (lv0 + lv1 - tw) / 2, (lv0 + lv1 + tw) / 2
    r, deck, e = rng.random(), 0.12, 0.03
    B("_Sanitaer", "Keramik", ua, ub, va, vb, tt - 0.15, tt - 0.12, r)                          # bottom
    B("_Sanitaer", "Keramik", ua, ua + deck, va, vb, tt - 0.12, tt, r)                          # deck
    B("_Sanitaer", "Keramik", ub - e, ub, va, vb, tt - 0.12, tt, r)                             # front rim
    B("_Sanitaer", "Keramik", ua + deck, ub - e, va, va + e, tt - 0.12, tt, r)                  # sides
    B("_Sanitaer", "Keramik", ua + deck, ub - e, vb - e, vb, tt - 0.12, tt, r)
    for v in (va + tw / 4, vb - tw / 4):
        um = ua + 0.05
        T("_Sanitaer", "Metall", (um, v, tt), (um, v, tt + 0.13), [(0.018, 0), (0.016, 1)], r)       # mixer
        T("_Sanitaer", "Metall", (um, v, tt + 0.12), (um + 0.15, v, tt + 0.10), [(0.009, 0), (0.008, 1)], r)   # spout
        T("_Sanitaer", "Metall", (um, v, tt + 0.13), (um - 0.03, v, tt + 0.18), [(0.006, 0), (0.005, 1)], r)   # lever
        disc("_Sanitaer", "Metall", ua + deck + (td - deck - e) / 2, v, 0.025, tt - 0.12, tt - 0.117, r)       # drain

    floor(c, x0, y0)
    f, front = 0.06, NICHE + 0.06 + LT              # front: the front sliding leaf's room face
    return [((SHOWER + lt / 2, front, 0.02), (SHOWER + lt / 2, lv0, 0.02), f"Durchgang {round((lv0 - front) * 100, 1):g}"),
            ((0, D - 0.15, 0.02), (SHOWER, D - 0.15, 0.02), "Dusche 80"),
            ((SHOWER - f, lv1, CLAD + 0.2), (SHOWER - f, D, CLAD + 0.2), "Glas 35"),
            ((SHOWER - f, lv0, lh), (SHOWER - f, lv1, lh), "Mauer 120"),
            ((SHOWER + lt / 2, lv0 - f, 0), (SHOWER + lt / 2, lv0 - f, lh), "100 hoch"),
            ((ub + f, va, tt), (ub + f, vb, tt), "Waschtrog 100"),
            ((0, NICHE + 0.35, 0.02), (HALF, NICHE + 0.35, 0.02), "WC 96.4"),
            ((HALF, NICHE + 0.35, 0.02), (HALF + NW, NICHE + 0.35, 0.02), "12"),
            ((HALF + NW, 0.08, LIN + 0.05), (W, 0.08, LIN + 0.05), "Schrank 96.4"),
            ((W - 0.08, 0, 0.02), (W - 0.08, NICHE, 0.02), "120 tief"),
            ((W - 0.08, 0, LIN + 0.05), (W - 0.08, 0.60, LIN + 0.05), "60")]


def floor(c, x0, y0):
    """The room's floor, last and from its own generator (the parts before keep their rnd): a
    limestone strip as wide as the WC along the west wall, from the south wall behind the toilet to
    the north wall at the shower's end (WC, shower), oak elsewhere (Schrank, the room before the
    Waschtrog); slabs and planks as the house's floor_cover(), none under the low wall and the
    niche wall. A dark base under the joints (in the house inside EG_Boden)."""
    rng = random.Random(7)
    lv0, lv1, _, lt = LOW
    wall = lambda u0, u1, v0, v1: (x0 + u0, x0 + u1, y0 + v0, y0 + v1)
    hc.box(c, c + "_Boden", "Fuge", x0, x0 + W, y0, y0 + D, 0.0, 0.002, rng.random())
    hc.tiles(c, c + "_Bodenbelag", "Kalkstein", x0, x0 + HALF, y0, y0 + D, 0.002, 0.018, [0.5, 0.4, 0.55, 0.45],
             (0.35, 0.8), 0.006, [wall(SHOWER, SHOWER + lt, lv0, lv1)], rng)
    hc.tiles(c, c + "_Bodenbelag", "Eiche", x0 + HALF, x0 + W, y0, y0 + D, 0.002, 0.014, [0.2], (1.2, 2.4), 0.003,
             [wall(HALF, HALF + NW, 0, NICHE)], rng)


def stone(c, x0, y0, side, rng):
    """Limestone cladding of the shower: "w" west wall, "n" north wall (both to CLAD), "l" the low
    wall's west face (to its top). Dark backing 2 mm off the wall, slabs 6 mm proud of it, rows of
    about 0.5 m, joints 4 mm; the west wall stops short of the north wall's slabs, the north wall's
    at the glass."""
    lv0, lv1, lh, _ = LOW
    T, J = 0.012, 0.004
    face, n, ua, ub, top = {"w": (0.0, 1, lv0, D - T, CLAD), "n": (D, -1, 0.0, FD_JAMB - BAD_AT[0] - 0.012, CLAD),
                            "l": (SHOWER, -1, lv0, lv1, lh)}[side]
    along_v = side != "n"
    o = c + "_Fliesen"

    def S(m, a, b, t0, t1, za, zb, r):
        ta, tb = sorted((face + n * t0, face + n * t1))
        if along_v:
            hc.box(c, o, m, x0 + ta, x0 + tb, y0 + a, y0 + b, za, zb, r)
        else:
            hc.box(c, o, m, x0 + a, x0 + b, y0 + ta, y0 + tb, za, zb, r)

    S("Fuge", ua, ub, 0.002, 0.006, 0.018, top, 0.5)
    rows = [0.018 + k * (top - 0.018) / round((top - 0.018) / 0.5) for k in range(round((top - 0.018) / 0.5) + 1)]
    for za, zb in zip(rows[:-1], rows[1:]):
        u = ua - rng.uniform(0, 0.4)
        while u < ub:
            a, b = max(u, ua), min(u + rng.uniform(0.4, 0.8), ub)
            if b - a > 0.02:
                S("Kalkstein", a + J / 2, b - J / 2, 0.006, T, za + J / 2, zb - J / 2, rng.random())
            u = b if b > u else ub
