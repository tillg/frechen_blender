"""Frechenlehen – the Bad Großeltern (EG, NW corner) as a sub-model (web/bad.html), after the user's
sketch input/2026-11-08 input/plan_grosseltern_bad.jpeg, the agreed drawing input/2026-11-08 input/grosseltern_v4.svg
and, since issue #63, variant B of input/2026-11-28 input/bad_grosseltern_optionen.svg. In the south a niche, 1.30
clear (its 12 cm front wall moved 22 cm north, #63), WC and shower in one room as in the Duschbad by the back hall
(code/gaeste_wc.py): the toilet in the west behind an opening of 102.4 under a lintel, east of it a walk-in shower
90 x 130 (no tray: the niche's limestone runs through; limestone on its walls to 2.0, the head on the east wall), a
glass pane 75 from the south wall on its west side, the entry 55 north of it; one sliding leaf, built open in front of
the front wall, rolls over the opening and closes the room. The room north of it: the Waschbecken einzeln 60 on the
north wall in the NW corner (where the walk-in shower stood till #63), west of the north window (FENSTER, sill 1.00), a
mirror 60 x 85 in a wooden frame above it; the west wall carries the big window WESTFENSTER (#63: 198 wide, sill
0.75, up to the ceiling like the OG's west windows), built by build_eg(). The floor: limestone in the niche and in a
strip along the west wall, oak elsewhere.

Pure Python like house_core.py, which imports this module: build_eg() calls bad_neu() at BAD_AT;
house_core.build_bad() wraps it at the origin as the Blueprint of web/bad.html. Everything is
axis-aligned and built straight into the given collection, so the house and the sub-model are the
same parts, only translated. Unlike the Ofen and the desk it brings walls of its own (the niche's front wall and
lintel); the outer walls stay in build_eg().
"""
import math, random
import house_core as hc

BAD_AT = (0.31, 8.656)                       # house: the room's inner SW corner
W, D = 2.048, 3.817                          # room (x, y); ceiling hc.Z_EG_TOP
NICHE, NW, HALF = 1.42, 0.12, 0.964          # niche to its front wall's north face (#63: 1.30 clear), the wall's thickness,
                                             # the limestone strip's width
WP = 1.024                                   # the niche's opening x 0 .. WP (over the WC), the front wall from WP
LW = WP + 0.04                               # the one sliding leaf: 4 cm over the wall when closed
XS, GL, HY = 1.148, 0.75, 0.575              # shower (#63): glass line (shower XS .. W, 90), glass from the south wall,
                                             # head on the east wall at y HY (as gaeste_wc.py)
FENSTER = (1.109, 2.008, 1.0, 2.0, "W", 1)   # the north window (house x; build_eg), the french door till 2026-11-25
WESTFENSTER = (10.285, 12.265, 0.75)         # #63: the west window (house y, sill; head the EG ceiling; build_eg),
                                             # 198 wide, centred on the wall between the niche and the north wall
BX, BW, BD = 0.40, 0.60, 0.47                # Waschbecken einzeln on the north wall: axis (x), width, depth
MW, MH, MF, MZ = 0.60, 0.85, 0.08, 1.17      # its mirror: outer width x height, frame width, bottom
LIN = 2.05                                   # lintel underside / rail top
CLAD, ST = 2.0, 0.012                        # shower's limestone cladding height, slab face
OLD_DRAWS = 10                               # global draws of bad_neu till #63 (burnt: later parts keep their rnd)


def cm(a, b):
    return "%g" % round(abs(b - a) * 100, 1)


