"""Frechenlehen – basin and shower in the Waschküche im 1. Stock (issue #29). The room (x 5.59 .. 8.59, y 2.79 ..
6.06, no window) holds the table along the whole south wall, the basket cupboard on the west wall, washer and
washer + dryer on the east wall and the door in the north wall (leaf open flat to the west). Added here: a
floor-level shower cabin 1.10 x 1.10 against the west wall just north of the table (DUSCHE, outer outline):
limestone slabs on its floor only, in the plane of the bathroom floors (no tray; house_core lays them with the
floor cover), limestone on the west wall to 2.0, the head on it, the drain in the middle; 8 mm glass to the south,
north and east up to 2.0 with a top rail, the east glass holding a door 60 wide at its north end (hinged north,
opening out into the room; built closed). On the east wall north of the machines a Waschbecken einzeln 60 on
Taubenblau tiles under a mirror 80 x 85 in a 10 cm wooden frame. Nothing on the south wall: #30 glazes its top metre.

Pure Python like house_core.py, which imports this module: build_sanitary() calls waschkueche_neu() on the OG
floor; build_slabs() takes DUSCHE for the floor cover, build_furniture() fits the cupboard north of it.
"""
import random
import house_core as hc

WI, WO = 5.59, 8.59                          # room: west and east faces (south 2.79: the Bad partition; north 6.06)
DUSCHE = (WI, WI + 1.10, 3.61, 4.71)         # shower cabin, outer: west wall .. glass, 1.8 cm north of the table
GT, ST = 0.008, 0.012                        # glass thickness; the limestone slabs' face off the wall
TW = 0.60                                    # glass door width (north end of the east glass)
GAP = 0.005                                  # the door's gap to the north pane, to the floor and the rail
BY = 5.28                                    # basin, tiles, mirror, lamp: their axis on the east wall, north of
                                             # the washer tower (4.85), 5+ cm outside the room door leaf's sweep
BW, BD = 0.60, 0.47                          # Waschbecken einzeln
MW, MH, MF, MZ = 0.80, 0.85, 0.10, 1.17      # mirror: outer width x height, frame width, bottom


def dusche(c, z, rng):
    """The shower cabin into collection c on floor z (the floor slabs: house_core's floor cover). Glass, rails,
    hinges and grips share one rnd (one draw from rng); the limestone draws its own."""
    o, (x0, x1, y0, y1), r = c + "_Sanitaer", DUSCHE, rng.random()
    zf, zt = z + 0.018, z + 2.0                                      # on the slabs; glass top
    B = lambda m, xa, xb, ya, yb, za, zb: hc.box(c, o, m, xa, xb, ya, yb, za, zb, r)
    T = lambda p0, p1, rad: hc.turned(c, o, "Metall", p0, p1, [(rad, 0), (rad, 1)], rnd=r)
    xs = x0 + ST                                                     # the panes start on the slabs
    dy1 = y1 - GT - GAP                                              # the door: dy0 .. dy1, hinged at dy1
    dy0 = dy1 - TW
    B("Glas", xs, x1, y0, y0 + GT, zf, zt)                           # south pane
    B("Glas", xs, x1, y1 - GT, y1, zf, zt)                           # north pane
    B("Glas", x1 - GT, x1, y0 + GT, dy0 - GAP, zf, zt)               # east: fixed pane
    B("Glas", x1 - GT, x1, dy0, dy1, z + 0.025, zt - GAP)           # east: the door
    for xa, xb, ya, yb in ((xs, x1, y0, y0 + GT), (xs, x1, y1 - GT, y1), (x1 - GT, x1, y0, dy0 - GAP)):
        B("Metall", xa - 0.006, xb + 0.006, ya - 0.006, yb + 0.006, zt, zt + 0.02)   # top rail
    for zh in (0.30, 1.62):                                          # glass-to-glass hinges on the north edge
        B("Metall", x1 - GT - 0.014, x1 + 0.014, dy1 - 0.05, y1 + 0.004, z + zh, z + zh + 0.08)
    ym = dy0 + 0.05                                                  # bar handle on both faces at the free edge
    for s, xg in ((1, x1), (-1, x1 - GT)):
        T((xg + s * 0.05, ym, z + 0.80), (xg + s * 0.05, ym, z + 1.40), 0.012)
        for zg in (0.85, 1.35):
            T((xg, ym, z + zg), (xg + s * 0.05, ym, z + zg), 0.007)
    hc.limestone(c, False, WI, 1, y0 + GT, y1 - GT, zf, zt, rng)    # west wall
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
