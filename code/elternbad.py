"""Frechenlehen – the Bad of Nadine & Till im 1. Stock (issue #3) as a sub-model (web/elternbad.html): the OG
Bad between Waschküche and Schlafzimmer (S, under the window of the south wall), rearranged: the door to the
Schlafzimmer at the south end of the east wall (hinged south, open 90 deg into the Bad; 25 cm off the corner,
so the open leaf with its levers clears the Wandlampe left of the window); the toilet where the door was (NE corner, back to
the north wall, facing the window; Taubenblau tiles on the north and east wall); the shower in the NW corner,
long towards the toilet to the window's east jamb, its entrance (60) at the west wall, glass from there and
at its toilet end, walk-in on the room's limestone floor (no tray), its west and north wall clad in limestone
to 2.0 like the Bad Großeltern's; the Waschbecken doppelt 100 under a mirror 110 x 85 in a 10 cm wooden frame (like the
Gästebad's, narrower: the wall to the window is 125), the basin's end 15 from the window reveal, four
Wandlampen over it, one left of the window (seen from inside), one over the cistern.

Pure Python like house_core.py, which imports this module: build_sanitary() calls elternbad_neu() at
ELTERNBAD_AT on the OG floor, build_og() takes the door (TUER) from here, BATHS_OG the room (ROOM);
house_core.build_elternbad() wraps it at the origin with the pieces of the room's four walls (walls=True)
as the Blueprint of web/elternbad.html. The floor stays the house's limestone (BATHS_OG).
"""
import random
import house_core as hc

ELTERNBAD_AT = (5.59, 0.40)                  # house: the room's inner SW corner
WI, WO, YS, YN = 5.59, 8.59, 0.40, 2.62      # room: west and east (Schlafzimmer wall) faces, south and north faces
ROOM = (WI, WO, YS, YN)
FENSTER = (6.84, 7.72)                       # the window in the south wall (build_og())
TUER = (0.65, 1.58)                          # door in the east wall, hinged south, open 90 deg into the Bad
SS, SE = 1.64, FENSTER[1]                    # shower: south edge, east end (at the window's east jamb)
GA = 6.19                                    # glass GA .. SE on its south edge, open WI .. GA (60): the entrance
TX = WO - 0.45                               # toilet axis, 45 from the east wall
FY = TUER[1] + 0.07 + 0.01                   # east wall tiles: from 1 cm past the door's architrave to the north wall
BX = FENSTER[0] - 0.15 - 0.50                 # basin and mirror: the basin's end 15 from the window reveal (as before)
BW, BD = 1.00, 0.47                          # Waschbecken doppelt
MW, MH, MF, MZ = 1.10, 0.85, 0.10, 1.17      # mirror: outer width x height, frame width, bottom
LX = (FENSTER[1] + WO) / 2                   # Wandlampe left of the window (seen from inside)
CLAD, ST = 2.0, 0.012                        # shower walls: limestone to 2.0 (as in the Bad Großeltern), slab face


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def waende(c, dx, dy):
    """The sub-model's pieces of the room's four walls: south (outer wall, the window), west (Waschküche
    side), north (Waschküche) and east (Schlafzimmer, with the door); in the house build_og() builds them whole."""
    H, zo = hc.Z_OG_TOP - hc.Z_OG, hc.Z_OG
    hc.wall(c, 5.44 + dx, 8.72 + dx, 0.0 + dy, YS + dy, 0.0, H,
            [(FENSTER[0] + dx, FENSTER[1] + dx, 3.62 - zo, 4.60 - zo, "W")], out=-1)
    hc.interior(c, 5.44 + dx, WI + dx, YS + dy, 2.79 + dy, (), 0.0, H)
    hc.interior(c, WI + dx, WO + dx, YN + dy, 2.79 + dy, (), 0.0, H)
    hc.interior(c, WO + dx, 8.72 + dx, YS + dy, 2.79 + dy, [(TUER[0] + dy, TUER[1] + dy, -1, "a", False)], 0.0, H)


