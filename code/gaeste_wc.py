"""Frechenlehen – the Duschbad by the back hall (EG) as a sub-model (web/gaeste_wc.html), issue #61 (variant B of the
drawing input/2026-11-27 input/hintereingang_optionen.svg, the user 2026-11-27): the old Gäste-WC and Garderobe of
input/2026-11-10 input/gaeste_wc_v3.svg are one room, its north wall moved 20 cm north (room 204.8 x 129.9). In the
east a walk-in shower 90 x 130 (no tray: the room's limestone runs through; limestone on its walls to 2.0, the head
on the east wall), a glass pane 75 from the south wall on its west side, the entry 55 north of it; in the west the
toilet on the south wall (Taubenblau tiles on the WC part's walls) and the basin einzeln 40 x 28 on its Ständer on
the west wall north of the window, a mirror 40 x 60 in a wooden frame above it. The door 76 in the north wall (west
part) opens outward into the back hall, hinged east (laid flat it would cover the shoe rack). In the back hall east
of the door a shoe rack of two 20 cm levels with six pairs of shoes. The Garderobe moved to the Flur
(code/garderobe.py).

Pure Python like house_core.py, which imports this module: build_eg() calls gaeste_wc_neu() at WC_AT;
house_core.build_gaeste_wc() wraps it at the origin as the Blueprint of web/gaeste_wc.html. Positions are written
in house coordinates and shifted by (x0, y0) - WC_AT. It brings the room's north wall (with its door) and the back
hall's two other doors; the floor stays the house's limestone.
"""
import random
import house_core as hc

WC_AT = (0.31, 5.475)                        # house: the room's inner SW corner
WI, WO = 0.31, 2.358                         # room: west wall face, east face
YS, YN, YF = 5.475, 6.774, 6.923             # south wall face, north wall (#61: 20 cm north): room face, hall face
XS, GL = 1.458, 0.75                         # shower: its glass line (shower x XS .. WO, 90), glass from the south wall
DA, DB = 0.68, 1.44                          # door opening (76) in the north wall, hinged at DB, outward 90 deg
TX = 0.85                                    # toilet axis on the south wall
BW, BD, BM = 0.40, 0.28, 6.55                # Waschbecken einzeln on the west wall: its axis north of the window (5.724 .. 6.324)
MW, MH, MF, MZ = 0.40, 0.60, 0.05, 1.20      # mirror: outer width x height, frame width, bottom
HY, CLAD, ST = 6.05, 2.0, 0.012              # shower head on the east wall at y HY; limestone to CLAD, slab face
SX = 1.56                                    # shoe rack: from x SX to the east wall, on the north wall's hall face
SHOE_D, SHOE_Z, SHOE_T = 0.33, (0.04, 0.26, 0.48), 0.02  # its depth, its three boards' bottoms, thickness
OLD_DRAWS = 44                               # global draws of the Gäste-WC + Garderobe till #61 (burnt: later parts keep theirs)


def cm(a, b):
    return "%d" % round(abs(b - a) * 100)


