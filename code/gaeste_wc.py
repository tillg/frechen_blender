"""Frechenlehen – the Gäste-WC by the back hall (EG) as a sub-model (web/gaeste_wc.html), after the
agreed drawing input/2026-11-10 input/gaeste_wc_v3.svg (generator gaeste_wc_svg.py beside it) and the
Mallnitz photos of the same folder. The old WC (2.05 x 1.10 m) is split by a new 10 cm partition,
its east face flush with the old door's west jamb: in the west the WC with a new 76 opening in the
north wall, its leaf opened outward into the Flur (90 deg, hinged at the partition side: laid flat it
would cover the Garderobe's opening), the toilet centred on the south wall, Taubenblau tiles; in the
east the Garderobe, open to the Flur through the old 80 opening, with a bench from wall to wall, a
hook board, hooks and a hat shelf (garderobe mallnitz.jpeg). The WC's hand basin hangs outside, on
the Flur east wall between the WC wall and the Windfang door, tiles behind it and a mirror in a
wooden frame above.

Pure Python like house_core.py, which imports this module: build_eg() calls gaeste_wc_neu() at
WC_AT; house_core.build_gaeste_wc() wraps it at the origin as the Blueprint of web/gaeste_wc.html.
Positions are written in house coordinates (those of the drawing) and shifted by (x0, y0) - WC_AT,
as the basin lies outside the room. Like the Bad it brings walls of its own: the partition and the
WC's north wall (Bestand) with both openings; the floor stays the house's limestone.
"""
import math, random
import house_core as hc

