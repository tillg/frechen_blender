"""Frechenlehen – the Gästebad im 1. Stock (issue #18) as a sub-model (web/gaestebad.html): the OG Bad at
the end of the Flur (NW; the architect's "Bad 6,98 m²" with "WC 2,26 m²"), split along its south wall
like the EG Gäste-WC below it (code/gaeste_wc.py): a 10 cm partition over the EG one; west of it an open
WC niche (no wall, no door; toilet centred on its south wall, facing north; Taubenblau tiles), east of it
a walk-in shower 115 wide, long to 5 cm short of the Flur door's leaf (open flat against the east wall),
a 65 cm glass panel on its north edge from the east wall, the rest open; the Waschbecken doppelt 120 in
the middle of the north wall under a mirror 140 x 85 in a 10 cm wooden frame (like the OG Flur's).

Pure Python like house_core.py, which imports this module: build_sanitary() calls gaestebad_neu() at
GAESTEBAD_AT on the OG floor, build_og() takes the Flur door (TUER) from here; house_core.build_gaestebad()
wraps it at the origin with the pieces of the room's four walls (walls=True) as the Blueprint of
web/gaestebad.html. The floor stays the house's limestone (BATHS_OG).
"""
import random
import house_core as hc
import gaeste_wc

GAESTEBAD_AT = (0.31, 5.46)                  # house: the room's inner SW corner
WI, WO, YS, YN = 0.31, 2.57, 5.46, 8.57      # room: west and east (Flur wall) faces, south and north faces
PA, PB = gaeste_wc.PA, gaeste_wc.PB          # partition, over the EG Gäste-WC's
YP = 6.54                                    # its north end: the niches 108 deep
TUER = (7.66, 8.47)                          # Flur door in the east wall, hinged south, open flat into the Bad
SN = 6.85                                    # shower's north edge: 5 cm short of the open leaf (y 6.906)
GA = 1.92                                    # glass GA .. WO (65), open PB .. GA (50)
TX = (WI + PA) / 2                           # toilet axis: centred in the niche
BX = (WI + WO) / 2                           # basin and mirror: the middle of the north wall
BW, BD = 1.20, 0.47                          # Waschbecken doppelt
MW, MH, MF, MZ = 1.40, 0.85, 0.10, 1.17      # mirror: outer width x height, frame width, bottom


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def waende(c, dx, dy):
    """The sub-model's pieces of the room's four walls: west (outer wall, two windows), south, east
    (Flur, with the door) and north; in the house build_og() builds them whole."""
    H, zo = hc.Z_OG_TOP - hc.Z_OG, hc.Z_OG
    hc.wall(c, 0.0 + dx, WI + dx, 5.12 + dy, 8.86 + dy, 0.0, H,
            [(5.72 + dy, 6.32 + dy, 4.18 - zo, 4.78 - zo, "W"), (6.77 + dy, 7.76 + dy, 0.75, H, "W")], out=-1)
    hc.wall(c, WI + dx, 2.71 + dx, 5.12 + dy, YS + dy, 0.0, H)
    hc.interior(c, WO + dx, 2.71 + dx, YS + dy, YN + dy, [(TUER[0] + dy, TUER[1] + dy, -1, "a")], 0.0, H)
    hc.interior(c, WI + dx, 2.71 + dx, YN + dy, 8.86 + dy, (), 0.0, H)


