"""Frechenlehen – the Küche (EG) as a sub-model (web/kueche.html), after the agreed drawing
input/2026-11-09 input/speis_kueche_v6.svg (the kitchen door measured from a photo of 2026-11-09).
On the north wall the Spülzeile from the kitchen door's frame into the NE corner, under the Abzug
(flue box, from 1.80 m up); on the east wall the Ostzeile, 60 cm from the Halbinsel's front, then the
Wamsler wood cooker under its old steel hood; the Halbinsel with the cooktop towards the dining
table; the Besenschrank in the NW corner, behind the kitchen door opened into the room. No wall
cabinets. All cabinets in the style of input/2026-11-10 input/kueche_mallnitz.png, painted RAL 5014
(hc.mallnitz_front); east of the sink, where the Herd stands in front of the Spülzeile, a blind
cabinet, its granite top (like the Ostzeile's) running up to the Herd.

Pure Python like house_core.py, which imports this module: build_eg() calls kueche_neu() at
KUECHE_AT; house_core.build_kueche() wraps it at the origin as the Blueprint of web/kueche.html.
Positions are written in house coordinates (those of the drawing) and shifted by (x0, y0) -
KUECHE_AT, so the house and the sub-model are the same parts, only translated. The room's walls and
doors stay in build_eg().
"""
import math, random
import house_core as hc
import ofen

KUECHE_AT = (5.49, 5.849)                    # house: the room's inner NW corner (Speis wall x Flur wall)
ZP, ZC, ZT = 0.10, 0.86, 0.90                # plinth / carcass / worktop top
XW, YN, XE = 5.492, 5.847, 8.555             # wall faces (2 mm clear): Speis wall, Flur wall, east wall
SINK_X0 = 7.05                               # Spülzeile: from the kitchen door's frame (7.03) ...
HY0, HY1 = 4.30, 5.10                        # the Herd (80) along the east wall, right after the Ostzeile
OSTZEILE = (3.66, 4.26)                      # the Ostzeile's door: 60 from the Halbinsel's front
ABZUG = (8.227, 5.55, 1.80)                  # Abzug: x from, y from (depth 30 assumed), underside
BESEN = (6.002, 5.297, 2.20)                 # Besenschrank: x to, y from (incl. door), height


