"""Frechenlehen – basin and shower in the Waschküche im 1. Stock (issue #29). The room (x 5.59 .. 8.59, y 2.79 ..
6.06, no window) holds the table along the whole south wall, the basket cupboard on the west wall, the washer
tower (washer + dryer, 4 cm from the table) on the east wall and the door in the north wall (opened 90°, its leaf at x 7.15). Added here: a
floor-level shower cabin 1.10 x 1.10 in the NW corner, right of the door as one comes in (DUSCHE, outer outline;
the user: „Gleich rechts in dem Eck … mit zwei Glaswänden, die man aufklappen kann. Und dann noch ein Spalt von
20 cm bis zu dem Schrank.“): its floor the room's limestone (#28: the whole room, in the plane of the bathroom
floors; no tray; house_core lays it with the floor cover), limestone on the west and north wall to 2.0, the head on the west wall,
the drain in the middle; its south and east side each a bifold glass door folding into the cabin (built closed);
the cupboard ends 20 cm before it. On the east wall north of the tower the deep ceramic sink of the Briol
(waschbecken-briol.jpeg, 60 x 45, two wall taps) on Taubenblau tiles under a mirror 80 x 85 in a 10 cm wooden frame. The south wall's top metre is the Bad's Oberlicht (#30,
elternbad.oberlicht()): the four Wandlampen over the table hang under it (LAMPE_H).

Pure Python like house_core.py, which imports this module: build_sanitary() calls waschkueche_neu() on the OG
floor; build_slabs() takes ROOM for the floor cover (via BATHS_OG), build_furniture() ends the cupboard 20 cm before it.
"""
import random
import house_core as hc

WI, WO, YS, YN = 5.59, 8.59, 2.79, 6.06      # room: west, east, south (the Bad partition) and north (Flur) faces
ROOM = (WI, WO, YS, YN)                      # its limestone floor (#28): house_core's floor cover, BATHS_OG
DUSCHE = (WI, 6.69, 4.96, YN)                # shower cabin, outer: the NW corner, right of the door as one comes in
GT, ST = 0.008, 0.012                        # glass thickness; the limestone slabs' face off the wall
GAP = 0.005                                  # the glass doors' gaps: to the profile, the floor, the other door
BY = 4.70                                    # basin, tiles, mirror, lamp: their axis on the east wall, north of
                                             # the washer tower (4.252): tiles 3 cm, basin 15 cm from it
BW, BD = 0.60, 0.45                          # the Briol sink (deep, wall-hung)
MW, MH, MF, MZ = 0.80, 0.85, 0.10, 1.17      # mirror: outer width x height, frame width, bottom
LAMPE_H = 1.10                               # the four Wandlampen over the table (south wall): under #30's glazing
                                             # (sill 1.20; lamp top +0.085), the shade's rim 23 cm over the table


def dusche(c, z, rng):
    """The shower cabin into collection c on floor z (the floor slabs: house_core's floor cover): limestone on the
    west and north wall, head and drain, the south and east side each a bifold glass door (faltwand). Glass, profiles,
    hinges and grips share one rnd (one draw from rng); the limestone draws its own."""
    o, (x0, x1, y0, y1), r = c + "_Sanitaer", DUSCHE, rng.random()
    zf, zt = z + 0.018, z + 2.0                                      # on the slabs; top of the glass

    def faltwand(along_x, ta, uw, uf, out):
        """Bifold glass door: glass t = ta .. ta + GT, from the wall profile at u = uw to the free end uf; two equal
        panels folding into the cabin, two hinges at the fold, a bar handle each side of the free panel (`out`: the
        outside's t direction)."""
        P = (lambda u, t: (u, t)) if along_x else (lambda u, t: (t, u))
        B = lambda m, ua, ub, t0, t1, za, zb: hc.box(c, o, m, *sorted((P(ua, t0)[0], P(ub, t1)[0])),
                                                     *sorted((P(ua, t0)[1], P(ub, t1)[1])), za, zb, r)
        d = 1 if uf > uw else -1
        B("Metall", uw, uw + d * 0.02, ta - 0.0085, ta + GT + 0.0085, zf, zt)        # wall profile
        ua = uw + d * (0.02 + GAP)
        um = (ua + uf) / 2                                                          # the fold
        B("Glas", ua, um - d * 0.003, ta, ta + GT, z + 0.025, zt - GAP)
        B("Glas", um + d * 0.003, uf, ta, ta + GT, z + 0.025, zt - GAP)
        for zh in (0.30, 1.62):
            B("Metall", um - 0.012, um + 0.012, ta - 0.006, ta + GT + 0.006, z + zh, z + zh + 0.08)
        ug = uf - d * 0.06                                                          # bar handles at the free end
        for s, tg in ((out, ta + GT if out > 0 else ta), (-out, ta if out > 0 else ta + GT)):
            T = lambda t0, t1, z0, z1, rad: hc.turned(c, o, "Metall", (*P(ug, t0), z0), (*P(ug, t1), z1),
                                                      [(rad, 0), (rad, 1)], rnd=r)
            T(tg + s * 0.05, tg + s * 0.05, z + 0.80, z + 1.40, 0.012)
            for zg in (0.85, 1.35):
                T(tg, tg + s * 0.05, z + zg, z + zg, 0.007)

    faltwand(True, y0, x0 + ST, x1, -1)                              # south: from the west wall to the corner
    faltwand(False, x1 - GT, y1 - ST, y0 + GT + GAP, 1)              # east: from the Flur wall to the south door
    hc.limestone(c, False, WI, 1, y0 + GT, y1 - ST, zf, zt, rng)    # west wall
    hc.limestone(c, True, y1, -1, x0 + ST, x1 - GT, zf, zt, rng)    # north (Flur) wall
    hc.shower(c, x0, x1, y0, y1, [], (WI + ST, (y0 + y1) / 2, 1, 0), z=z, tray=False)   # head, drain