def gaeste_wc_neu(c="GaesteWC", x0=0.0, y0=0.0):
    """The Duschbad and the back hall's doors and shoe rack, built into collection c with the room's inner SW corner
    at (x0, y0). The north wall, the doors, toilet and shower draw from the global stream, which is then set to where
    the former Gäste-WC left it (OLD_DRAWS); limestone and mirror from this module's generator, tiles and basin from
    their own. Returns the dimension lines (sub-model coordinates)."""
    dx, dy = x0 - WC_AT[0], y0 - WC_AT[1]
    st, rng = random.getstate(), random.Random(12)

    # the north wall with the door (outward, 90 deg); the back door (closed; in the west wall's opening) and the
    # glazed Windfang door (open 90 deg into the back hall; in the wall x 2.358 .. 2.657), each leaf its own object so
    # the viewer can swing it, both hinged north: open they lie along the hall's north wall (request 2026-11-10)
    hc.interior(c, WI + dx, WO + dx, YN + dy, YF + dy, [(DA + dx, DB + dx, 1, "b", False, "panel", "Innentuer",
                                                         c + "_WC_Tuer")])
    hc.back_door(c, dx, dy)
    hc.panel_door(c, "y", 7.408 + dy, 8.506 + dy, WO + dx, 2.657 + dx, 0.0, hc.DOOR_H, -1, "b", False, "glazed",
                  leaf=c + "_Windfangtuer")

    # WC part: toilet on the south wall, Taubenblau tiles on its walls (door left free), the basin with its mirror
    hc.toilet(c, TX + dx, YS + dy, 0, 1)
    hc.wainscot(c, 0.0, WI + dx, XS + dx, YS + dy, YN + dy, (DA + dx, DB + dx), sides="snw")
    hc.waschbecken(c, WI + dx, BM + dy, 1, 0, BW, BD, 1, tile=hc.WC_TILE_T)
    hc.wood_mirror(c, WI + dx, BM + dy, 1, 0, MW, MH, MF, MZ, rng)

    # shower: limestone on the east wall and on the shower's parts of the south and north wall, head and drain, the pane
    hc.limestone(c, False, WO + dx, -1, YS + dy, YN + dy, 0.018, CLAD, rng)
    hc.limestone(c, True, YS + dy, 1, XS + 0.005 + dx, WO - ST + dx, 0.018, CLAD, rng)
    hc.limestone(c, True, YN + dy, -1, XS + 0.005 + dx, WO - ST + dx, 0.018, CLAD, rng)
    hc.shower(c, XS + dx, WO + dx, YS + dy, YN + dy, [(XS + dx, YS + dy, XS + dx, YS + GL + dy)],
              (WO - ST + dx, HY + dy, -1, 0), tray=False)

    schuhregal(c, dx, dy, rng)
    hc.restream(st, OLD_DRAWS)

    # dimension lines (sub-model coordinates)
    S = lambda xa, ya_, za_, xb, yb_, zb_, s: ((xa - WC_AT[0], ya_ - WC_AT[1], za_), (xb - WC_AT[0], yb_ - WC_AT[1], zb_), s)
    f, ba, bb, ma, mb = 0.02, BM - BW / 2, BM + BW / 2, BM - MW / 2, BM + MW / 2
    return [S(WI, YN - 0.05, f, WO, YN - 0.05, f, f"Raumbreite {cm(WI, WO)}"),       # the room on the floor (every
            S(WI + 0.65, YS, f, WI + 0.65, YN, f, f"Raumtiefe {cm(YS, YN)}"),        # bath sub-model)
            S(XS, YS + 0.05, 2.10, WO, YS + 0.05, 2.10, f"Dusche {cm(XS, WO)}"),
            S(XS - 0.05, YS, 2.10, XS - 0.05, YS + GL, 2.10, f"Glas {cm(0, GL)}"),
            S(XS - 0.05, YS + GL, 2.10, XS - 0.05, YN, 2.10, f"Einstieg {cm(YS + GL, YN)}"),
            S(WI, YS + 0.80, f, TX, YS + 0.80, f, cm(WI, TX)),
            S(WI, YF + 0.05, f, DA, YF + 0.05, f, cm(WI, DA)),
            S(DA, YF + 0.05, f, DB, YF + 0.05, f, f"Tür {cm(DA, DB)}"),
            S(WI + BD + 0.05, YS, 0.85, WI + BD + 0.05, ba, 0.85, cm(YS, ba)),
            S(WI + BD + 0.05, ba, 0.85, WI + BD + 0.05, bb, 0.85, f"HWB {cm(ba, bb)}"),
            S(WI + 0.06, ma, MZ + MH + 0.05, WI + 0.06, mb, MZ + MH + 0.05, f"Spiegel {cm(ma, mb)} × {cm(0, MH)}"),
            S(SX, YF + SHOE_D + 0.05, SHOE_Z[-1] + SHOE_T + f, WO, YF + SHOE_D + 0.05, SHOE_Z[-1] + SHOE_T + f,
              f"Schuhregal {cm(SX, WO)}"),
            S((SX + WO) / 2, YF, SHOE_Z[-1] + SHOE_T + f, (SX + WO) / 2, YF + SHOE_D, SHOE_Z[-1] + SHOE_T + f,
              f"{cm(0, SHOE_D)} tief")]


