"""Frechenlehen – the Bad Großeltern (EG, NW corner) as a sub-model (web/bad.html), after the user's
sketch input/2026-11-08 input/plan_grosseltern_bad.jpeg and the agreed drawing
input/2026-11-08 input/grosseltern_v4.svg. From north to south: a walk-in shower 0.95 wide in the NW corner
(request 2026-11-25: the low wall moved 15 cm east), east of it a wall 1.20 m long, 1.00 m high, 12 cm thick
and a clear glass pane on its shower edge (above it to the ceiling, by the north wall down to the floor)
that turns the corner in front of the north wall: the north french door became a window (FENSTER, sill
1.00), whose west 15 cm now lie in the shower, so a return pane closes them off up to the north wall's
limestone, the water kept off sill and window; a Waschbecken doppelt 100 x 47 (two
deck mixers, one bowl, input/2026-11-12 input/) on its chrome Ständer on that wall's east face; in the south a niche 1.20 m deep over the full width,
one room since #61 (WC and Schrank were split by a 12 cm wall): the WC in the west behind an opening of 102.4 under a
lintel, a white Einbauschrank (50 deep, to the ceiling, two doors) in the east behind the niche's front wall, 58 clear
in front of it; one sliding leaf, built open in front of that wall, rolls over the opening and closes the room. The
floor: limestone in the niche and in a strip as wide as the WC along the west wall, oak elsewhere.

Pure Python like house_core.py, which imports this module: build_eg() calls bad_neu() at BAD_AT;
house_core.build_bad() wraps it at the origin as the Blueprint of web/bad.html. Everything is
axis-aligned and built straight into the given collection, so the house and the sub-model are the
same parts, only translated. Unlike the Ofen and the desk it brings walls of its own (the niche's front wall,
lintel, low wall); the outer walls stay in build_eg().
"""
import math, random
import house_core as hc

BAD_AT = (0.31, 8.656)                       # house: the room's inner SW corner
W, D = 2.048, 3.817                          # room (x, y); ceiling hc.Z_EG_TOP
NICHE, NW, HALF = 1.20, 0.12, 0.964          # niche depth, its front wall's thickness, the limestone strip's width
WP = 1.024                                   # #61: the niche's opening x 0 .. WP (over the WC), the front wall from WP
LW = WP + 0.04                               # the one sliding leaf: 4 cm over the wall when closed
SCH, SD = HALF + NW, 0.50                    # Einbauschrank: x from SCH to the east wall, depth with its doors
SHOWER = 0.95                                # walk-in shower width (west; 0.80 till 2026-11-25)
GLASS = 0.35                                 # thin glass from the north wall
FENSTER = (1.109, 2.008, 1.0, 2.0, "W", 1)   # the north window (house x; build_eg), the french door till 2026-11-25
FD_JAMB = FENSTER[0]                         # house x: its west jamb
RET = 0.025                                  # the glass's return: its centre plane off the north wall
LOW = (2.267, 3.467, 1.00, 0.12)             # low wall: v from, v to, height, thickness
TROG = (0.47, 1.00, 0.85)                    # Waschbecken doppelt: depth, width, top (hc.waschbecken's)
LIN = 2.05                                   # lintel underside / rail top
CLAD = 2.0                                   # shower's limestone cladding height


