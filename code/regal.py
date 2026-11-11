"""Frechenlehen – "Schrank im Büro": the Tegernsee bookcase (input/2026-11-11 input/regal_tegernsee.jpeg,
2.38 m high, elements 94 / 94 / 94 / 52) around the east window of the Bibliothek (the Büro end), as a
sub-model (web/regal.html), after the agreed drawing input/2026-11-11 input/buero_regal_v2.svg
(generator buero_regal_svg.py beside it). Looking at the window: a 94 column left (north), the middle
94 split into a base below the window (cabinet + open compartment, top 5 cm under the sill) and a
bridge above it (frieze + cornice: only 38 cm over the head), a 94 column right (south, the mirror of
the left one; the 52 vitrine is not built in). Depths estimated from the photo: 42, the middle base
48 (it stands forward in the photo); shelf heights after the photo too. The Büro door moves west so
that, opened 90 deg, it stands clear of the right column.

Pure Python like house_core.py, which imports this module: build_furniture() calls regal_neu() at
REGAL_AT (the furniture object EG_Moebel, stage "Eingerichtet"); house_core.build_regal() wraps it at
the origin with the pieces of the three walls around it (east wall with the window, north wall with
the balcony door, Flur wall with the Büro door) as the Blueprint of web/regal.html. The openings are
defined once here (FENSTER, BALKONTUER, TUER) and build_eg() uses them for the house's walls.
"""
import random
import house_core as hc

REGAL_AT = (14.575, 8.876)                   # house: the Bibliothek's inner SE corner (east wall x Flur wall)
E, EO = 14.575, 14.885                       # east wall: inner / outer face
FS, FSS = 8.876, 8.576                       # Flur wall: Bibliothek face / Windfang face
FN, FNO = 12.473, 12.887                     # north wall: inner / outer face
X0 = 12.60                                   # sub-model: west end of the north and Flur wall pieces
FENSTER = (10.315, 11.214, 1.0, 2.0, "W", 1)       # east window (plan: 90 wide), shutters
BALKONTUER = (12.867, 13.766, 0, 2.0, "FD", 1)    # north french door, shutters
# Büro door: 106 wide, hinged east, opened 90 deg into the Bibliothek. Moved 50 cm west of the
# plan's place (13.517 .. 14.575): its open leaf (east face 2.5 cm west of the jamb) then stands
# 10.5 cm, its lever 8 cm in front of the right column (drawing v2: 46 cm, 6.5 cm air - too little
# for a lever)
SHIFT = 0.50
TUER = (13.517 - SHIFT, 14.575 - SHIFT, 1, "b", False)

RH, BW, D, DM = 2.38, 0.94, 0.42, 0.48       # height, element width, depth, middle base depth
M0 = (FENSTER[0] + FENSTER[1]) / 2 - BW / 2  # the middle element, centred on the window
M1, N1, S0 = M0 + BW, M0 + 2 * BW, M0 - BW   # its north edge, the north column's, the south column's start
XB = E - 0.005                               # back of the carcass, 5 mm off the wall
XF, XFM = E - D, E - DM                      # fronts: columns and bridge / middle base
T = 0.025                                    # board thickness
PLINTH, CAB, SHELVES, TOP = 0.10, 0.66, (1.03, 1.46, 1.83), 2.11   # after the photo (left bay)
BASE, BRIDGE, CORN, CO = 0.95, 2.02, 2.24, 0.03   # base top, bridge underside, cornice bottom, overhang


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def waende(c, dx, dy):
    """The sub-model's pieces of the three walls (in the house build_eg() builds them whole)."""
    H = hc.Z_EG_TOP
    hc.wall(c, E + dx, EO + dx, FSS + dy, FN + dy, 0.0, H, [(FENSTER[0] + dy, FENSTER[1] + dy, *FENSTER[2:])], out=+1)
    hc.wall(c, X0 + dx, EO + dx, FN + dy, FNO + dy, 0.0, H, [(BALKONTUER[0] + dx, BALKONTUER[1] + dx, *BALKONTUER[2:])],
            out=+1)
    hc.interior(c, X0 + dx, E + dx, FSS + dy, FS + dy, [(TUER[0] + dx, TUER[1] + dx, *TUER[2:])])