def briol(c, z, rng):
    """The deep ceramic sink after input/2026-11-05 input/waschbecken-briol.jpeg, hung on the east wall's tiles at
    BY: BW x BD, rim at 0.85, 30 high, walls 2.5 cm, a lip 3.5 cm high all round, the body 6 mm inside it; drain,
    overflow, a waste pipe down and back to the wall; above it two wall taps with cross handles side by side
    (u = -/+ 7 cm). One rnd (one draw from rng) for all of it."""
    o, r = c + "_Sanitaer", rng.random()
    M = hc.at_wall(WO - hc.WC_TILE_T, BY, -1, 0)
    K = lambda u0, u1, v0, v1, z0, z1: hc.xy_prism(c, o, "Keramik", [M(u0, v0), M(u1, v0), M(u1, v1), M(u0, v1)],
                                                   z + z0, z + z1, r)
    T = lambda p0, p1, rad: hc.turned(c, o, "Metall", (*M(p0[0], p0[1]), z + p0[2]), (*M(p1[0], p1[1]), z + p1[2]),
                                      [(rad, 0), (rad, 1)], rnd=r)
    w, d, top, zb, e, i, L, lw = BW / 2, BD, 0.85, 0.55, 0.025, 0.006, 0.035, 0.04
    K(-w + i, w - i, 0.0, d - i, zb, zb + e)                                       # bottom
    K(-w + i, w - i, 0.0, e, zb + e, top - L)                                      # back
    K(-w + i, w - i, d - i - e, d - i, zb + e, top - L)                            # front
    for s in (-1, 1):
        K(*sorted((s * (w - i), s * (w - i - e))), e, d - i - e, zb + e, top - L)  # sides
        K(*sorted((s * w, s * (w - lw))), lw, d - lw, top - L, top)                # lip: sides,
    K(-w, w, 0.0, lw, top - L, top)                                                # back,
    K(-w, w, d - lw, d, top - L, top)                                              # front
    vd = d / 2
    T((0, vd, zb + e), (0, vd, zb + e + 0.003), 0.03)                              # drain
    T((0, e, top - 0.09), (0, e + 0.003, top - 0.09), 0.014)                       # overflow
    T((0, vd, zb), (0, vd, 0.42), 0.016)                                           # waste pipe
    T((0, vd + 0.016, 0.42), (0, 0.0, 0.42), 0.016)                                # to the wall
    T((0, 0.0, 0.42), (0, 0.008, 0.42), 0.03)                                      # rosette
    ht = top + 0.24                                                                # wall taps
    for u in (-0.07, 0.07):
        T((u, 0.0, ht), (u, 0.01, ht), 0.025)                                      # rosette
        T((u, 0.0, ht), (u, 0.065, ht), 0.011)                                     # body
        T((u, 0.06, ht), (u, 0.09, ht - 0.03), 0.009)                              # spout, bent down
        T((u, 0.09, ht - 0.03), (u, 0.095, ht - 0.09), 0.008)
        T((u, 0.035, ht), (u, 0.035, ht + 0.035), 0.006)                           # stem
        T((u - 0.025, 0.035, ht + 0.035), (u + 0.025, 0.035, ht + 0.035), 0.0045)   # cross handle
        T((u, 0.01, ht + 0.035), (u, 0.06, ht + 0.035), 0.0045)


def becken(c, z, rng):
    """The Briol sink on the east wall on Taubenblau tiles 12 cm wider each side, the wood-framed mirror above it
    (its Wandlampe: house_core.WANDLAMPEN_OG, in the slot of the lamp it replaced)."""
    hc.wainscot(c, z, WO - 1.0, WO, BY - BW / 2 - 0.12, BY + BW / 2 + 0.12, None, sides="e")
    briol(c, z, rng)
    hc.wood_mirror(c, WO, BY, -1, 0, MW, MH, MF, z + MZ, rng)


def waschkueche_neu(c, z):
    """Basin and shower of the Waschküche into collection c on floor z. Glass, limestone and mirror draw from an own
    stream; head and drain (hc.shower) and the tiles and basin draw as their helpers do elsewhere."""
    rng = random.Random(29)
    dusche(c, z, rng)
    becken(c, z, rng)
