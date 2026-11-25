"""Frechenlehen – the Schrankbett (issue #7): a wall bed in the Yoga room (OG, NW room) that folds up
into its case, as a sub-model (web/schrankbett.html). Agreed with Till 2026-11-13: lying area 2.00 long,
above the bed only a Blende up to the ceiling (the room is 2.20 high, the bed folded up 2.08), spruce
like the other OG furniture (assumed). Request 2026-11-25: moved from the south wall (by the Yoga door)
to the opposite wall, the north wall, and slid into the corner with the back outer wall (west): the
side cabinets are gone, the bed is 1.40 wide (lying area 1.40 x 2.00), its case just wide enough for it.
The west window behind it is gone, merged into the room's other west window (2026-11-25), so the case
stands against plain wall.

Local coordinates: x east from the west wall, y from the north wall into the room (southwards), z up
from the floor slab; the house (and the sub-model) get y mirrored: house y = y0 - y.

The bed is built folded down, an object of its own (<c>_Klappbett) with its PIVOT on the hinge axis and
CRANK = -90 deg about x (it folds up towards the north wall): the viewer folds it up and down on the lift
clock (slides.js). A simple pivot under a 2.20 ceiling: 20 cm from the head end, 8 cm above the
underside, so that the 2.04 long body swings clear of the floor, the case's back and the Blende
(tests/test_core.py sweeps it); folded up its underside (framed with six raised panels like the doors)
is flush with the case's front. Its two feet (<c>_Klappfuesse, same PIVOT and CRANK) fold onto the
underside meanwhile (FOLD: +90 deg about their hinge), so folded up they stand out by their thickness only.

Pure Python like house_core.py, which imports this module: build_furniture() calls schrankbett_neu() at
SCHRANKBETT_AT (case: furniture OG_Moebel; the bed OG_Klappbett); house_core.build_schrankbett() wraps it
at the origin with the pieces of the west wall and the north wall.
"""
import random
import house_core as hc

SCHRANKBETT_AT = (0.31, 12.485)              # house: the Yoga room's inner NW corner (west wall x north wall)
CEIL, FL = 2.20, 0.012                       # room height, floor finish
TOP = CEIL - 0.003                           # top of the case
D, YB, BT = 0.45, 0.005, 0.012               # case front (= the bed's underside folded up), back 5 mm off the wall, back panel
T = 0.019                                    # board thickness
BW, L = 1.44, 2.04                           # the bed: width (lying area 1.40, frame 2 cm round it) and length
NW = BW + 0.02                               # the niche: the bed plus 1 cm either side
W = NW + 2 * T                               # the case's width, from the west wall
A, DU, ZU = 0.20, 0.08, 0.16                 # pivot: from the head end, above the underside; underside down
YP, ZP = D - DU, ZU + DU                     # the pivot axis (folded up the underside is at y = D)
YH = YP - A                                  # the head end, down
BLENDE = 2.10                                # Blende underside: over the highest point of the swing (2.08)
MAT = 0.23                                   # mattress top above the underside
FR = 0.008                                   # the underside's frame: proud of its board


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def waende(c, dx, dy):
    """The sub-model's pieces of the west wall (plain: from the window's north jamb, 10.94, 5 cm before the
    case) and the north wall; in the house build_og() builds them whole."""
    hc.wall(c, 0.0 + dx, 0.31 + dx, 10.94 + dy, 12.485 + dy, 0.0, CEIL, out=-1)
    hc.wall(c, 0.0 + dx, 2.60 + dx, 12.485 + dy, hc.D_OUT + dy, 0.0, CEIL, out=+1)