def bad_neu(c="Bad", x0=0.0, y0=0.0):
    """The Bad Großeltern with its niche, built into collection c with the room's inner SW corner at
    (x0, y0). The parts draw their rnd from their own generator (the toilet and the WC tiles keep
    theirs; the second leaf's draw is burnt). Returns the dimension lines (sub-model coordinates)."""
    rng = random.Random(5)
    H = hc.Z_EG_TOP
    B = lambda o, m, u0, u1, v0, v1, z0, z1, r=None: hc.box(c, c + o, m, x0 + u0, x0 + u1, y0 + v0, y0 + v1, z0, z1, r)
    T = lambda o, m, p0, p1, prof, r=None: hc.turned(c, c + o, m, (x0 + p0[0], y0 + p0[1], p0[2]),
                                                    (x0 + p1[0], y0 + p1[1], p1[2]), prof, rnd=r)
    disc = lambda o, m, u, v, rad, z0, z1, r=None: hc.xy_prism(
        c, c + o, m, [(x0 + u + rad * math.cos(2 * math.pi * i / 16), y0 + v + rad * math.sin(2 * math.pi * i / 16))
                      for i in range(16)], z0, z1, r)

    # walls (#61: WC and Schrank one room): the niche's front wall in front of the Einbauschrank, full height,
    # the lintel over the opening (the WC); the low wall
    r = rng.random()
    B("_Waende", "Putz", WP, W, NICHE - NW, NICHE, 0, H, r)
    B("_Waende", "Putz", 0, WP, NICHE - NW, NICHE, LIN, H, r)
    lv0, lv1, lh, lt = LOW
    B("_Waende", "Putz", SHOWER, SHOWER + lt, lv0, lv1, 0, lh, rng.random())

    # glass (request 2026-11-25): a pane on the low wall's shower edge, up to the ceiling and by the north
    # wall down to the floor, ending 1 mm short of the return; the return, 12 mm thick, RET off the north
    # wall, from the main pane's east face west over the window's jamb onto the north wall's limestone, a
    # chrome profile between its end and the slabs: so the window's west part lies outside the shower
    gx, yr = SHOWER - 0.007, D - RET                  # centre planes of the main pane and the return
    hc.prism(c, c + "_Sanitaer", "Glas", lambda u, t, z: (x0 + t, y0 + u, z),
             [(lv0, lh), (lv1, lh), (lv1, 0.0), (yr - 0.007, 0.0), (yr - 0.007, H), (lv0, H)],
             gx - 0.006, gx + 0.006, rng.random())
    r, xw = rng.random(), FD_JAMB - BAD_AT[0] - 0.012 - 0.04  # the second pane's draw; 4 cm over the slabs
    B("_Sanitaer", "Glas", xw, gx + 0.006, yr - 0.006, yr + 0.006, 0.0, H, r)
    B("_Sanitaer", "Metall", xw, xw + 0.015, yr + 0.006, D - 0.0125, 0.0, H, r)   # wall profile

    # niche (#61): one sliding leaf on one track, built open in front of the front wall; it rolls west over the
    # opening and closes the room (4 cm over the wall)
    LT, zl, o = 0.04, 0.005, "_Schiebetuer"
    LH, tc, la = LIN - 0.05 - zl - 0.005, NICHE + 0.01 + LT / 2, W - LW - 0.005
    rl = 0.8 + 0.2 * rng.random()
    rng.random()                                     # the second leaf's draw (till #61): later parts keep theirs

    def part(w0, w1, d0, d1, za, zb, r=rl, m="Innentuer"):
        B(o, m, la + w0, la + w1, tc + d0, tc + d1, zl + za, zl + zb, r)

    hc.six_panel_leaf(part, LW, LH)
    hc.sliding_pulls(part, LW)
    hc.SLIDE[c + o] = (-la, 0.0, 0.0)                # its own object: rolls over the opening and back
    hc.LEAVES.append((c, [(x0 + la, y0 + tc - LT / 2, zl), (x0 + la + LW, y0 + tc + LT / 2, zl + LH)]))
    B("_Innentueren", "Metall", 0, W, NICHE, NICHE + 0.06, LIN - 0.05, LIN - 0.005, rng.random())   # rail

    # the WC: the toilet in the opening on the south wall, Taubenblau tiles on the south wall up to the
    # Einbauschrank and on the west wall
    hc.toilet(c, x0 + HALF / 2, y0, 0, 1)
    hc.wainscot(c, 0.0, x0, x0 + SCH - 0.002, y0, y0 + NICHE, None, sides="sw")

    # Einbauschrank (#61), white, floor to ceiling, against the south wall east of the WC: carcass, a recessed
    # plinth, two doors (a frame round a recessed panel) with chrome knobs at the meeting stiles; in front of it
    # NICHE - NW - SD clear to the front wall
    S, m, r = "_Schrank", "Rahmen", rng.random()
    d, zp, um = SD - 0.02, 0.10, (SCH + W) / 2
    B(S, m, SCH, W, 0, 0.02, 0.0, H, r)                                             # back
    B(S, m, SCH, SCH + 0.02, 0.02, d, 0.0, H, r)                                    # sides
    B(S, m, W - 0.02, W, 0.02, d, 0.0, H, r)
    B(S, m, SCH + 0.02, W - 0.02, 0.02, d, H - 0.02, H, r)                          # top
    B(S, m, SCH + 0.02, W - 0.02, 0.02, d - 0.04, zp - 0.02, zp, r)                 # bottom
    B(S, "Fuge", SCH + 0.02, W - 0.02, d - 0.06, d - 0.04, 0.0, zp - 0.02, r)       # plinth, recessed
    for ua, ub in ((SCH + 0.002, um - 0.0015), (um + 0.0015, W - 0.002)):           # doors
        w, za, zb = 0.07, zp + 0.002, H - 0.003
        for a, b, zc, zd in ((ua, ua + w, za, zb), (ub - w, ub, za, zb), (ua + w, ub - w, za, za + w),
                             (ua + w, ub - w, zb - w, zb), (ua + w, ub - w, 1.25 - w / 2, 1.25 + w / 2)):
            B(S, m, a, b, d, SD, zc, zd, r)                                         # stiles, rails
        for zc, zd in ((za + w, 1.25 - w / 2), (1.25 + w / 2, zb - w)):
            B(S, m, ua + w, ub - w, d, SD - 0.008, zc, zd, r)                       # panels, recessed
        uk = ub - 0.04 if ua < um else ua + 0.04
        B(S, "Metall", uk - 0.01, uk + 0.01, SD, SD + 0.025, 1.04, 1.06, r)        # knob

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

    # Waschbecken doppelt (request 2026-11-12) on its Ständer, on the low wall's east face, centred
    # on it; one draw from this module's stream, as the former Waschtrog
    td, tw, tt = TROG
    ua, ub, va, vb = SHOWER + lt, SHOWER + lt + td, (lv0 + lv1 - tw) / 2, (lv0 + lv1 + tw) / 2
    hc.waschbecken(c, x0 + ua, y0 + (va + vb) / 2, 1, 0, tw, td, 2, rng=random.Random(rng.random()))

    floor(c, x0, y0)
    f, front = 0.06, tc + LT / 2                    # front: the sliding leaf's room face
    return [((SHOWER + lt / 2, front, 0.02), (SHOWER + lt / 2, lv0, 0.02), f"Durchgang {round((lv0 - front) * 100, 1):g}"),
            ((0, 3.10, CLAD), (SHOWER, 3.10, CLAD), f"Dusche {round(SHOWER * 100)}"),   # over the low wall: seen from the room
            ((SHOWER - f, lv1, CLAD + 0.2), (SHOWER - f, yr - 0.007, CLAD + 0.2), f"Glas {round((yr - 0.007 - lv1) * 100)}"),
            ((xw, yr - f, CLAD + 0.2), (gx + 0.006, yr - f, CLAD + 0.2), f"Ecke {round((gx + 0.006 - xw) * 100)}"),
            ((SHOWER - f, lv0, lh), (SHOWER - f, lv1, lh), "Mauer 120"),
            ((SHOWER + lt / 2, lv0 - f, 0), (SHOWER + lt / 2, lv0 - f, lh), "100 hoch"),
            ((ub + f, va, tt), (ub + f, vb, tt), "Waschbecken 100"),
            ((0, NICHE + 0.35, 0.02), (WP, NICHE + 0.35, 0.02), f"Öffnung {round(WP * 100, 1):g}"),
            ((SCH, SD + 0.05, 0.02), (W, SD + 0.05, 0.02), f"Einbauschrank {round((W - SCH) * 100, 1):g}"),
            ((SCH - 0.03, 0, 0.02), (SCH - 0.03, SD, 0.02), f"{round(SD * 100)} tief"),
            ((W - 0.30, SD, 0.02), (W - 0.30, NICHE - NW, 0.02), f"{round((NICHE - NW - SD) * 100)} frei"),
            ((WP - 0.08, 0, 0.02), (WP - 0.08, NICHE, 0.02), f"{round(NICHE * 100)} tief"),
            ((0, 1.80, LIN + 0.25), (W, 1.80, LIN + 0.25), f"Raumbreite {round(W * 100, 1):g}"),   # the room (request
            ((W - 0.30, 0, LIN + 0.25), (W - 0.30, D, LIN + 0.25), f"Raumtiefe {round(D * 100, 1):g}")]   # 2026-11-25)


