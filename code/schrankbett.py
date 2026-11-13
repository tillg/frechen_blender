"""Frechenlehen – the Schrankbett (issue #7): a 2 x 2 m wall bed in the Yoga room (OG, NW room) that
folds up into a Schrankwand on the south wall, as a sub-model (web/schrankbett.html). Agreed with Till
2026-11-13: where the bed stood (head at the south wall), lying area 2.00 x 2.00; from the west wall
to the Yoga door, a side cabinet either side of the bed, as deep as the bed is thick (45); above the
bed only a Blende up to the ceiling (the room is 2.20 high, the bed folded up 2.08). The left cabinet
covers part of the west window's reveal (accepted). Spruce like the other OG furniture (assumed).

The bed is built folded down, an object of its own (<c>_Klappbett) with its PIVOT on the hinge axis and
CRANK = 90 deg about x: the viewer folds it up and down on the lift clock (slides.js). A simple pivot
under a 2.20 ceiling: 20 cm from the head end, 8 cm above the underside, so that the 2.04 long body
swings clear of the floor, the carcass's back and the Blende (tests/test_core.py sweeps it); folded
up its underside (framed with six raised panels like the doors) is flush with the door fronts. Its two
feet (<c>_Klappfuesse, same PIVOT and CRANK) fold onto the underside meanwhile (FOLD: -90 deg about
their hinge), so folded up they stand out by their thickness only.

Pure Python like house_core.py, which imports this module: build_furniture() calls schrankbett_neu() at
SCHRANKBETT_AT (carcass: furniture OG_Moebel; the bed OG_Klappbett); house_core.build_schrankbett()
wraps it at the origin with the pieces of the west wall (window) and the south wall (Yoga door).
"""
import random
import house_core as hc

SCHRANKBETT_AT = (0.31, 8.86)                # house: the Yoga room's inner SW corner (west wall x south wall)
DOOR = (3.17, 4.15)                          # the Yoga door in the south wall (build_og), opening into the room
X1 = DOOR[0] - 0.07 - 0.005                  # the unit's east end: 5 mm off the door's architrave
W = X1 - SCHRANKBETT_AT[0]                   # its width (local coordinates from here on: x east, y north
CEIL, FL = 2.20, 0.012                       # from the corner, z up from the floor slab); room height, floor finish
TOP = CEIL - 0.003                           # top of the unit
D, YC, YB, BT = 0.45, 0.43, 0.005, 0.012     # door fronts, carcass front, back (5 mm off the wall), back panel
T, PLINTH = 0.019, 0.08                      # board thickness, plinth height
NW = 2.06                                    # the niche: the bed 2.04 plus 1 cm either side
SW = (W - NW) / 2                            # each side cabinet
BW = L = 2.04                                # the bed: width and length (frame 2 cm round the lying area)
A, DU, ZU = 0.20, 0.08, 0.16                 # pivot: from the head end, above the underside; underside down
YP, ZP = D - DU, ZU + DU                     # the pivot axis (folded up the underside is at y = D)
YH = YP - A                                  # the head end, down
BLENDE = 2.10                                # Blende underside: over the highest point of the swing (2.08)
MAT = 0.23                                   # mattress top above the underside
FR = 0.008                                   # the underside's frame: proud of its board


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def waende(c, dx, dy):
    """The sub-model's pieces of the west wall (window) and the south wall (Yoga door); in the house
    build_og() builds them whole."""
    hc.wall(c, 0.0 + dx, 0.31 + dx, 8.57 + dy, 10.60 + dy, 0.0, CEIL, [(8.96 + dy, 9.95 + dy, 0.75, CEIL, "W")], out=-1)
    hc.interior(c, 0.31 + dx, 5.30 + dx, 8.57 + dy, 8.86 + dy, [(DOOR[0] + dx, DOOR[1] + dx, 1, "b")], 0.0, CEIL)