def schrankbett_neu(c="Schrankbett", x0=0.0, y0=0.0, z=0.0, walls=False):
    """The Schrankbett built into collection c with the Yoga room's inner NW corner at (x0, y0) on
    floor z; with walls (the sub-model) also the two wall pieces. Case and bed draw their rnd from
    this module's generator, the walls from the global stream. Returns the dimension lines
    (sub-model coordinates)."""
    if walls:
        waende(c, x0 - SCHRANKBETT_AT[0], y0 - SCHRANKBETT_AT[1])
    rng = random.Random(16)
    B = lambda o, m, xa, xb, ya, yb, za, zb: hc.box(c, o, m, x0 + xa, x0 + xb, y0 - yb, y0 - ya, z + za, z + zb,
                                                    rng.random())
    o = c + "_Moebel"
    B(o, "FichteZ", 0.0, W, YB, YB + BT, FL, TOP)                                 # back, the whole width
    for xa in (0.0, W - T):
        B(o, "FichteZ", xa, xa + T, YB + BT, D, FL, TOP)                            # sides, to the front
    for fa, fb in ((T, T + 0.008), (W - T - 0.008, W - T)):                       # hinge fittings on their inner faces
        B(o, "Metall", fa, fb, YP - 0.04, YP + 0.04, ZP - 0.04, ZP + 0.04)
    B(o, "FichteX", T, W - T, YB + BT, D - T, TOP - T, TOP)                         # top, behind the Blende
    B(o, "FichteX", T, W - T, D - T, D, BLENDE, TOP)                                # Blende

    # the bed, folded down: underside, frame, slatted base, mattress, duvet, pillows
    o = c + "_Klappbett"
    xa, xb = T + 0.01, T + 0.01 + BW
    yf = YH + L                                                                     # foot end
    Z = lambda w: ZU + w                                                            # height above the underside
    # underside, the case's face folded up: framed with six raised panels like the doors
    # (request 2026-11-13): board, frame 8 mm proud of it, fields raised 4 mm in the openings
    B(o, "FichteY", xa, xb, YH, yf, Z(FR), Z(0.02))                                 # board
    xm, F = (xa + xb) / 2, 0.10                                                     # middle stile, frame width
    for sa, sb in ((xa, xa + F), (xm - F / 2, xm + F / 2), (xb - F, xb)):
        B(o, "FichteY", sa, sb, YH, yf, Z(0.0), Z(FR))                              # stiles, full length
    rails = [YH + k * (L - F) / 3 for k in range(4)]                                # rails at the ends, two between
    for ca, cb in ((xa + F, xm - F / 2), (xm + F / 2, xb - F)):
        for ra in rails:
            B(o, "FichteX", ca, cb, ra, ra + F, Z(0.0), Z(FR))
        for ra, rb in zip(rails, rails[1:]):
            B(o, "FichteY", ca + 0.05, cb - 0.05, ra + F + 0.05, rb - 0.05, Z(FR / 2), Z(FR))   # raised field
    for xs in (xa, xb - 0.02):
        B(o, "FichteY", xs, xs + 0.02, YH, yf, Z(0.02), Z(0.16))                    # side rails
    for ys in (YH, yf - 0.02):
        B(o, "FichteX", xa + 0.02, xb - 0.02, ys, ys + 0.02, Z(0.02), Z(0.16))      # head and foot boards
    B(o, "FichteX", xa + 0.02, xb - 0.02, YH + 0.02, yf - 0.02, Z(0.03), Z(0.05))   # slatted base
    B(o, "Leinen", xa + 0.02, xb - 0.02, YH + 0.02, yf - 0.02, Z(0.05), Z(MAT))     # one mattress 1.40 x 2.00
    for k in range(2):
        pm = xa + 0.02 + (k + 0.5) * (BW - 0.04) / 2                                # pillows: one per half
        B(o, "Bettwaesche", pm - 0.25, pm + 0.25, YH + 0.06, YH + 0.41, Z(MAT), Z(MAT + 0.08))
    B(o, "Bettwaesche", xa + 0.03, xb - 0.03, YH + 0.45, yf - 0.03, Z(MAT), Z(MAT + 0.04))   # duvet
    hc.PIVOT[o], hc.CRANK[o] = (x0 + T, y0 - YP, z + ZP), ((1, 0, 0), -90)
    # the two feet at the foot end, an object of their own on the bed's axis: hinged at the underside
    # (their head-side face), they fold flat onto it (FOLD +90 deg, mirrored) as the bed goes up (request 2026-11-13)
    f = c + "_Klappfuesse"
    for xs in (xa + 0.10, xb - 0.16):
        B(f, "FichteZ", xs, xs + 0.06, yf - 0.06, yf - 0.03, FL, ZU)
    hc.PIVOT[f], hc.CRANK[f] = hc.PIVOT[o], hc.CRANK[o]
    hc.FOLD[f] = ((x0 + T, y0 - (yf - 0.06), z + ZU), (1, 0, 0), 90)

    # dimension lines (sub-model coordinates: y mirrored), the drawing's numbers
    f, yd = 0.02, -(D + 0.05)                                                       # just before the case's front
    return [((0.0, yd, TOP + f), (W, yd, TOP + f), f"Schrankbett {cm(0, W)}"),
            ((T, yd, BLENDE - 0.05), (W - T, yd, BLENDE - 0.05), f"Nische {cm(0, NW)}"),   # under the Blende
            ((W + 0.06, 0.0, TOP), (W + 0.06, -D, TOP), f"Tiefe {cm(0, D)}"),
            ((W + 0.06, -D, 0.0), (W + 0.06, -D, CEIL), f"Raumhöhe {cm(0, CEIL)}"),
            ((W - T - 0.20, -D - 0.02, BLENDE), (W - T - 0.20, -D - 0.02, TOP), f"Blende {cm(BLENDE, TOP)}"),
            ((xa + 0.02, -yf - 0.10, Z(MAT)), (xb - 0.02, -yf - 0.10, Z(MAT)), f"Liegefläche {cm(0, BW - 0.04)}"),
            ((xb + 0.10, -YH - 0.02, Z(MAT)), (xb + 0.10, -yf + 0.02, Z(MAT)), cm(0, 2.0)),
            ((xb + 0.30, 0.0, 0.05), (xb + 0.30, -yf, 0.05), f"ausgeklappt {cm(0, yf)} ab Wand"),
            ((xb + 0.10, -yf, 0.0), (xb + 0.10, -yf, Z(MAT)), f"Liegehöhe {cm(0, Z(MAT))}")]