def floor(c, x0, y0):
    """The room's floor, last and from its own generator (the parts before keep their rnd): a
    limestone strip as wide as the WC's former half along the west wall, from the south wall to the
    north wall at the shower's end, and limestone in the rest of the niche (#61, own generator), oak
    elsewhere (the room before the Waschbecken); slabs and planks as the house's floor_cover(), none
    under the low wall and the niche's front wall. A dark base under the joints (in the house inside EG_Boden)."""
    rng = random.Random(7)
    lv0, lv1, _, lt = LOW
    wall = lambda u0, u1, v0, v1: (x0 + u0, x0 + u1, y0 + v0, y0 + v1)
    hc.box(c, c + "_Boden", "Fuge", x0, x0 + W, y0, y0 + D, 0.0, 0.002, rng.random())
    hc.tiles(c, c + "_Bodenbelag", "Kalkstein", x0, x0 + HALF, y0, y0 + D, 0.002, 0.018, [0.5, 0.4, 0.55, 0.45],
             (0.35, 0.8), 0.006, [wall(SHOWER, SHOWER + lt, lv0, lv1)], rng)
    hc.tiles(c, c + "_Bodenbelag", "Eiche", x0 + HALF, x0 + W, y0 + NICHE, y0 + D, 0.002, 0.014, [0.2], (1.2, 2.4),
             0.003, [wall(SHOWER, SHOWER + lt, lv0, lv1)], rng)
    hc.tiles(c, c + "_Bodenbelag", "Kalkstein", x0 + HALF, x0 + W, y0, y0 + NICHE, 0.002, 0.018,       # the niche's east
             [0.5, 0.4, 0.55, 0.45], (0.35, 0.8), 0.006, [wall(WP, W, NICHE - NW, NICHE)],        # part to the leaf
             random.Random(61))                                                                   # line (#61)


def stone(c, x0, y0, side, rng):
    """Limestone cladding of the shower: "w" west wall, "n" north wall (both to CLAD), "l" the low
    wall's west face (to its top). Dark backing 2 mm off the wall, slabs 6 mm proud of it, rows of
    about 0.5 m, joints 4 mm; the west wall stops short of the north wall's slabs, the north wall's
    at the glass."""
    lv0, lv1, lh, _ = LOW
    T = 0.012
    face, n, ua, ub, top = {"w": (0.0, 1, lv0, D - T, CLAD), "n": (D, -1, 0.0, FD_JAMB - BAD_AT[0] - 0.012, CLAD),
                            "l": (SHOWER, -1, lv0, lv1, lh)}[side]
    hc.limestone(c, side == "n", face, n, ua, ub, 0.018, top, rng, x0, y0)