def regal_neu(c="Regal", x0=0.0, y0=0.0, walls=False):
    """The bookcase built into collection c with the Bibliothek's inner SE corner at (x0, y0); with
    walls (the sub-model) also the three wall pieces around it. The bookcase draws its rnd from this
    module's generator, the walls from the global stream (as everywhere in the house). Returns the
    dimension lines (sub-model coordinates)."""
    dx, dy = x0 - REGAL_AT[0], y0 - REGAL_AT[1]
    if walls:
        waende(c, dx, dy)
    rng = random.Random(14)
    o = c + "_Moebel"
    B = lambda m, xa, xb, ya, yb, za, zb, r=None: hc.box(c, o, m, xa + dx, xb + dx, ya + dy, yb + dy, za, zb,
                                                     rng.random() if r is None else r)

    def doors(xf, ya, yb, za, zb):
        """Two framed doors with a raised field and an iron knob each, in front of the carcass."""
        h = (yb - ya) / 2
        for k in range(2):
            a, b = ya + k * h + 0.0015, ya + (k + 1) * h - 0.0015
            B("NussZ", xf - 0.02, xf, a, b, za, zb)
            B("NussX", xf - 0.028, xf - 0.02, a + 0.07, b - 0.07, za + 0.07, zb - 0.07)
            yk = b - 0.04 if k == 0 else a + 0.04
            B("Eisen", xf - 0.045, xf - 0.02, yk - 0.008, yk + 0.008, zb - 0.09, zb - 0.074, 0.5)

    def books(xf, ya, yb, z, top):
        """A row of books of random size, front-aligned 3 cm behind the shelf edge, some gaps."""
        y = ya + 0.01
        while True:
            if rng.random() < 0.08:
                y += rng.uniform(0.04, 0.10)
            w, h, d = rng.uniform(0.02, 0.05), rng.uniform(0.19, min(0.30, top - z - 0.02)), rng.uniform(0.17, 0.25)
            if y + w > yb - 0.01:
                break
            B("Buecher", xf + 0.03, xf + 0.03 + d, y, y + w, z + 0.001, z + h)
            y += w + 0.002

    def carcass(xf, ya, yb, top):
        """Sides, back, recessed plinth and bottom board of one element up to `top`."""
        for a, b in ((ya, ya + T), (yb - T, yb)):
            B("NussZ", xf, XB, a, b, 0.0, top)
        B("NussZ", XB - 0.012, XB, ya + T, yb - T, PLINTH, top)
        B("NussX", xf + 0.01, xf + 0.03, ya + T, yb - T, 0.0, PLINTH)
        B("NussX", xf, XB - 0.012, ya + T, yb - T, PLINTH, PLINTH + T)

    for ya, yb in ((S0, M0), (M1, N1)):                                     # the two columns
        carcass(XF, ya, yb, CORN)
        doors(XF, ya + T, yb - T, PLINTH + 0.03, CAB - 0.025)
        levels = (CAB,) + SHELVES + (TOP,)
        for z in levels:
            B("NussX", XF + 0.005, XB - 0.012, ya + T, yb - T, z - T, z)       # cabinet top, shelves, top board
        for z, top in zip(levels, levels[1:]):
            books(XF + 0.005, ya + T, yb - T, z, top - T)
        B("NussX", XF, XF + 0.02, ya + T, yb - T, TOP, CORN)                # frieze
    carcass(XFM, M0, M1, BASE - T)                                          # the middle base under the window
    doors(XFM, M0 + T, M1 - T, PLINTH + 0.03, 0.49 - T)
    B("NussX", XFM + 0.005, XB - 0.012, M0 + T, M1 - T, 0.49 - T, 0.49)
    books(XFM + 0.005, M0 + T, M1 - T, 0.49, BASE - T)
    B("NussX", XFM, XB, M0, M1, BASE - T, BASE)                             # its top, 5 cm under the sill
    B("NussX", XF, XB, M0, M1, BRIDGE, BRIDGE + T)                          # the bridge over the window
    B("NussX", XF, XF + 0.02, M0, M1, BRIDGE + T, CORN)
    B("NussZ", XB - 0.012, XB, M0, M1, BRIDGE + T, CORN)
    r = rng.random()                                                        # stepped cornice over all three
    B("NussX", XF - CO / 2, XB, S0 - CO / 2, N1 + CO / 2, CORN, CORN + 0.06, r)
    B("NussX", XF - CO, XB, S0 - CO, N1 + CO, CORN + 0.06, RH, r)

    # dimension lines (sub-model coordinates), the drawing's numbers
    S = lambda xa, ya, za, xb, yb, zb, s: ((xa - E, ya - FS, za), (xb - E, yb - FS, zb), s)
    xd, f, wa, wb = XF - 0.06, 0.02, FENSTER[0], FENSTER[1]
    lf = TUER[1] - 0.025                                                    # the open leaf's east face
    return [S(xd, FS, f, xd, S0, f, f"{cm(FS, S0)} frei"),
            S(xd, S0, f, xd, M0, f, f"Säule {cm(S0, M0)}"),
            S(xd, M0, f, xd, M1, f, f"Mitte {cm(M0, M1)}"),
            S(xd, M1, f, xd, N1, f, f"Säule {cm(M1, N1)}"),
            S(xd, N1, f, xd, FN, f, f"{cm(N1, FN)} frei"),
            S(E - 0.06, wa, 1.5, E - 0.06, wb, 1.5, f"Fenster {cm(wa, wb)}"),
            S(XFM - 0.06, M0 + 0.15, 0.0, XFM - 0.06, M0 + 0.15, BASE, f"Unterteil {cm(0, BASE)}"),
            S(XF - 0.06, M0 + 0.15, BRIDGE, XF - 0.06, M0 + 0.15, RH, f"Brücke {cm(BRIDGE, RH)}"),
            S(XF - 0.06, N1 - 0.15, 0.0, XF - 0.06, N1 - 0.15, RH, f"Höhe {cm(0, RH)}"),
            S(XF, N1 - 0.10, RH + 0.01, E, N1 - 0.10, RH + 0.01, f"Tiefe {cm(XF, E)}"),
            S(XFM, M1 - 0.10, BASE + 0.01, E, M1 - 0.10, BASE + 0.01, cm(XFM, E)),
            S(TUER[0], FS + 0.05, f, TUER[1], FS + 0.05, f, f"Tür {cm(TUER[0], TUER[1])}"),
            S(lf, FS + 0.9, 1.05, XF, FS + 0.9, 1.05, ("%.1f Luft" % ((XF - lf) * 100)).replace(".", ",")),
            S(BALKONTUER[1], FN - 0.10, 0.30, XF, FN - 0.10, 0.30, f"{cm(BALKONTUER[1], XF)} frei")]