def kueche_neu(c="Kueche", x0=0.0, y0=0.0):
    """The Küche built into collection c with the room's inner NW corner at (x0, y0). The parts draw
    their rnd from their own generator. Returns the dimension lines (sub-model coordinates)."""
    dx, dy = x0 - KUECHE_AT[0], y0 - KUECHE_AT[1]
    rng = random.Random(14)
    o, zp, zc, zt = c + "_Kueche", ZP, ZC, ZT
    B = lambda ob, m, xa, xb, ya, yb, za, zb, r=None: hc.box(c, ob, m, xa + dx, xb + dx, ya + dy, yb + dy, za, zb,
                                                         rng.random() if r is None else r)
    PR = lambda ob, m, pts, za, zb, r=None: hc.xy_prism(c, ob, m, [(x + dx, y + dy) for x, y in pts], za, zb,
                                                     rng.random() if r is None else r)

    # carcasses (x0, x1, y0, y1, plinth inset W/E/S/N), painted like the fronts
    for xa, xb, ya, yb, pl in ((SINK_X0, XE, 5.269, YN, (0, 0, 0.04, 0)),                # Spülzeile
                               (6.57, XE, 3.05, 3.64, (0.06, 0, 0.06, 0.06)),             # Halbinsel
                               (7.977, XE, 3.64, HY0 - 0.04, (0.06, 0, 0, 0.06))):        # Ostzeile
        B(o, "Front", xa, xb, ya, yb, zp, zc)
        B(o, "Fuge", xa + pl[0], xb - pl[1], ya + pl[2], yb - pl[3], 0.005, zp)
    # Mallnitz fronts (hc.mallnitz_front), each with a cup pull: doors near the top, drawers
    # centred; per run (frame axis, room face, side, [(from, to, kind)]); the cabinet under the
    # cooktop has drawers towards the kitchen and towards the dining table; east of 7.85 the Herd
    # stands in front of the Spülzeile: a blind cabinet, closed towards the Herd by a filler
    za, zb, dr = zp + 0.005, zc - 0.005, (0.18, 0.285, 0.285)        # drawer heights, top to bottom
    runs = [("x", 5.249, +1, [(SINK_X0, 7.45, "door_r"), (7.45, 7.85, "door_l"), (7.85, 7.977, None)]),
            ("x", 3.66, -1, [(6.57, 7.165, "door_r"), (7.165, 7.957, "drawers")]),
            ("x", 3.03, +1, [(7.165, 7.957, "drawers")]),
            ("y", 7.957, +1, [(OSTZEILE[0], OSTZEILE[1], "drawers")])]
    for ax, f, s, units in runs:
        sh = (dx, dy) if ax == "x" else (dy, dx)
        P = lambda u, t, z, ax=ax, sh=sh: hc.frame(ax)(u + sh[0], t + sh[1], z)
        for a, b, kind in units:
            a, b = a + 0.003, b - 0.003
            if kind == "drawers":
                z = zb
                for h in dr:
                    hc.mallnitz_front(c, o, P, a, b, f, s, z - h + 0.0015, z - 0.0015, rng.random(),
                                      [((a + b) / 2, z - min(h / 2, 0.07))])
                    z -= h
            else:
                grips = {"door_r": [(b - 0.08, zb - 0.06)], "door_l": [(a + 0.08, zb - 0.06)]}
                hc.mallnitz_front(c, o, P, a, b, f, s, za, zb, rng.random(), grips.get(kind, []))
    B(o, "Front", 7.957, 7.977, HY1 + 0.007, 5.249, za, zb)                            # filler to the Herd
    B(o, "Fuge", 7.997, 8.017, HY1 + 0.007, 5.269, 0.005, zp)
    PR(o, "Granit", [(SINK_X0, 5.229), (7.937, 5.229), (7.937, HY1 + 0.007), (XE, HY1 + 0.007), (XE, YN),
                     (SINK_X0, YN)], zc, zt)                                        # 2 mm off the Herd's rim
    PR(o, "Granit", [(6.55, 3.03), (XE, 3.03), (XE, HY0 - 0.007), (7.937, HY0 - 0.007),
                     (7.937, 3.68), (6.55, 3.68)], zc, zt)
    sx = 7.46                                                       # sink at today's water connection
    B(o, "Stahl", sx - 0.23, sx + 0.23, 5.30, 5.76, zt, zt + 0.003)
    B(o, "Stahl", sx - 0.20, sx + 0.20, 5.33, 5.70, zt + 0.003, zt + 0.004)
    B(o, "Stahl", sx - 0.015, sx + 0.015, 5.77, 5.80, zt, zt + 0.26)                  # tap
    B(o, "Stahl", sx - 0.01, sx + 0.01, 5.60, 5.77, zt + 0.235, zt + 0.255)
    B(o, "Eisen", 7.18, 7.95, 3.12, 3.58, zt, zt + 0.005)                            # cooktop
    for cx, cy, rr in ((7.36, 3.24, 0.08), (7.36, 3.46, 0.06), (7.76, 3.24, 0.06), (7.76, 3.46, 0.09)):
        PR(o, "Metall", [(cx + rr * math.cos(math.pi * i / 8), cy + rr * math.sin(math.pi * i / 8))
                         for i in range(16)], zt + 0.005, zt + 0.006)
    ofen.wamsler(c, 7.972 + dx, HY0 + dy, rng)

    # hood of the old form: rolled lip, straight skirt with a rail, canopy narrowing to the stack
    h, xf, ym = c + "_Haube", XE - 0.55, (HY0 + HY1) / 2
    ya, yb, rh = ym - 0.43, ym + 0.43, rng.random()
    B(h, "Stahl", xf - 0.01, XE, ya - 0.01, yb + 0.01, 1.62, 1.64, rh)
    B(h, "Stahl", xf, XE, ya, yb, 1.64, 1.76, rh)
    v = [(xf, ya, 1.76), (XE, ya, 1.76), (XE, yb, 1.76), (xf, yb, 1.76),
         (XE - 0.22, ym - 0.15, 2.04), (XE, ym - 0.15, 2.04), (XE, ym + 0.15, 2.04), (XE - 0.22, ym + 0.15, 2.04)]
    hc.add(c, h, "Stahl", [(x + dx, y + dy, z) for x, y, z in v],
           [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], rh)
    B(h, "Stahl", XE - 0.20, XE, ym - 0.135, ym + 0.135, 2.04, hc.Z_EG_TOP + 0.02, rh)    # into the ceiling
    hc.prism(c, h, "Stahl", hc.frame("x"), [(xf - 0.04 + dx + 0.01 * math.cos(math.pi * i / 4),
                                             1.70 + 0.01 * math.sin(math.pi * i / 4)) for i in range(8)],
             ya + 0.02 + dy, yb - 0.02 + dy, rng.random())                            # rail
    for y in (ya + 0.05, yb - 0.05):
        B(h, "Stahl", xf - 0.04, xf, y - 0.005, y + 0.005, 1.695, 1.705)
    # at its back edge (the wall) a strip under the lip with 4 built-in spots (#22), one light for the four
    sa, sb = ya + 0.05, yb - 0.05
    B(h, "Metall", XE - 0.07, XE - 0.01, sa, sb, 1.60, 1.62, rh)
    for k in range(4):
        y = sa + (sb - sa) * (k + 0.5) / 4
        B(h, "Opalglas", XE - 0.06, XE - 0.02, y - 0.02, y + 0.02, 1.596, 1.60, rh)
    hc.WALL_LIGHTS.append((XE - 0.50 + dx, ym + dy, 1.45))    # 50 out from the wall like every lamp's, under the hood
    hc.WALL_LIGHT_VARIANT.append(None)
    # Besenschrank in the NW corner, door to the south, on a plinth like the base units
    bx, by, bh = BESEN
    B(o, "Front", XW, bx, by + 0.02, YN, zp, bh)
    B(o, "Fuge", XW, bx, by + 0.06, YN, 0.005, zp)
    hc.mallnitz_front(c, o, lambda u, t, z: (u + dx, t + dy, z), XW + 0.003, bx - 0.003, by, +1, zp + 0.005,
                      bh - 0.005, rng.random(), [(bx - 0.08, 1.00)])

    # Abzug (flue box) in the NE corner, plastered, from 1.80 m to the ceiling
    ax0, ay0, az = ABZUG
    B(c + "_Waende", "Putz", ax0, XE, ay0, YN, az, hc.Z_EG_TOP)

    f = 0.06                                                        # dimension lines
    P = lambda x, y, z: (x - KUECHE_AT[0], y - KUECHE_AT[1], z)
    return [(P(SINK_X0, 5.229 - f, zt), P(XE, 5.229 - f, zt), "Spülzeile 150.5"),
            (P(7.957 - f, OSTZEILE[0], zt), P(7.957 - f, OSTZEILE[1], zt), "Ostzeile 60"),
            (P(7.957 - f, HY0, zt), P(7.957 - f, HY1, zt), "Herd 80"),
            (P(XW, by - f, bh), P(bx, by - f, bh), "Besenschrank 51"),
            (P(bx + f, by, bh), P(bx + f, YN, bh), "55 tief"),
            (P(ax0 - f, ay0, 0.0), P(ax0 - f, ay0, az), "Abzug ab 180"),
            (P(ax0 - f, ay0, hc.Z_EG_TOP - 0.05), P(ax0 - f, YN, hc.Z_EG_TOP - 0.05), "Abzug 30 tief (angenommen)"),
            (P(6.57, 3.03 - f, zt), P(XE, 3.03 - f, zt), "Halbinsel 198.5")]