def bad_neu(c="Bad", x0=0.0, y0=0.0):
    """The Bad Großeltern with its niche, built into collection c with the room's inner SW corner at
    (x0, y0). The parts draw their rnd from their own generator; toilet and shower draw from the global stream,
    which is then set to where the bathroom till #63 left it (OLD_DRAWS). Returns the dimension lines (sub-model
    coordinates)."""
    st, rng = random.getstate(), random.Random(5)
    H, YI = hc.Z_EG_TOP, NICHE - NW                 # YI: the niche's clear depth (front wall's south face)
    B = lambda o, m, u0, u1, v0, v1, z0, z1, r=None: hc.box(c, c + o, m, x0 + u0, x0 + u1, y0 + v0, y0 + v1, z0, z1, r)

    # walls: the niche's front wall east of the opening, full height, the lintel over the opening (the WC)
    r = rng.random()
    B("_Waende", "Putz", WP, W, YI, NICHE, 0, H, r)
    B("_Waende", "Putz", 0, WP, YI, NICHE, LIN, H, r)
    for _ in range(3):                               # the draws of the low wall and its two panes (till #63)
        rng.random()

    # niche: one sliding leaf on one track, built open in front of the front wall; it rolls west over the
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

    # the WC: the toilet on the south wall west of the shower, Taubenblau tiles on the south wall up to the glass
    # and on the west wall
    hc.toilet(c, x0 + HALF / 2, y0, 0, 1)
    hc.wainscot(c, 0.0, x0, x0 + XS, y0, y0 + YI, None, sides="sw")

    # walk-in shower (#63, as the Duschbad's): limestone on the east wall and on the shower's parts of the south wall
    # and the front wall, head and drain, the pane on its west side from the south wall's tiles
    hc.limestone(c, False, x0 + W, -1, y0, y0 + YI, 0.018, CLAD, rng)
    hc.limestone(c, True, y0, 1, x0 + XS + 0.005, x0 + W - ST, 0.018, CLAD, rng)
    hc.limestone(c, True, y0 + YI, -1, x0 + XS + 0.005, x0 + W - ST, 0.018, CLAD, rng)
    hc.shower(c, x0 + XS, x0 + W, y0, y0 + YI, [(x0 + XS, y0 + 0.012, x0 + XS, y0 + GL)], (x0 + W - ST, y0 + HY, -1, 0),
              tray=False)

    # Waschbecken einzeln (#63) on the north wall in the NW corner, west of the north window, a mirror above it
    hc.waschbecken(c, x0 + BX, y0 + D, 0, -1, BW, BD, 1, rng=random.Random(rng.random()))
    hc.wood_mirror(c, x0 + BX, y0 + D, 0, -1, MW, MH, MF, MZ, rng)

    floor(c, x0, y0)
    hc.restream(st, OLD_DRAWS)
    f, front = 0.06, tc + LT / 2                    # front: the sliding leaf's room face
    ba, bb, ma, mb = BX - BW / 2, BX + BW / 2, BX - MW / 2, BX + MW / 2
    return [((XS, 0.05, 2.10), (W, 0.05, 2.10), f"Dusche {cm(XS, W)}"),
            ((XS - 0.05, 0, 2.10), (XS - 0.05, GL, 2.10), f"Glas {cm(0, GL)}"),
            ((XS - 0.05, GL, 2.10), (XS - 0.05, YI, 2.10), f"Einstieg {cm(GL, YI)}"),
            ((0, NICHE + 0.35, 0.02), (WP, NICHE + 0.35, 0.02), f"Öffnung {cm(0, WP)}"),
            ((WP - 0.08, 0, 0.02), (WP - 0.08, YI, 0.02), f"{cm(0, YI)} tief"),
            ((ba, D - BD - 0.05, 0.85), (bb, D - BD - 0.05, 0.85), f"HWB {cm(ba, bb)}"),
            ((ma, D - 0.06, MZ + MH + 0.05), (mb, D - 0.06, MZ + MH + 0.05), f"Spiegel {cm(ma, mb)} × {cm(0, MH)}"),
            ((0, 1.80, LIN + 0.25), (W, 1.80, LIN + 0.25), f"Raumbreite {cm(0, W)}"),   # the room (request
            ((W - 0.30, 0, LIN + 0.25), (W - 0.30, D, LIN + 0.25), f"Raumtiefe {cm(0, D)}")]   # 2026-11-25)


def floor(c, x0, y0):
    """The room's floor, last and from its own generator (the parts before keep their rnd): a limestone strip
    HALF wide along the west wall from the south wall to the north wall and limestone in the rest of the niche
    (#61, own generator), oak elsewhere; slabs and planks as the house's floor_cover(), none under the niche's
    front wall. A dark base under the joints (in the house inside EG_Boden)."""
    rng = random.Random(7)
    wall = (x0 + WP, x0 + W, y0 + NICHE - NW, y0 + NICHE)
    hc.box(c, c + "_Boden", "Fuge", x0, x0 + W, y0, y0 + D, 0.0, 0.002, rng.random())
    hc.tiles(c, c + "_Bodenbelag", "Kalkstein", x0, x0 + HALF, y0, y0 + D, 0.002, 0.018, [0.5, 0.4, 0.55, 0.45],
             (0.35, 0.8), 0.006, [], rng)
    hc.tiles(c, c + "_Bodenbelag", "Eiche", x0 + HALF, x0 + W, y0 + NICHE, y0 + D, 0.002, 0.014, [0.2], (1.2, 2.4),
             0.003, [], rng)
    hc.tiles(c, c + "_Bodenbelag", "Kalkstein", x0 + HALF, x0 + W, y0, y0 + NICHE, 0.002, 0.018,       # the niche's east
             [0.5, 0.4, 0.55, 0.45], (0.35, 0.8), 0.006, [wall], random.Random(61))               # part to the leaf line
