"""Frechenlehen – the Gästebad im 1. Stock (issue #18) as a sub-model (web/gaestebad.html): the OG Bad at
the end of the Flur (NW; the architect's "Bad 6,98 m²" with "WC 2,26 m²"). Issue #32: coming in through the
Flur door (east wall) one faces the back wall (west, the outer wall): on the left, in the SW corner, a
walk-in shower 101 x 140 (west wall to the glass, south wall to the tub) on the room's limestone floor, its
back (west) and side (south) wall in limestone to 2.0, the head on the south wall; to its right a bathtub
170 x 75 built in along the back wall under the big window (rim 58 below its 75 sill: lying in the tub,
back to the north wall, one looks out of it), a white ceramic shell in a limestone apron. Between shower
and WC a glass wall (where the partition over the EG Gäste-WC's stood, code/gaeste_wc.py) from the south
wall to YG, a little further forward than that wall reached; north of it the way into the shower. East of
it the open WC (toilet centred on the south wall, facing north; Taubenblau tiles on the south and east
wall); the Waschbecken einzeln 60 on the north wall between tub and door under a mirror 80 x 85 in a 10 cm
wooden frame (like the OG Flur's).

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
PA = gaeste_wc.PA                            # the glass between shower and WC: over the EG partition's west face
YG = 6.34                                    # its north end, 19 cm before the partition's (6.15); the way in north of it
TUER = (7.66, 8.47)                          # Flur door in the east wall, hinged south, open flat into the Bad
YT, XT, ZR = 6.87, WI + 0.75, 0.58           # tub: south edge (window from 6.77), east face, rim top
SN = YT - 0.015                              # shower's north edge: clear of the tub's limestone end
SX = (WI + PA) / 2                           # shower head: the middle of its south wall, on the slabs
CLAD, ST = 2.0, 0.012                        # shower walls: limestone to 2.0, slab face off the wall
WS = (5.72, 6.32, 4.18)                      # the west wall's small window: y span, sill (house z)
TX = (PA + WO) / 2                           # toilet axis: centred between glass and east wall
BX = 1.45                                    # basin and mirror: between the tub and the door
BW, BD = 0.60, 0.47                          # Waschbecken einzeln
MW, MH, MF, MZ = 0.80, 0.85, 0.10, 1.17      # mirror: outer width x height, frame width, bottom


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


def wanne(c, dx, dy, z, rng):
    """The bathtub (#32) built in along the west wall from YT to the north wall, XT - WI wide: a white
    ceramic shell (bottom at 0.15, rim walls 6 cm, a cap 2 cm high that overhangs the apron), its apron
    (east) and south end clad with limestone (hc.limestone), a chrome deck mixer with spout on the south
    rim, drain and overflow at that end (the back rest end is the north). Shell in <c>_Sanitaer, cladding
    in <c>_Fliesen."""
    o, r, R, cap = c + "_Sanitaer", rng.random(), 0.06, ZR - 0.02
    x0, x1, y0, y1 = WI + dx, XT + dx, YT + dy, YN + dy
    K = lambda xa, xb, ya, yb, za, zb: hc.box(c, o, "Keramik", xa, xb, ya, yb, z + za, z + zb, r)
    K(x0 + R, x1 - R, y0 + R, y1 - R, 0.015, 0.15)                                  # bottom
    K(x0, x0 + R, y0, y1, 0.015, cap); K(x1 - R, x1, y0, y1, 0.015, cap)           # rim walls: west, east
    K(x0 + R, x1 - R, y0, y0 + R, 0.015, cap); K(x0 + R, x1 - R, y1 - R, y1, 0.015, cap)   # south, north
    K(x1 - R, x1 + 0.014, y0 - 0.014, y1, cap, ZR)                                 # caps: east (over the apron),
    K(x0, x1 - R, y0 - 0.014, y0 + R, cap, ZR)                                     # south (over the end),
    K(x0, x0 + R, y0 + R, y1, cap, ZR); K(x0 + R, x1 - R, y1 - R, y1, cap, ZR)     # west, north
    hc.limestone(c, False, XT, 1, YT, YN, z + 0.015, z + cap, rng, dx, dy)         # apron
    hc.limestone(c, True, YT, -1, WI, XT + 0.012, z + 0.015, z + cap, rng, dx, dy)  # south end
    cx = (x0 + x1) / 2
    T = lambda p0, p1, prof: hc.turned(c, o, "Metall", (cx + p0[0], p0[1], z + p0[2]), (cx + p1[0], p1[1], z + p1[2]),
                                       prof, rnd=r)
    T((0, y0 + R + 0.12, 0.15), (0, y0 + R + 0.12, 0.153), [(0.025, 0), (0.025, 1)])                   # drain
    T((0, y0 + R, ZR - 0.10), (0, y0 + R + 0.003, ZR - 0.10), [(0.025, 0), (0.025, 1)])                # overflow
    ym = y0 + R / 2
    T((0, ym, ZR), (0, ym, ZR + 0.13), [(0.018, 0), (0.016, 1)])                                        # mixer,
    T((0, ym, ZR + 0.12), (0, ym + 0.16, ZR + 0.10), [(0.009, 0), (0.008, 1)])                          # spout,
    T((0, ym, ZR + 0.13), (0, ym - 0.03, ZR + 0.18), [(0.006, 0), (0.005, 1)])                          # lever


def gaestebad_neu(c="Gaestebad", x0=0.0, y0=0.0, z=0.0, walls=False):
    """The Gästebad built into collection c with the room's inner SW corner at (x0, y0) on floor z; with
    walls (the sub-model) also the four wall pieces. Mirror, shower walls and tub draw their rnd from this
    module's generators (the shower's limestone too); tiles and basin from their own. Returns the dimension
    lines (sub-model coordinates)."""
    dx, dy = x0 - GAESTEBAD_AT[0], y0 - GAESTEBAD_AT[1]
    if walls:
        waende(c, dx, dy)
    rng = random.Random(18)

    # north wall: the basin between tub and door, the mirror above it
    hc.waschbecken(c, BX + dx, YN + dy, 0, -1, BW, BD, 1, z=z)
    hc.wood_mirror(c, BX + dx, YN + dy, 0, -1, MW, MH, MF, z + MZ, rng)
    for k in range(2):                                   # two Wandlampen over it, one per half of its width (#19)
        hc.wandlampe(c, BX - MW / 2 + MW * (k + 0.5) / 2 + dx, YN + dy, 0, -1, z + hc.WANDLAMPE_SPIEGEL_H)
    hc.wandlampe(c, (WI + XT) / 2 + dx, YN + dy, 0, -1, z + hc.WANDLAMPE_SPIEGEL_H)   # over the tub's head end
    hc.wandlampe(c, WO + dx, (YS + YG) / 2 + dy, -1, 0, z + hc.WANDLAMPE_H)           # east wall: over the toilet
    # back wall: the shower in the SW corner (no tray: the limestone floor runs through; limestone on the west wall,
    # its small window left free above the sill, and on the south wall to the glass; the head on the slabs), the
    # tub north of it; south wall: the WC east of the glass
    sill = z + WS[2] - hc.Z_OG
    hc.limestone(c, False, WI, 1, YS, SN, z + 0.018, sill, rng, dx, dy)
    for ya, yb in ((YS, WS[0]), (WS[1], SN)):
        hc.limestone(c, False, WI, 1, ya, yb, sill, z + CLAD, rng, dx, dy)
    hc.limestone(c, True, YS, 1, WI + ST, PA - 0.005, z + 0.018, z + CLAD, rng, dx, dy)
    hc.shower(c, WI + dx, PA + dx, YS + dy, SN + dy, [(PA + dx, YS + dy, PA + dx, YG + dy)],
              (SX + dx, YS + ST + dy, 0, 1), z=z, tray=False)
    wanne(c, dx, dy, z, random.Random(32))
    hc.toilet(c, TX + dx, YS + dy, 0, 1, z=z)
    hc.wainscot(c, z, PA + 0.006 + dx, WO + dx, YS + dy, YG + dy, (WO + dx, WO + dx), sides="se")

    # dimension lines (sub-model coordinates)
    S = lambda xa, ya, za, xb, yb, zb, s: ((xa - GAESTEBAD_AT[0], ya - GAESTEBAD_AT[1], za),
                                           (xb - GAESTEBAD_AT[0], yb - GAESTEBAD_AT[1], zb), s)
    f, top = 0.02, 2.10
    ba, bb = BX - BW / 2, BX + BW / 2
    ma, mb = BX - MW / 2, BX + MW / 2
    return [S(WI, YS + 0.05, top, PA, YS + 0.05, top, f"Dusche {cm(WI, PA)} × {cm(YS, SN)}"),
            S(PA, YS + 0.05, top, WO, YS + 0.05, top, f"WC {cm(PA, WO)}"),
            S(PA + 0.05, YS, f, PA + 0.05, YG, f, f"Glas {cm(YS, YG)}"),
            S(PA - 0.05, YG, f, PA - 0.05, SN, f, f"Durchgang {cm(YG, SN)}"),
            S(PA, YS + 0.85, f, TX, YS + 0.85, f, cm(PA, TX)),
            S(TX, YS + 0.85, f, WO, YS + 0.85, f, cm(TX, WO)),
            S(WI + 0.45, YT, f, WI + 0.45, YN, f, f"Wanne {cm(YT, YN)} × {cm(WI, XT)}"),
            S(XT + 0.03, YT + 0.15, 0.0, XT + 0.03, YT + 0.15, ZR, f"Rand {cm(0, ZR)}"),
            S(WI, YN - BD - 0.25, f, ba, YN - BD - 0.25, f, cm(WI, ba)),
            S(ba, YN - BD - 0.25, f, bb, YN - BD - 0.25, f, f"Waschbecken {cm(ba, bb)}"),
            S(bb, YN - BD - 0.25, f, WO, YN - BD - 0.25, f, cm(bb, WO)),
            S(ma, YN - 0.06, MZ + MH + 0.05, mb, YN - 0.06, MZ + MH + 0.05, f"Spiegel {cm(ma, mb)} × {cm(0, MH)}"),
            S(ma - 0.05, YN - 0.06, 0.0, ma - 0.05, YN - 0.06, MZ, f"UK {cm(0, MZ)}"),
            S(WO - 0.05, TUER[0], f, WO - 0.05, TUER[1], f, f"Tür {cm(*TUER)}"),
            S(WI, YT + 0.35, top, WO, YT + 0.35, top, cm(WI, WO)),
            S(WI + 0.30, YS, top, WI + 0.30, YN, top, cm(YS, YN))]
