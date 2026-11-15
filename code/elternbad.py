"""Frechenlehen – the Bad of Nadine & Till im 1. Stock (issues #3, #33) as a sub-model (web/elternbad.html): the OG
Bad between Waschküche (N) and Schlafzimmer (E), under the window of the south wall. The door to the Schlafzimmer at the
south end of the east wall (hinged south, open 90 deg into the Bad; 25 cm off the corner, so the open leaf with its
levers clears the Wandlampe left of the window). Along the back wall (west, opposite the door) two walk-in showers on
one strip 90 deep (#33): a head in each back corner (SW, NW), one pane per shower from its side wall towards the
middle, 60 clear between the panes (the way in), the room's limestone floor running through; the strip's walls clad
in limestone like the Bad Großeltern's, to 2.0, but on the north wall only to 1.20: that wall is the partition to the
Waschküche, whose top metre #30 glazes, so nothing on it reaches above 1.20. The toilet on the north wall between
the glass and the basin (Taubenblau tiles on the north wall and on the east wall down to the door); the Waschbecken
einzeln 60 on the east wall north of the door under a mirror 80 x 85 in a 10 cm wooden frame, two Wandlampen over it,
one left of the window (seen from inside).

Pure Python like house_core.py, which imports this module: build_sanitary() calls elternbad_neu() at
ELTERNBAD_AT on the OG floor, build_og() takes the door (TUER) from here, BATHS_OG the room (ROOM);
house_core.build_elternbad() wraps it at the origin with the pieces of the room's four walls (walls=True)
as the Blueprint of web/elternbad.html. The floor is the house's limestone (BATHS_OG); the sub-model lays the
same slabs itself.
"""
import random
import house_core as hc

ELTERNBAD_AT = (5.59, 0.40)                  # house: the room's inner SW corner
WI, WO, YS, YN = 5.59, 8.59, 0.40, 2.62      # room: west and east (Schlafzimmer wall) faces, south and north faces
ROOM = (WI, WO, YS, YN)
FENSTER = (6.84, 7.72)                       # the window in the south wall (build_og())
TUER = (0.65, 1.58)                          # door in the east wall, hinged south, open 90 deg into the Bad
XG = WI + 0.90                               # the showers' strip along the west wall: glass line
YM = (YS + YN) / 2                           # the middle of the west wall: the way in
PA, PB = YM - 0.30 - 0.012, YM + 0.30 + 0.012   # panes YS .. PA and PB .. YN: their rails (12) leave 60 clear
HU = 0.30                                    # shower heads: 30 from the south and north wall
SILL = 1.20                                  # north wall (Waschküche): nothing above 1.20, #30 glazes the top metre
TX = XG + 0.66                               # toilet axis on the north wall
FY = TUER[1] + 0.07 + 0.01                   # east wall tiles: from 1 cm past the door's architrave to the north wall
BY = (FY + YN) / 2                           # basin, mirror and their lamps on the east wall, centred on the tiles
BW, BD = 0.60, 0.47                          # Waschbecken einzeln
MW, MH, MF, MZ = 0.80, 0.85, 0.10, 1.17      # mirror: outer width x height, frame width, bottom
LX = (FENSTER[1] + WO) / 2                   # Wandlampe left of the window (seen from inside)
CLAD, ST = 2.0, 0.012                        # shower walls: limestone to 2.0 (as in the Bad Großeltern), slab face


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def waende(c, dx, dy):
    """The sub-model's pieces of the room's four walls and its floor: south (outer wall, the window with its
    shutters), west (Waschküche
    side), north (Waschküche) and east (Schlafzimmer, with the door); in the house build_og() builds them whole.
    The floor: the limestone slabs of the house's floor_cover() on a dark base, from its own generator."""
    H, zo = hc.Z_OG_TOP - hc.Z_OG, hc.Z_OG
    hc.wall(c, 5.44 + dx, 8.72 + dx, 0.0 + dy, YS + dy, 0.0, H,
            [(FENSTER[0] + dx, FENSTER[1] + dx, 3.62 - zo, 4.60 - zo, "W", 1)], out=-1)
    hc.interior(c, 5.44 + dx, WI + dx, YS + dy, 2.79 + dy, (), 0.0, H)
    hc.interior(c, WI + dx, WO + dx, YN + dy, 2.79 + dy, (), 0.0, H)
    hc.interior(c, WO + dx, 8.72 + dx, YS + dy, 2.79 + dy, [(TUER[0] + dy, TUER[1] + dy, -1, "a", False)], 0.0, H)
    rng = random.Random(4)
    hc.box(c, c + "_Boden", "Fuge", WI + dx, WO + dx, YS + dy, YN + dy, 0.0, 0.002, rng.random())
    hc.tiles(c, c + "_Bodenbelag", "Kalkstein", WI + dx, WO + dx, YS + dy, YN + dy, 0.002, 0.018, [0.5, 0.4, 0.55, 0.45],
             (0.35, 0.8), 0.006, (), rng)