WC_AT = (0.31, 5.475)                        # house: the old WC room's inner SW corner
WI, WO = 0.31, 2.358                         # room: west wall face, east face (= the Flur east wall's face)
YS, YN, YF = 5.475, 6.574, 6.723             # south wall face, north wall: room face, Flur face
PA, PB = 1.319, 1.419                        # partition; its east face = the old door's west jamb
DA, DB = 0.48, 1.24                          # new WC door opening (76), hinged at DB
GA, GB = 1.419, 2.218                        # old opening (80) to the Garderobe, no door
FWA, FWB = 7.408, 8.506                      # Windfang door's jambs; its architrave 7 cm
TX = (WI + PA) / 2                           # toilet axis: centred in the WC
TD = 0.70                                    # toilet depth incl. tiles (hc.toilet's seat; drawing: 69)
BW, BD = 0.40, 0.28                          # hand basin (hc.wc_basin), centred on the Flur wall piece
BM = (YF + FWA) / 2
MF, MGW, MGH, MZ = 0.07, 0.40, 0.60, 1.20    # mirror: frame width, glass width x height, frame bottom
BK, BZ = 0.35, 0.45                          # bench depth, seat top
HOOK_Z, SHELF_D, SHELF_Z, BOARD_TOP = 1.65, 0.28, 1.85, 1.90


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def gaeste_wc_neu(c="GaesteWC", x0=0.0, y0=0.0):
    """The Gäste-WC with Garderobe and the Flur basin, built into collection c with the old WC
    room's inner SW corner at (x0, y0). The north wall and the toilet draw their rnd from the global
    stream (as everywhere in the house), the tiles from wainscot()'s own, the rest from this
    module's generator. Returns the dimension lines (sub-model coordinates)."""
    dx, dy = x0 - WC_AT[0], y0 - WC_AT[1]
    rng = random.Random(12)
    H = hc.Z_EG_TOP
    B = lambda o, m, xa, xb, ya, yb, za, zb, r=None: hc.box(c, c + o, m, xa + dx, xb + dx, ya + dy, yb + dy, za, zb,
                                                         rng.random() if r is None else r)

    # walls: the partition; the north wall with the new WC door (outward, 90 deg) and the old
    # opening as an open passage to the Garderobe
    B("_Waende", "Putz", PA, PB, YS, YN, 0.0, H)
    hc.interior(c, WI + dx, WO + dx, YN + dy, YF + dy, [(DA + dx, DB + dx, 1, "b", False, "panel", "Innentuer",
                                                         c + "_WC_Tuer"), (GA + dx, GB + dx)])
    # the other two doors of the back hall, each leaf its own object so the viewer can swing it:
    # the back door (closed; in the west wall's opening) and the glazed Windfang door (open 90 deg
    # into the Flur; in the wall x 2.358 .. 2.657); both hinged north, so open they lie along the
    # back hall's north wall (request 2026-11-10)
    hc.back_door(c, dx, dy)
    hc.panel_door(c, "y", FWA + dy, FWB + dy, WO + dx, 2.657 + dx, 0.0, hc.DOOR_H, -1, "b", False, "glazed",
                  leaf=c + "_Windfangtuer")

    # WC: toilet centred on the south wall, Taubenblau tiles on its four walls (door left free)
    hc.toilet(c, TX + dx, YS + dy, 0, 1)
    hc.wainscot(c, 0.0, WI + dx, PA + dx, YS + dy, YN + dy, (DA + dx, DB + dx))

    # Flur east wall: hand basin, tiles behind it up to the Windfang door's architrave, mirror
    # 40 x 60 in a 7 cm wooden frame (2.5 cm deep), its glass set back in the frame
    hc.wc_basin(c, WO + dx, BM + dy, -1, 0, w=BW, d=BD, mirror=False)
    hc.wainscot(c, 0.0, WO + dx - 1.0, WO + dx, YF + dy, FWA - 0.07 + dy, None, sides="e")
    o, r = "_Sanitaer", rng.random()
    ya, yb, za, zb = BM - MGW / 2 - MF, BM + MGW / 2 + MF, MZ, MZ + MGH + 2 * MF
    B(o, "Kiefer", WO - 0.025, WO, ya, yb, za, za + MF, r)                                   # bottom, top
    B(o, "Kiefer", WO - 0.025, WO, ya, yb, zb - MF, zb, r)
    B(o, "Kiefer", WO - 0.025, WO, ya, ya + MF, za + MF, zb - MF, r)                         # sides
    B(o, "Kiefer", WO - 0.025, WO, yb - MF, yb, za + MF, zb - MF, r)
    B(o, "Spiegel", WO - 0.012, WO - 0.004, ya + MF, yb - MF, za + MF, zb - MF)

    # Garderobe after garderobe mallnitz.jpeg: old spruce; a bench from wall to wall (seat, apron,
    # end boards with a scrolled arm), the hook board above it with six iron hooks, the hat shelf on
    # three brackets
    o, r = "_Garderobe", rng.random()
    xf = WO - BK                                                                             # bench front
    B(o, "FichteY", xf, WO, YS, YN, BZ - 0.04, BZ, r)                                        # seat
    B(o, "FichteY", xf, xf + 0.02, YS + 0.025, YN - 0.025, BZ - 0.15, BZ - 0.04, r)          # apron
    B(o, "FichteZ", WO - 0.02, WO, YS, YN, BZ, BOARD_TOP, r)                                 # hook board
    B(o, "FichteY", WO - SHELF_D, WO, YS, YN, SHELF_Z, SHELF_Z + 0.03, r)                   # hat shelf (28 from the wall)
    P = lambda u, t, z: (u + dx, t + dy, z)                                                  # (x, z) profiles, t = y
    arm = [(xf + 0.01, BZ), (WO - 0.02, BZ), (WO - 0.02, BZ + 0.26)] + \
          [(xf + 0.09 + 0.08 * math.cos(math.pi * i / 8), BZ + 0.18 + 0.08 * math.sin(math.pi * i / 8))
           for i in range(9)]
    for ya_, yb_ in ((YS, YS + 0.025), (YN - 0.025, YN)):
        B(o, "FichteZ", xf + 0.01, WO - 0.02, ya_, yb_, 0.0, BZ - 0.04, r)                   # end board
        hc.prism(c, c + o, "FichteZ", P, arm, ya_, yb_, r)                                   # its arm
    bracket = [(WO - 0.02, SHELF_Z), (WO - 0.20, SHELF_Z)] + \
              [(WO - 0.02 - 0.18 * math.cos(math.pi / 2 * i / 6), SHELF_Z - 0.20 * math.sin(math.pi / 2 * i / 6))
               for i in range(1, 7)]
    for y in (YS + 0.06, (YS + YN) / 2, YN - 0.06):
        hc.prism(c, c + o, "FichteZ", P, bracket, y - 0.0125, y + 0.0125, r)
    for i in range(6):                                                                       # hooks
        y = YS + 0.10 + i * (YN - YS - 0.20) / 5
        B(o, "Eisen", WO - 0.12, WO - 0.02, y - 0.006, y + 0.006, HOOK_Z - 0.005, HOOK_Z + 0.007, 0.5)
        B(o, "Eisen", WO - 0.12, WO - 0.108, y - 0.006, y + 0.006, HOOK_Z + 0.007, HOOK_Z + 0.04, 0.5)

    # dimension lines (sub-model coordinates), the drawing's numbers
    S = lambda xa, ya_, za_, xb, yb_, zb_, s: ((xa - WC_AT[0], ya_ - WC_AT[1], za_), (xb - WC_AT[0], yb_ - WC_AT[1], zb_), s)
    f, ba, bb = 0.02, BM - BW / 2, BM + BW / 2
    return [S(WI, YS + 0.05, 2.30, PA, YS + 0.05, 2.30, f"WC {cm(WI, PA)}"),
            S(PA, YS + 0.05, 2.30, PB, YS + 0.05, 2.30, cm(PA, PB)),
            S(PB, YS + 0.05, 2.30, WO, YS + 0.05, 2.30, f"Garderobe {cm(PB, WO)}"),
            S(WI, YF + 0.05, f, DA, YF + 0.05, f, cm(WI, DA)),
            S(DA, YF + 0.05, f, DB, YF + 0.05, f, f"Tür {cm(DA, DB)}"),
            S(WI, YN - 0.25, f, TX, YN - 0.25, f, cm(WI, TX)),
            S(TX, YN - 0.25, f, PA, YN - 0.25, f, cm(TX, PA)),
            S(TX, YS + TD, f, TX, YN, f, f"{cm(YS + TD, YN)} frei"),
            S(PB, (YS + YN) / 2, f, xf, (YS + YN) / 2, f, f"{cm(PB, xf)} frei"),
            S(WO - BK / 2, YS, BZ + f, WO - BK / 2, YN, BZ + f, f"Bank {cm(0, BK)} × {cm(YS, YN)}"),
            S(DB, YF + 0.35, f, WO - BD - 0.01, YF + 0.35, f, f"{cm(DB, WO - BD - 0.01)} frei"),
            S(WO - BD - 0.06, YF, 0.85, WO - BD - 0.06, ba, 0.85, cm(YF, ba)),
            S(WO - BD - 0.06, ba, 0.85, WO - BD - 0.06, bb, 0.85, f"HWB {cm(ba, bb)}"),
            S(WO - BD - 0.06, bb, 0.85, WO - BD - 0.06, FWA, 0.85, cm(bb, FWA)),
            S(WO - 0.06, ya - 0.05, 0.0, WO - 0.06, ya - 0.05, MZ, f"UK {cm(0, MZ)}"),
            S(WO - 0.06, ya, zb + 0.05, WO - 0.06, yb, zb + 0.05, f"Spiegel {cm(ya, yb)} × {cm(za, zb)}")]
