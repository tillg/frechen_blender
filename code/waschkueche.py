"""Frechenlehen – basin and shower in the Waschküche im 1. Stock (issue #29). The room (x 5.59 .. 8.59, y 2.79 ..
6.06, no window) holds the table along the whole south wall, the basket cupboard on the west wall, washer and
washer + dryer on the east wall and the door in the north wall (opened 90°, its leaf at x 7.15). Added here: a
floor-level shower cabin 1.10 x 1.10 in the NW corner, right of the door as one comes in (DUSCHE, outer outline;
the user: „Gleich rechts in dem Eck … mit zwei Glaswänden, die man aufklappen kann. Und dann noch ein Spalt von
20 cm bis zu dem Schrank.“): limestone slabs on its floor only, in the plane of the bathroom floors (no tray;
house_core lays them with the floor cover), limestone on the west and north wall to 2.0, the head on the west wall,
the drain in the middle; its south and east side each a bifold glass door folding into the cabin (built closed);
the cupboard ends 20 cm before it. On the east wall north of the machines a Waschbecken einzeln 60 on Taubenblau
tiles under a mirror 80 x 85 in a 10 cm wooden frame. Nothing on the south wall: #30 glazes its top metre.

Pure Python like house_core.py, which imports this module: build_sanitary() calls waschkueche_neu() on the OG
floor; build_slabs() takes DUSCHE for the floor cover, build_furniture() ends the cupboard 20 cm before it.
"""
import random
import house_core as hc

WI, WO, YN = 5.59, 8.59, 6.06                # room: west, east and north (Flur) faces (south 2.79: the Bad partition)
DUSCHE = (WI, 6.69, 4.96, YN)                # shower cabin, outer: the NW corner, right of the door as one comes in
GT, ST = 0.008, 0.012                        # glass thickness; the limestone slabs' face off the wall
GAP = 0.005                                  # the glass doors' gaps: to the profile, the floor, the other door
BY = 5.28                                    # basin, tiles, mirror, lamp: their axis on the east wall, north of
                                             # the washer tower (4.85), 5+ cm outside the room door leaf's sweep
BW, BD = 0.60, 0.47                          # Waschbecken einzeln
MW, MH, MF, MZ = 0.80, 0.85, 0.10, 1.17      # mirror: outer width x height, frame width, bottom


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


def becken(c, z, rng):
    """The basin on the east wall on Taubenblau tiles 12 cm wider each side, the wood-framed mirror above it (its
    Wandlampe: house_core.WANDLAMPEN_OG, in the slot of the lamp it replaced)."""
    hc.wainscot(c, z, WO - 1.0, WO, BY - BW / 2 - 0.12, BY + BW / 2 + 0.12, None, sides="e")
    hc.waschbecken(c, WO, BY, -1, 0, BW, BD, 1, z=z, tile=hc.WC_TILE_T)
    hc.wood_mirror(c, WO, BY, -1, 0, MW, MH, MF, z + MZ, rng)


def waschkueche_neu(c, z):
    """Basin and shower of the Waschküche into collection c on floor z. Glass, limestone and mirror draw from an own
    stream; head and drain (hc.shower) and the tiles and basin draw as their helpers do elsewhere."""
    rng = random.Random(29)
    dusche(c, z, rng)
    becken(c, z, rng)