def elternbad_neu(c="Elternbad", x0=0.0, y0=0.0, z=0.0, walls=False):
    """The Bad Nadine & Till built into collection c with the room's inner SW corner at (x0, y0) on floor z;
    with walls (the sub-model) also the four wall pieces. Mirror and shower cladding draw from this module's
    generator, toilet and shower from the global stream (as everywhere in the house), tiles and basin
    from their own. Returns the dimension lines (sub-model coordinates)."""
    dx, dy = x0 - ELTERNBAD_AT[0], y0 - ELTERNBAD_AT[1]
    if walls:
        waende(c, dx, dy)
    rng = random.Random(3)

    # south wall: the basin between west wall and window, the mirror and four lamps above it, a lamp left of the window
    hc.waschbecken(c, BX + dx, YS + dy, 0, 1, BW, BD, 2, z=z)
    hc.wood_mirror(c, BX + dx, YS + dy, 0, 1, MW, MH, MF, z + MZ, rng)
    for k in range(4):                                   # one per quarter of the mirror's width (#19)
        hc.wandlampe(c, BX - MW / 2 + MW * (k + 0.5) / 4 + dx, YS + dy, 0, 1, z + hc.WANDLAMPE_SPIEGEL_H)
    hc.wandlampe(c, LX + dx, YS + dy, 0, 1, z + hc.WANDLAMPE_H)
    # north wall: the walk-in shower from the west wall to SE (no tray: the limestone floor runs through; limestone
    # on its two walls from the floor up; the north
    # wall's to the glass, the west wall's to the north slabs; the head on their face), the toilet in the NE
    # corner on its tiles, a lamp over the cistern
    hc.limestone(c, True, YN + dy, -1, WI + dx, SE - 0.005 + dx, z + 0.018, z + CLAD, rng)
    hc.limestone(c, False, WI + dx, 1, SS + dy, YN - ST + dy, z + 0.018, z + CLAD, rng)
    hc.shower(c, WI + dx, SE + dx, SS + dy, YN + dy,
              [(GA + dx, SS + dy, SE + dx, SS + dy), (SE + dx, SS + dy, SE + dx, YN + dy)],
              ((GA + SE) / 2 + dx, YN - ST + dy, 0, -1), z=z, tray=False)
    hc.toilet(c, TX + dx, YN + dy, 0, -1, z=z)
    hc.wainscot(c, z, SE + 0.006 + dx, WO + dx, FY + dy, YN + dy, (WO + dx, WO + dx), sides="ne")
    hc.wandlampe(c, TX + dx, YN + dy, 0, -1, z + hc.WANDLAMPE_H)

    # dimension lines (sub-model coordinates)
    S = lambda xa, ya, za, xb, yb, zb, s: ((xa - ELTERNBAD_AT[0], ya - ELTERNBAD_AT[1], za),
                                           (xb - ELTERNBAD_AT[0], yb - ELTERNBAD_AT[1], zb), s)
    f, top = 0.02, 2.10
    ba, bb = BX - BW / 2, BX + BW / 2
    ma, mb = BX - MW / 2, BX + MW / 2
    return [S(WI, YN - 0.05, top, SE, YN - 0.05, top, f"Dusche {cm(WI, SE)} × {cm(SS, YN)}"),
            S(SE, YN - 0.05, top, TX, YN - 0.05, top, cm(SE, TX)),
            S(TX, YN - 0.05, top, WO, YN - 0.05, top, cm(TX, WO)),
            S(WI + 0.05, SS, top, WI + 0.05, YN, top, cm(SS, YN)),
            S(WI, SS - 0.05, f, GA, SS - 0.05, f, f"{cm(WI, GA)} offen"),
            S(GA, SS - 0.05, f, SE, SS - 0.05, f, f"Glas {cm(GA, SE)}"),
            S(WI, YS + BD + 0.25, f, ba, YS + BD + 0.25, f, cm(WI, ba)),
            S(ba, YS + BD + 0.25, f, bb, YS + BD + 0.25, f, f"Waschbecken {cm(ba, bb)}"),
            S(bb, YS + BD + 0.25, f, FENSTER[0], YS + BD + 0.25, f, cm(bb, FENSTER[0])),
            S(ma, YS + 0.06, MZ + MH + 0.05, mb, YS + 0.06, MZ + MH + 0.05, f"Spiegel {cm(ma, mb)} × {cm(0, MH)}"),
            S(ma - 0.05, YS + 0.06, 0.0, ma - 0.05, YS + 0.06, MZ, f"UK {cm(0, MZ)}"),
            S(FENSTER[0], YS + 0.05, top, FENSTER[1], YS + 0.05, top, f"Fenster {cm(*FENSTER)}"),
            S(WO - 0.05, YS, f, WO - 0.05, TUER[0], f, cm(YS, TUER[0])),
            S(WO - 0.05, TUER[0], f, WO - 0.05, TUER[1], f, f"Tür {cm(*TUER)}"),
            S(WI, (SS + YS) / 2, top, WO, (SS + YS) / 2, top, cm(WI, WO)),
            S(WI + 0.30, YS, top, WI + 0.30, YN, top, cm(YS, YN))]
