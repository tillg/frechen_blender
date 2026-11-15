"""Frechenlehen – the Gäste-WC by the back hall (EG) as a sub-model (web/gaeste_wc.html), after the
agreed drawing input/2026-11-10 input/gaeste_wc_v3.svg (generator gaeste_wc_svg.py beside it) and the
Mallnitz photos of the same folder. The old WC (2.05 x 1.10 m) is split by a new 10 cm partition,
its east face flush with the old door's west jamb: in the west the WC with a new 76 opening in the
north wall, its leaf opened outward into the Flur (90 deg, hinged at the partition side: laid flat it
would cover the Garderobe's opening), the toilet centred on the south wall, Taubenblau tiles; in the
east the Garderobe, open to the Flur through the old 80 opening, without a bench (issue #27): on its
left (east) wall a hook board with 23 hooks and a hat shelf (garderobe mallnitz.jpeg), across its back
end a hanging rod with five coats, under them a shoe shelf of two 20 cm levels with six pairs of shoes. The WC's hand basin stands outside, on
its Waschbeckenständer (input/2026-11-12 input/), at the Flur east wall between the WC wall and the
Windfang door, tiles behind it and a mirror in a wooden frame above.

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
BW, BD = 0.40, 0.28                          # Waschbecken einzeln (hc.waschbecken), centred on the Flur wall piece
BM = (YF + FWA) / 2
MF, MGW, MGH, MZ = 0.07, 0.40, 0.60, 1.20    # mirror: frame width, glass width x height, frame bottom
HOOK_Z, BOARD_Z, BOARD_TOP = (1.50, 1.65), 1.35, 2.00   # Garderobe (#27): hook rows, hook board on the east wall
SHELF_D, SHELF_Z, BRACKET = 0.28, 1.95, 0.14            # hat shelf: depth, bottom, its brackets' reach
ROD_Y, ROD_Z, ROD_R = YS + 0.27, 1.78, 0.0125           # hanging rod across the back end (south wall)
SHOE_D, SHOE_Z, SHOE_T = 0.33, (0.04, 0.26, 0.48), 0.02  # shoe shelf: depth, its three boards' bottoms, thickness


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

    # Flur east wall: hand basin on its Ständer, tiles behind it up to the Windfang door's architrave, mirror
    # 40 x 60 in a 7 cm wooden frame (2.5 cm deep), its glass set back in the frame
    hc.waschbecken(c, WO + dx, BM + dy, -1, 0, BW, BD, 1, tile=hc.WC_TILE_T)
    hc.wainscot(c, 0.0, WO + dx - 1.0, WO + dx, YF + dy, FWA - 0.07 + dy, None, sides="e")
    ya, yb, za, zb = BM - MGW / 2 - MF, BM + MGW / 2 + MF, MZ, MZ + MGH + 2 * MF
    hc.wood_mirror(c, WO + dx, BM + dy, -1, 0, yb - ya, zb - za, MF, za, rng)

    # Garderobe after garderobe mallnitz.jpeg, without the bench (issue #27): walking in from the
    # passage (heading south), on the left (east) wall the old-spruce hook board over the whole wall
    # with 23 iron hooks in two staggered rows and the hat shelf on three brackets above; across the
    # back end (south wall) a steel hanging rod from wall to wall, under it a shoe shelf with two
    # levels of 20 cm
    o, r = "_Garderobe", rng.random()
    B(o, "FichteZ", WO - 0.02, WO, YS, YN, BOARD_Z, BOARD_TOP, r)                           # hook board
    B(o, "FichteY", WO - SHELF_D, WO, YS, YN, SHELF_Z, SHELF_Z + 0.03, r)                   # hat shelf (28 from the wall)
    P = lambda u, t, z: (u + dx, t + dy, z)                                                  # (x, z) profiles, t = y
    bracket = [(WO - 0.02, SHELF_Z), (WO - 0.02 - BRACKET, SHELF_Z)] + \
              [(WO - 0.02 - BRACKET * math.cos(math.pi / 2 * i / 6), SHELF_Z - 0.20 * math.sin(math.pi / 2 * i / 6))
               for i in range(1, 7)]
    for y in (YS + 0.06, (YS + YN) / 2, YN - 0.06):
        hc.prism(c, c + o, "FichteZ", P, bracket, y - 0.0125, y + 0.0125, r)
    n = 12                                                                                   # hooks: 12 above, 11 between them below
    ys = [YS + 0.10 + i * (YN - YS - 0.20) / (n - 1) for i in range(n)]
    for z, row in ((HOOK_Z[1], ys), (HOOK_Z[0], [(a + b) / 2 for a, b in zip(ys, ys[1:])])):
        for y in row:
            B(o, "Eisen", WO - 0.12, WO - 0.02, y - 0.006, y + 0.006, z - 0.005, z + 0.007, 0.5)
            B(o, "Eisen", WO - 0.12, WO - 0.108, y - 0.006, y + 0.006, z + 0.007, z + 0.04, 0.5)
    rod = lambda xa, xb, rr: hc.turned(c, c + o, "Stahl", (xa + dx, ROD_Y + dy, ROD_Z), (xb + dx, ROD_Y + dy, ROD_Z),
                                       [(rr, 0), (rr, 1)], 12, 0.5)
    rod(PB, WO - 0.02, ROD_R)                                                                # rod, into the hook board
    rod(PB, PB + 0.008, 0.03)                                                                # its wall flanges
    rod(WO - 0.028, WO - 0.02, 0.03)
    for xa, xb in ((PB, PB + 0.02), (WO - 0.02, WO)):                                        # shoe shelf: sides,
        B(o, "FichteZ", xa, xb, YS, YS + SHOE_D, 0.0, SHOE_Z[-1] + SHOE_T, r)
    for z in SHOE_Z:                                                                         # three boards,
        B(o, "FichteX", PB + 0.02, WO - 0.02, YS, YS + SHOE_D, z, z + SHOE_T, r)
    B(o, "FichteX", PB + 0.02, WO - 0.02, YS + SHOE_D - 0.04, YS + SHOE_D - 0.02, 0.0, SHOE_Z[0], r)   # recessed plinth

    kleidung(c, dx, dy)

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
            S(PB, ROD_Y, ROD_Z + 0.05, WO, ROD_Y, ROD_Z + 0.05, f"Kleiderstange {cm(PB, WO)} auf {cm(0, ROD_Z)}"),
            S((PB + WO) / 2, YS, SHOE_Z[-1] + SHOE_T + f, (PB + WO) / 2, YS + SHOE_D, SHOE_Z[-1] + SHOE_T + f,
              f"Schuhregal {cm(0, SHOE_D)} tief"),
            S(PB + 0.06, YS + SHOE_D + 0.02, SHOE_Z[0] + SHOE_T, PB + 0.06, YS + SHOE_D + 0.02, SHOE_Z[1], cm(SHOE_Z[0] + SHOE_T, SHOE_Z[1])),
            S(PB + 0.06, YS + SHOE_D + 0.02, SHOE_Z[1] + SHOE_T, PB + 0.06, YS + SHOE_D + 0.02, SHOE_Z[2], cm(SHOE_Z[1] + SHOE_T, SHOE_Z[2])),
            S(WO - 0.06, YS, BOARD_TOP + 0.05, WO - 0.06, YN, BOARD_TOP + 0.05, f"Hakenbrett {cm(YS, YN)}"),
            S(DB, YF + 0.35, f, WO - BD - 0.01, YF + 0.35, f, f"{cm(DB, WO - BD - 0.01)} frei"),
            S(WO - BD - 0.06, YF, 0.85, WO - BD - 0.06, ba, 0.85, cm(YF, ba)),
            S(WO - BD - 0.06, ba, 0.85, WO - BD - 0.06, bb, 0.85, f"HWB {cm(ba, bb)}"),
            S(WO - BD - 0.06, bb, 0.85, WO - BD - 0.06, FWA, 0.85, cm(bb, FWA)),
            S(WO - 0.06, ya - 0.05, 0.0, WO - 0.06, ya - 0.05, MZ, f"UK {cm(0, MZ)}"),
            S(WO - 0.06, ya, zb + 0.05, WO - 0.06, yb, zb + 0.05, f"Spiegel {cm(ya, yb)} × {cm(za, zb)}")]


def kleidung(c, dx, dy):
    """The Garderobe's illustrating clothes (#27), object <c>_Kleidung (furniture): five coats in
    five fabrics on wooden hangers on the rod, between the partition's Wandlampe (reaching x 1.63)
    and the east wall's hooks (from x 2.238), and a dozen shoes, 6 pairs (Halbschuhe, Turnschuhe,
    Stiefel), three on each level of the shoe shelf, toes to the room. Own random.Random(27), an
    explicit rnd for every part, so nothing else in the house changes."""
    rk, o = random.Random(27), c + "_Kleidung"
    X = lambda m, xa, xb, prof, r: hc.prism_x(c, o, m, xa + dx, xb + dx, [(y + dy, z) for y, z in prof], r)
    Bx = lambda m, xa, xb, ya, yb, za, zb, r: hc.box(c, o, m, xa + dx, xb + dx, ya + dy, yb + dy, za, zb, r)

    def T(m, xc, half, prof, r):                                        # (y, z) profile, its thickness half(z) about xc
        n = len(prof)
        v = [(xc + k * half(z) + dx, y + dy, z) for k in (-1, 1) for y, z in prof]
        f = [list(range(n))[::-1], list(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        hc.add(c, o, m, v, f, r)
    fabrics = ["Loden", "Kamel", "Anthrazit", "Jeans", "Wolle"]
    rk.shuffle(fabrics)
    yc, s = ROD_Y, ROD_Z - 0.08                                         # hanger plane, shoulder line
    for i, m in enumerate(fabrics):
        xc, ln, hw, r = 1.71 + 0.10 * i + rk.uniform(-0.004, 0.004), rk.uniform(0.85, 1.05), rk.uniform(0.22, 0.25), rk.random()
        T(m, xc, lambda z: 0.02 + 0.02 * (z - s + ln) / ln,                                         # body, from 8 cm
          [(yc - hw, s - ln), (yc + hw, s - ln), (yc + 0.20, s - 0.30), (yc + 0.21, s - 0.05),            # thick at the
           (yc + 0.07, s + 0.02), (yc - 0.07, s + 0.02), (yc - 0.21, s - 0.05), (yc - 0.20, s - 0.30)], r)  # shoulders to 4
        for k in (-1, 1):                                                                          # sleeves
            T(m, xc, lambda z: 0.045 - 0.01 * (s - z) / 0.62, [(yc + k * 0.20, s - 0.04), (yc + k * 0.245, s - 0.10),
                                                               (yc + k * 0.255, s - 0.60), (yc + k * 0.20, s - 0.62)], r)
        Bx(m, xc - 0.03, xc + 0.03, yc - 0.07, yc + 0.07, s + 0.02, s + 0.06, r)                   # collar
        X("Kiefer", xc - 0.006, xc + 0.006, [(yc - 0.20, s - 0.03), (yc + 0.20, s - 0.03), (yc + 0.20, s - 0.015),
                                             (yc + 0.05, s + 0.035), (yc - 0.05, s + 0.035), (yc - 0.20, s - 0.015)], r)
        w, f = 0.002, ROD_R + 0.002                                                                # hook over the rod
        Bx("Stahl", xc - w, xc + w, yc + f, yc + f + 2 * w, s + 0.06, ROD_Z + f + 2 * w, 0.5)
        Bx("Stahl", xc - w, xc + w, yc - f - 2 * w, yc + f, ROD_Z + f, ROD_Z + f + 2 * w, 0.5)
        Bx("Stahl", xc - w, xc + w, yc - f - 2 * w, yc - f, ROD_Z, ROD_Z + f, 0.5)
    kinds = [("Halbschuh", 0.08, ["Leder", "Anthrazit"]), ("Turnschuh", 0.085, ["Leinen", "Jeans", "Wolle"]),
             ("Stiefel", 0.15, ["Leder", "Kamel"])] * 2
    rk.shuffle(kinds)
    xa, xb = PB + 0.02, WO - 0.02                                                                  # between the sides
    for j, (kind, hh, mats) in enumerate(kinds):
        b = SHOE_Z[j // 3] + SHOE_T + 0.001                                                         # on its board
        xp = xa + (xb - xa) * (j % 3 + 0.5) / 3
        m, ls, y0, r = rk.choice(mats), rk.uniform(0.26, 0.29), YS + 0.02 + rk.uniform(0, 0.01), rk.random()
        y1, z0, sh = y0 + ls, b + 0.019, 0.12 if kind == "Stiefel" else 0.09                        # toe, upper's base, shaft
        for xs in (xp - 0.055, xp + 0.055):
            Bx("Gummi", xs - 0.045, xs + 0.045, y0, y1, b, b + 0.02, r)                            # sole
            X(m, xs - 0.04, xs + 0.04, [(y0 + 0.005, z0), (y1 - 0.005, z0), (y1 - 0.005, z0 + 0.025), (y1 - 0.05, z0 + 0.045),
                                       (y0 + sh + 0.01, z0 + 0.06), (y0 + sh, z0 + hh), (y0 + 0.005, z0 + hh)], r)   # upper