def elternbad_neu(c="Elternbad", x0=0.0, y0=0.0, z=0.0, walls=False):
    """The Bad Nadine & Till built into collection c with the room's inner SW corner at (x0, y0) on floor z;
    with walls (the sub-model) also the four wall pieces. Mirror and shower cladding draw from this module's
    generator, toilet and shower from the global stream (as everywhere in the house), tiles and basin
    from their own. Returns the dimension lines (sub-model coordinates)."""
    dx, dy = x0 - ELTERNBAD_AT[0], y0 - ELTERNBAD_AT[1]
    if walls:
        waende(c, dx, dy)
    rng = random.Random(3)

    # east wall, north of the door: the basin on the tiles, the mirror and two lamps above it; a lamp left of the window
    hc.waschbecken(c, WO + dx, BY + dy, -1, 0, BW, BD, 1, z=z, tile=hc.WC_TILE_T)
    hc.wood_mirror(c, WO + dx, BY + dy, -1, 0, MW, MH, MF, z + MZ, rng)
    for d in (-MW / 4, MW / 4):
        hc.wandlampe(c, WO + dx, BY + d + dy, -1, 0, z + hc.WANDLAMPE_SPIEGEL_H)
    hc.wandlampe(c, LX + dx, YS + dy, 0, 1, z + hc.WANDLAMPE_H)
    # west wall: the two walk-in showers (no tray: the limestone floor runs through; limestone on the west wall and on
    # the strip's pieces of the south and north wall, which stop at the glass; the north wall's only to SILL; the
    # heads on the west wall's slabs), the toilet on the north wall's tiles
    hc.limestone(c, False, WI + dx, 1, YS + dy, YN + dy, z + 0.018, z + CLAD, rng)
    hc.limestone(c, True, YS + dy, 1, WI + ST + dx, XG - 0.005 + dx, z + 0.018, z + CLAD, rng)
    hc.limestone(c, True, YN + dy, -1, WI + ST + dx, XG - 0.005 + dx, z + 0.018, z + SILL, rng)
    hc.shower(c, WI + dx, XG + dx, YS + dy, YM + dy, [(XG + dx, YS + dy, XG + dx, PA + dy)],
              (WI + ST + dx, YS + HU + dy, 1, 0), z=z, tray=False)
    hc.shower(c, WI + dx, XG + dx, YM + dy, YN + dy, [(XG + dx, PB + dy, XG + dx, YN + dy)],
              (WI + ST + dx, YN - HU + dy, 1, 0), z=z, tray=False)
    hc.toilet(c, TX + dx, YN + dy, 0, -1, z=z)
    hc.wainscot(c, z, XG + 0.006 + dx, WO + dx, FY + dy, YN + dy, (WO + dx, WO + dx), sides="ne")

    # dimension lines (sub-model coordinates)
    S = lambda xa, ya, za, xb, yb, zb, s: ((xa - ELTERNBAD_AT[0], ya - ELTERNBAD_AT[1], za),
                                           (xb - ELTERNBAD_AT[0], yb - ELTERNBAD_AT[1], zb), s)
    f, top = 0.02, 2.10
    ba, bb = BY - BW / 2, BY + BW / 2
    ma, mb = BY - MW / 2, BY + MW / 2
    return [S(WI, YN - 0.05, top, XG, YN - 0.05, top, f"Duschen {cm(WI, XG)}"),
            S(XG, YN - 0.75, f, TX, YN - 0.75, f, cm(XG, TX)),                  # in front of the toilet
            S(TX, YN - 0.75, f, WO, YN - 0.75, f, cm(TX, WO)),
            S(XG + 0.05, YS, f, XG + 0.05, PA, f, f"Glas {cm(YS, PA)}"),
            S(XG + 0.05, PA + 0.012, f, XG + 0.05, PB - 0.012, f, f"Durchgang {cm(PA + 0.012, PB - 0.012)}"),
            S(XG + 0.05, PB, f, XG + 0.05, YN, f, f"Glas {cm(PB, YN)}"),
            S(WO - BD - 0.25, TUER[1], f, WO - BD - 0.25, ba, f, cm(TUER[1], ba)),
            S(WO - BD - 0.25, ba, f, WO - BD - 0.25, bb, f, f"Waschbecken {cm(ba, bb)}"),
            S(WO - BD - 0.25, bb, f, WO - BD - 0.25, YN, f, cm(bb, YN)),
            S(WO - 0.06, ma, MZ + MH + 0.05, WO - 0.06, mb, MZ + MH + 0.05, f"Spiegel {cm(ma, mb)} × {cm(0, MH)}"),
            S(WO - 0.06, ma - 0.05, 0.0, WO - 0.06, ma - 0.05, MZ, f"UK {cm(0, MZ)}"),
            S(FENSTER[0], YS + 0.05, top, FENSTER[1], YS + 0.05, top, f"Fenster {cm(*FENSTER)}"),
            S(WO - 0.05, YS, f, WO - 0.05, TUER[0], f, cm(YS, TUER[0])),
            S(WO - 0.05, TUER[0], f, WO - 0.05, TUER[1], f, f"Tür {cm(*TUER)}"),
            S(WI, YM, top, WO, YM, top, cm(WI, WO)),
            S(WI + 0.30, YS, top, WI + 0.30, YN, top, cm(YS, YN))]