def schrankbett_neu(c="Schrankbett", x0=0.0, y0=0.0, z=0.0, walls=False):
    """The Schrankbett built into collection c with the Yoga room's inner SW corner at (x0, y0) on
    floor z; with walls (the sub-model) also the two wall pieces. Carcass and bed draw their rnd from
    this module's generator, the walls from the global stream. Returns the dimension lines
    (sub-model coordinates)."""
    if walls:
        waende(c, x0 - SCHRANKBETT_AT[0], y0 - SCHRANKBETT_AT[1])
    rng = random.Random(16)
    B = lambda o, m, xa, xb, ya, yb, za, zb: hc.box(c, o, m, x0 + xa, x0 + xb, y0 + ya, y0 + yb, z + za, z + zb,
                                                    rng.random())
    o = c + "_Moebel"
    B(o, "FichteZ", 0.0, W, YB, YB + BT, FL, TOP)                                 # back, the whole width
    for a, b, h in ((0.0, SW, SW - 0.05), (W - SW, W, W - SW + 0.05)):           # the two side cabinets
        for xa in (a, b - T):
            B(o, "FichteZ", xa, xa + T, YB + BT, YC, FL, TOP)                       # sides
        B(o, "FichteX", a + T, b - T, YC - 0.04, YC - 0.02, FL, PLINTH)             # recessed plinth
        B(o, "FichteX", a + T, b - T, YB + BT, YC, PLINTH, PLINTH + T)              # bottom
        B(o, "FichteX", a + T, b - T, YB + BT, YC, TOP - T, TOP)                    # top
        B(o, "FichteZ", a + 0.002, b - 0.002, YC, D, PLINTH + 0.003, TOP - 0.003)   # door
        B(o, "Metall", h - 0.008, h + 0.008, D, D + 0.025, 0.95, 1.25)              # handle, by the niche
        fa, fb = (b, b + 0.008) if a == 0.0 else (a - 0.008, a)                    # hinge fitting on the niche face
        B(o, "Metall", fa, fb, YP - 0.04, YP + 0.04, ZP - 0.04, ZP + 0.04)
    B(o, "FichteX", SW, W - SW, YB + BT, YC, TOP - T, TOP)                          # over the niche
    B(o, "FichteX", SW, W - SW, YC, D, BLENDE, TOP)                                 # Blende

    # the bed, folded down: underside, frame, slatted base, two mattresses, duvet, pillows
    o = c + "_Klappbett"
    xa, xb = SW + 0.01, SW + 0.01 + BW
    yf = YH + L                                                                     # foot end
    Z = lambda w: ZU + w                                                            # height above the underside
    # underside, the Schrankwand's face folded up: framed with six raised panels like the doors
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
    for k in range(2):
        ma, mb = xa + 0.02 + k * 1.0, xa + 0.02 + (k + 1) * 1.0
        B(o, "Leinen", ma + 0.002 * k, mb - 0.002 * (1 - k), YH + 0.02, yf - 0.02, Z(0.05), Z(MAT))
        B(o, "Bettwaesche", (ma + mb) / 2 - 0.25, (ma + mb) / 2 + 0.25, YH + 0.06, YH + 0.41, Z(MAT), Z(MAT + 0.08))
    B(o, "Bettwaesche", xa + 0.03, xb - 0.03, YH + 0.45, yf - 0.03, Z(MAT), Z(MAT + 0.04))   # duvet
    hc.PIVOT[o], hc.CRANK[o] = (x0 + SW, y0 + YP, z + ZP), ((1, 0, 0), 90)
    # the two feet at the foot end, an object of their own on the bed's axis: hinged at the underside
    # (their head-side face), they fold flat onto it (FOLD -90 deg) as the bed goes up (request 2026-11-13)
    f = c + "_Klappfuesse"
    for xs in (xa + 0.10, xb - 0.16):
        B(f, "FichteZ", xs, xs + 0.06, yf - 0.06, yf - 0.03, FL, ZU)
    hc.PIVOT[f], hc.CRANK[f] = hc.PIVOT[o], hc.CRANK[o]
    hc.FOLD[f] = ((x0 + SW, y0 + yf - 0.06, z + ZU), (1, 0, 0), -90)

    # dimension lines (sub-model coordinates), the drawing's numbers
    f, yd = 0.02, D + 0.30
    return [((0.0, yd, f), (SW, yd, f), f"Schrank {cm(0, SW)}"),
            ((SW, yd, f), (W - SW, yd, f), f"Bett {cm(0, NW)}"),
            ((W - SW, yd, f), (W, yd, f), f"Schrank {cm(0, SW)}"),
            ((0.0, -0.05, TOP + 0.02), (W, -0.05, TOP + 0.02), f"Schrankwand {cm(0, W)}"),
            ((W + 0.06, 0.0, TOP), (W + 0.06, D, TOP), f"Tiefe {cm(0, D)}"),
            ((W + 0.06, D, 0.0), (W + 0.06, D, CEIL), f"Raumhöhe {cm(0, CEIL)}"),
            ((W / 2, D + 0.02, BLENDE), (W / 2, D + 0.02, TOP), f"Blende {cm(BLENDE, TOP)}"),
            ((xa + 0.02, yf + 0.10, Z(MAT)), (xb - 0.02, yf + 0.10, Z(MAT)), f"Liegefläche {cm(0, 2.0)}"),
            ((xb + 0.10, YH + 0.02, Z(MAT)), (xb + 0.10, yf - 0.02, Z(MAT)), cm(0, 2.0)),
            ((xa - 0.30, 0.0, 0.05), (xa - 0.30, yf, 0.05), f"ausgeklappt {cm(0, yf)} ab Wand"),
            ((xb + 0.10, yf, 0.0), (xb + 0.10, yf, Z(MAT)), f"Liegehöhe {cm(0, Z(MAT))}")]