def gaestebad_neu(c="Gaestebad", x0=0.0, y0=0.0, z=0.0, walls=False):
    """The Gästebad built into collection c with the room's inner SW corner at (x0, y0) on floor z; with
    walls (the sub-model) also the four wall pieces. Partition and mirror draw their rnd from this
    module's generator, toilet and shower from the global stream (as everywhere in the house), tiles
    and basin from their own. Returns the dimension lines (sub-model coordinates)."""
    dx, dy = x0 - GAESTEBAD_AT[0], y0 - GAESTEBAD_AT[1]
    if walls:
        waende(c, dx, dy)
    rng = random.Random(18)
    H = hc.Z_OG_TOP - hc.Z_OG
    hc.box(c, c + "_Waende", "Putz", PA + dx, PB + dx, YS + dy, YP + dy, z, z + H, rng.random())   # partition

    # north wall: the basin in the middle, the mirror above it
    hc.waschbecken(c, BX + dx, YN + dy, 0, -1, BW, BD, 2, z=z)
    hc.wood_mirror(c, BX + dx, YN + dy, 0, -1, MW, MH, MF, z + MZ, rng)
    for k in range(4):                                   # four Wandlampen over it, one per quarter of its width (#19)
        hc.wandlampe(c, BX - MW / 2 + MW * (k + 0.5) / 4 + dx, YN + dy, 0, -1, z + hc.WANDLAMPE_SPIEGEL_H)
    hc.wandlampe(c, WI + dx, (6.32 + 6.77) / 2 + dy, 1, 0, z + hc.WANDLAMPE_SPIEGEL_H)   # west wall: between the windows
    # south wall: the shower east of the partition, the WC niche west of it (tiles on its three walls)
    hc.shower(c, PB + dx, WO + dx, YS + dy, SN + dy, [(GA + dx, SN + dy, WO + dx, SN + dy)],
              ((GA + WO) / 2 + dx, YS + dy, 0, 1), z=z)
    hc.toilet(c, TX + dx, YS + dy, 0, 1, z=z)
    hc.wainscot(c, z, WI + dx, PA + dx, YS + dy, YP + dy, (WI + dx, PA + dx))

    # dimension lines (sub-model coordinates)
    S = lambda xa, ya, za, xb, yb, zb, s: ((xa - GAESTEBAD_AT[0], ya - GAESTEBAD_AT[1], za),
                                           (xb - GAESTEBAD_AT[0], yb - GAESTEBAD_AT[1], zb), s)
    f, top = 0.02, 2.10
    ba, bb = BX - BW / 2, BX + BW / 2
    ma, mb = BX - MW / 2, BX + MW / 2
    return [S(WI, YS + 0.05, top, PA, YS + 0.05, top, f"WC {cm(WI, PA)}"),
            S(PA, YS + 0.05, top, PB, YS + 0.05, top, cm(PA, PB)),
            S(PB, YS + 0.05, top, WO, YS + 0.05, top, f"Dusche {cm(PB, WO)} × {cm(YS, SN)}"),
            S(WO - 0.05, YS, top, WO - 0.05, SN, top, cm(YS, SN)),
            S(PA - 0.05, YS, f, PA - 0.05, YP, f, cm(YS, YP)),
            S(PB, SN + 0.05, f, GA, SN + 0.05, f, f"{cm(PB, GA)} offen"),
            S(GA, SN + 0.05, f, WO, SN + 0.05, f, f"Glas {cm(GA, WO)}"),
            S(WI, YS + 0.80, f, TX, YS + 0.80, f, cm(WI, TX)),
            S(TX, YS + 0.80, f, PA, YS + 0.80, f, cm(TX, PA)),
            S(WI, YN - BD - 0.25, f, ba, YN - BD - 0.25, f, cm(WI, ba)),
            S(ba, YN - BD - 0.25, f, bb, YN - BD - 0.25, f, f"Waschbecken {cm(ba, bb)}"),
            S(bb, YN - BD - 0.25, f, WO, YN - BD - 0.25, f, cm(bb, WO)),
            S(ma, YN - 0.06, MZ + MH + 0.05, mb, YN - 0.06, MZ + MH + 0.05, f"Spiegel {cm(ma, mb)} × {cm(0, MH)}"),
            S(ma - 0.05, YN - 0.06, 0.0, ma - 0.05, YN - 0.06, MZ, f"UK {cm(0, MZ)}"),
            S(WO - 0.05, TUER[0], f, WO - 0.05, TUER[1], f, f"Tür {cm(*TUER)}"),
            S(WI, SN + 0.45, top, WO, SN + 0.45, top, cm(WI, WO)),
            S(WI + 0.30, YS, top, WI + 0.30, YN, top, cm(YS, YN))]