def schuhregal(c, dx, dy, rng):
    """The shoe rack in the back hall (#61, object <c>_Schuhregal, furniture): on the room's north wall, from SX to
    the east wall, SHOE_D deep, two sides, three boards (two levels of 20 cm), a recessed plinth; on its levels six
    pairs of shoes (Halbschuhe, Turnschuhe, Stiefel), three on each, toes to the hall (<c>_Kleidung, furniture).
    Spruce from one draw of rng, the shoes from an own random.Random(27), an explicit rnd for every part."""
    o, r = c + "_Schuhregal", rng.random()
    B = lambda m, xa, xb, ya, yb, za, zb, rr=r: hc.box(c, o, m, xa + dx, xb + dx, ya + dy, yb + dy, za, zb, rr)
    y0, y1 = YF, YF + SHOE_D
    for xa, xb in ((SX, SX + 0.02), (WO - 0.02, WO)):                                       # sides
        B("FichteZ", xa, xb, y0, y1, 0.0, SHOE_Z[-1] + SHOE_T)
    for z in SHOE_Z:                                                                         # three boards
        B("FichteX", SX + 0.02, WO - 0.02, y0, y1, z, z + SHOE_T)
    B("FichteX", SX + 0.02, WO - 0.02, y0 + 0.02, y0 + 0.04, 0.0, SHOE_Z[0])                # plinth, recessed
    rk, o = random.Random(27), c + "_Kleidung"
    X = lambda m, xa, xb, prof, rr: hc.prism_x(c, o, m, xa + dx, xb + dx, [(y + dy, z) for y, z in prof], rr)
    Bx = lambda m, xa, xb, ya, yb, za, zb, rr: hc.box(c, o, m, xa + dx, xb + dx, ya + dy, yb + dy, za, zb, rr)
    kinds = [("Halbschuh", 0.08, ["Leder", "Anthrazit"]), ("Turnschuh", 0.085, ["Leinen", "Jeans", "Wolle"]),
             ("Stiefel", 0.15, ["Leder", "Kamel"])] * 2
    rk.shuffle(kinds)
    xa, xb = SX + 0.02, WO - 0.02                                                            # between the sides
    for j, (kind, hh, mats) in enumerate(kinds):
        b = SHOE_Z[j // 3] + SHOE_T + 0.001                                                  # on its board
        xp = xa + (xb - xa) * (j % 3 + 0.5) / 3
        m, ls, r0, rr = rk.choice(mats), rk.uniform(0.26, 0.29), y0 + 0.02 + rk.uniform(0, 0.01), rk.random()
        r1, z0, sh = r0 + ls, b + 0.019, 0.12 if kind == "Stiefel" else 0.09                 # heel at the wall, toe
        for xs in (xp - 0.055, xp + 0.055):                                                  # to the hall
            Bx("Gummi", xs - 0.045, xs + 0.045, r0, r1, b, b + 0.02, rr)                     # sole
            X(m, xs - 0.04, xs + 0.04, [(r0 + 0.005, z0), (r1 - 0.005, z0), (r1 - 0.005, z0 + 0.025), (r1 - 0.05, z0 + 0.045),
                                       (r0 + sh + 0.01, z0 + 0.06), (r0 + sh, z0 + hh), (r0 + 0.005, z0 + hh)], rr)   # upper
