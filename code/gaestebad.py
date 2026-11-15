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
import math
import random
import house_core as hc
import gaeste_wc

GAESTEBAD_AT = (0.31, 5.46)                  # house: the room's inner SW corner
WI, WO, YS, YN = 0.31, 2.57, 5.46, 8.57      # room: west and east (Flur wall) faces, south and north faces
PA = gaeste_wc.PA                            # the glass between shower and WC: over the EG partition's west face
YG = 6.34                                    # its north end, 19 cm before the partition's (6.15); the way in north of it
TUER = (7.66, 8.47)                          # Flur door in the east wall, hinged south, open flat into the Bad
SN = 6.865                                   # shower's north edge: the glass pane to the tub
TL, TW = 1.65, 0.75                          # tub: slipper tub, length x width (body, without the rolled rim)
TX0, YT = WI + 0.035, SN + 0.025             # its west and south edge: free of the wall and the pane
XT, TY1 = TX0 + TW, YT + TL                  # its east and north edge
HEAD, FOOT = 0.74, 0.60                      # rim: raised head end (south, to the shower), foot end; under the 0.75 sill
TAP = TY1 - 0.35                             # the tub's tap: on the west (outer) wall at the foot end
GX = XT + 0.05                               # the pane shower | tub: from the west wall's slabs to here
SX = (WI + PA) / 2                           # shower head: the middle of its south wall, on the slabs
CLAD, ST = 2.0, 0.012                        # shower walls: limestone to 2.0, slab face off the wall
WS = (5.72, 6.32, 4.18)                      # the west wall's small window: y span, sill (house z)
TX = (PA + WO) / 2                           # toilet axis: centred between glass and east wall
BX = 1.46                                    # basin and mirror: between the tub and the door
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
    """The bathtub (#32), after input/2026-11-15 input/badewanne.webp: a freestanding slipper tub TL x TW on four
    claw feet, its oval (superellipse) body narrowing to the bottom, a rolled rim, the head end raised as a back
    rest (HEAD, to the shower in the south) falling to FOOT at the north end; white ceramic, built of closed
    wall segments (one Part each, all sharing one rnd). The chrome tap with spout and hand shower comes out of
    the west (outer) wall at the foot end; the drain is at that end too. Own rng: one draw."""
    o, r, n = c + "_Sanitaer", rng.random(), 48
    cx, cy, a, b = (TX0 + XT) / 2 + dx, (YT + TY1) / 2 + dy, TL / 2, TW / 2

    def ring(sa, sb):                                    # superellipse outline (exponent 3), from the south end round
        pts = []
        for i in range(n):
            t = 2 * math.pi * i / n - math.pi / 2
            ct, st = math.cos(t), math.sin(t)
            pts.append((cx + sb * math.copysign(abs(ct) ** (2 / 3), ct), cy + sa * math.copysign(abs(st) ** (2 / 3), st)))
        return pts

    def rim(y):                                          # rim height: FOOT, rising over the south 40 % to HEAD
        s = min(1.0, max(0.0, (-(y - cy) / a - 0.2) / 0.8))
        return FOOT + (HEAD - FOOT) * s * s * (3 - 2 * s)

    zb, zf, w = 0.17, 0.21, 0.055                       # body bottom, inner floor, wall
    ob, ot = ring(0.80 * a, 0.78 * b), ring(a, b)
    it, ib = ring(a - w, b - w), ring(0.80 * a - w, 0.78 * b - w)
    orl, irl = ring(a + 0.012, b + 0.012), ring(a - w, b - w)
    for i in range(n):
        j = (i + 1) % n
        h0, h1 = z + rim(ot[i][1]) - 0.03, z + rim(ot[j][1]) - 0.03
        v = [(*ob[i], z + zb), (*ob[j], z + zb), (*ot[i], h0), (*ot[j], h1),
             (*it[i], h0), (*it[j], h1), (*ib[i], z + zf), (*ib[j], z + zf)]
        quads = [(0, 1, 3, 2), (2, 3, 5, 4), (4, 5, 7, 6), (6, 7, 1, 0), (0, 2, 4, 6), (1, 7, 5, 3)]
        hc.add(c, o, "Keramik", v, quads, r)                                        # wall segment
        v = [(*orl[i], h0 - 0.005), (*orl[j], h1 - 0.005), (*orl[i], h0 + 0.035), (*orl[j], h1 + 0.035),
             (*irl[i], h0 + 0.035), (*irl[j], h1 + 0.035), (*irl[i], h0 - 0.005), (*irl[j], h1 - 0.005)]
        hc.add(c, o, "Keramik", v, quads, r)                                        # rolled rim
    hc.xy_prism(c, o, "Keramik", ib, z + zb, z + zf, r)                              # inner floor
    for sx in (-1, 1):                                                               # claw feet
        for sy in (-1, 1):
            fx, fy = cx + sx * 0.25, cy + sy * 0.52
            hc.turned(c, o, "Keramik", (fx, fy, z), (fx, fy, z + zb + 0.01),
                      [(0.028, 0), (0.034, 0.12), (0.018, 0.3), (0.016, 0.55), (0.03, 0.85), (0.045, 1)], rnd=r)
    T = lambda p0, p1, prof: hc.turned(c, o, "Metall", (p0[0] + dx, p0[1] + dy, z + p0[2]),
                                       (p1[0] + dx, p1[1] + dy, z + p1[2]), prof, rnd=r)
    T((cx - dx, cy + 0.50 - dy, zf), (cx - dx, cy + 0.50 - dy, zf + 0.003), [(0.03, 0), (0.03, 1)])   # drain
    px, py, zt = WI, TAP, FOOT + 0.17                                               # the tap, on the outer wall
    T((px, py, zt), (px + 0.008, py, zt), [(0.035, 0), (0.035, 1)])                 # rosette
    T((px, py, zt), (px + 0.07, py, zt), [(0.022, 0), (0.022, 1)])                  # mixer body
    T((px + 0.05, py, zt), (px + 0.05, py, zt + 0.08), [(0.007, 0), (0.006, 1)])    # lever
    T((px + 0.07, py, zt), (px + 0.20, py, zt - 0.03), [(0.014, 0), (0.012, 1)])    # spout over the rim
    T((px, py + 0.12, zt + 0.25), (px + 0.008, py + 0.12, zt + 0.25), [(0.025, 0), (0.025, 1)])   # hand shower:
    T((px, py + 0.12, zt + 0.25), (px + 0.05, py + 0.12, zt + 0.25), [(0.008, 0), (0.008, 1)])     # holder,
    T((px + 0.05, py + 0.12, zt + 0.12), (px + 0.05, py + 0.12, zt + 0.30), [(0.011, 0), (0.012, 1)])   # grip,
    T((px + 0.05, py + 0.12, zt + 0.30), (px + 0.05, py + 0.12, zt + 0.34), [(0.02, 0), (0.022, 1)])   # head


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
    hc.wandlampe(c, (WI + XT) / 2 + dx, YN + dy, 0, -1, z + hc.WANDLAMPE_SPIEGEL_H)   # over the tub's foot end
    hc.wandlampe(c, WO + dx, (YS + YG) / 2 + dy, -1, 0, z + hc.WANDLAMPE_H)           # east wall: over the toilet
    # back wall: the shower in the SW corner (no tray: the limestone floor runs through; limestone on the west wall,
    # its small window left free above the sill, and on the south wall to the glass; the head on the slabs), the
    # tub north of it; south wall: the WC east of the glass
    sill = z + WS[2] - hc.Z_OG
    hc.limestone(c, False, WI, 1, YS, SN, z + 0.018, sill, rng, dx, dy)
    for ya, yb in ((YS, WS[0]), (WS[1], SN)):
        hc.limestone(c, False, WI, 1, ya, yb, sill, z + CLAD, rng, dx, dy)
    hc.limestone(c, True, YS, 1, WI + ST, PA - 0.005, z + 0.018, z + CLAD, rng, dx, dy)
    hc.shower(c, WI + dx, PA + dx, YS + dy, SN + dy, [(PA + dx, YS + dy, PA + dx, YG + dy),
                                                       (WI + ST + dx, SN + dy, GX + dx, SN + dy)],
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
            S((TX0 + XT) / 2, YT, f, (TX0 + XT) / 2, TY1, f, f"Wanne {cm(YT, TY1)} × {cm(TX0, XT)}"),
            S(XT + 0.03, YT + 0.10, 0.0, XT + 0.03, YT + 0.10, HEAD, f"Kopfende {cm(0, HEAD)}"),
            S(XT + 0.03, TY1 - 0.25, 0.0, XT + 0.03, TY1 - 0.25, FOOT, f"Rand {cm(0, FOOT)}"),
            S(WI, YN - BD - 0.25, f, ba, YN - BD - 0.25, f, cm(WI, ba)),
            S(ba, YN - BD - 0.25, f, bb, YN - BD - 0.25, f, f"Waschbecken {cm(ba, bb)}"),
            S(bb, YN - BD - 0.25, f, WO, YN - BD - 0.25, f, cm(bb, WO)),
            S(ma, YN - 0.06, MZ + MH + 0.05, mb, YN - 0.06, MZ + MH + 0.05, f"Spiegel {cm(ma, mb)} × {cm(0, MH)}"),
            S(ma - 0.05, YN - 0.06, 0.0, ma - 0.05, YN - 0.06, MZ, f"UK {cm(0, MZ)}"),
            S(WO - 0.05, TUER[0], f, WO - 0.05, TUER[1], f, f"Tür {cm(*TUER)}"),
            S(WI, YT + 0.35, top, WO, YT + 0.35, top, cm(WI, WO)),
            S(WI + 0.30, YS, top, WI + 0.30, YN, top, cm(YS, YN))]
