"""Frechenlehen – the Garderobe in the EG Flur (issue #61, G1 of input/2026-11-27 input/hintereingang_optionen.svg): on the big
Flur's south wall (the Speis's back), far west towards the back entrance, x GA .. GB: a hook board of old spruce
2 m long with many iron hooks in two staggered rows and a hat shelf on brackets above it, after
input/2026-11-10 input/garderobe mallnitz.jpeg (the hook board and hat shelf the back hall's Garderobe had, #27,
which gave way to the Duschbad, code/gaeste_wc.py); six coats hang from the upper hooks in front of the board.

Pure Python like house_core.py, which imports this module: build_eg() calls garderobe_neu() (house only, no
sub-model). The board, shelf and hooks are a built-in (EG_Garderobe), the coats furniture (EG_Kleidung).
"""
import math, random
import house_core as hc

GA, GB, YW = 2.80, 4.80, 6.349              # the board: x from, to; the Flur south wall's face (facing +y)
HOOK_Z, BOARD_Z, BOARD_TOP = (1.50, 1.65), 1.35, 2.00   # hook rows, the hook board
SHELF_D, SHELF_Z, BRACKET = 0.28, 1.95, 0.14             # hat shelf: depth, bottom, its brackets' reach
N_HOOKS = 20                                # upper row; the lower one between them
LAMPE_H = 2.20                              # the Flur's two Wandlampen there: over the hat shelf


def garderobe_neu(c="EG"):
    """The Garderobe into collection c (house coordinates). Own random.Random(61): no global draw."""
    rng = random.Random(61)
    o, r, yb = c + "_Garderobe", rng.random(), YW + 0.02                # yb: the board's face
    B = lambda m, xa, xb, ya, yb_, za, zb, rr=r: hc.box(c, o, m, xa, xb, ya, yb_, za, zb, rr)
    B("FichteZ", GA, GB, YW, yb, BOARD_Z, BOARD_TOP)                                         # hook board
    B("FichteX", GA, GB, YW, YW + SHELF_D, SHELF_Z, SHELF_Z + 0.03)                         # hat shelf
    bracket = [(yb, SHELF_Z), (yb + BRACKET, SHELF_Z)] + \
              [(yb + BRACKET * math.cos(math.pi / 2 * i / 6), SHELF_Z - 0.20 * math.sin(math.pi / 2 * i / 6))
               for i in range(1, 7)]
    for x in (GA + 0.06, GA + (GB - GA) / 3, GB - (GB - GA) / 3, GB - 0.06):                    # brackets
        hc.prism_x(c, o, "FichteX", x - 0.0125, x + 0.0125, bracket, r)
    xs = [GA + 0.10 + i * (GB - GA - 0.20) / (N_HOOKS - 1) for i in range(N_HOOKS)]
    for z, row in ((HOOK_Z[1], xs), (HOOK_Z[0], [(a + b) / 2 for a, b in zip(xs, xs[1:])])):
        for x in row:                                                                        # iron hooks: arm, tip
            B("Eisen", x - 0.006, x + 0.006, yb, yb + 0.10, z - 0.005, z + 0.007, 0.5)
            B("Eisen", x - 0.006, x + 0.006, yb + 0.088, yb + 0.10, z + 0.007, z + 0.04, 0.5)
    maentel(c, xs, yb, rng)


def maentel(c, xs, yb, rng):
    """Six coats (EG_Kleidung, furniture) in five fabrics from every third upper hook, in front of the hooks: a
    body tapering from its shoulders to the hem (thicker at the top), two sleeves, a collar and a loop over the
    hook; side by side, not touching. Each coat one draw of rng."""
    o, s = c + "_Kleidung", HOOK_Z[1] - 0.03                               # the shoulder line, under the hook
    fabrics = ["Loden", "Kamel", "Anthrazit", "Jeans", "Wolle"]
    rng.shuffle(fabrics)
    y0 = yb + 0.102                                                        # the coats' back: in front of the hooks
    for i, xc in enumerate(xs[1::3][:6]):
        m, r = (fabrics + fabrics)[i], rng.random()
        ln, hw = 0.85 + 0.20 * r, 0.12 + 0.01 * r                          # length, half width at the hem
        T = lambda prof, t0, t1, m=m, r=r: _slab(c, o, m, prof, y0, t0, t1, s, ln, r)
        T([(xc - hw, s - ln), (xc + hw, s - ln), (xc + 0.11, s - 0.30), (xc + 0.11, s - 0.04), (xc + 0.05, s + 0.02),
           (xc - 0.05, s + 0.02), (xc - 0.11, s - 0.04), (xc - 0.11, s - 0.30)], 0.09, 0.04)            # body
        for k in (-1, 1):                                                                         # sleeves
            T([(xc + k * 0.095, s - 0.04), (xc + k * 0.125, s - 0.08), (xc + k * 0.13, s - 0.60),
               (xc + k * 0.095, s - 0.62)][::k], 0.10, 0.08)
        hc.box(c, o, m, xc - 0.05, xc + 0.05, y0, y0 + 0.05, s + 0.02, s + 0.06, r)                # collar
        hc.box(c, o, m, xc - 0.005, xc + 0.005, yb + 0.09, y0, s + 0.05, HOOK_Z[1] + 0.02, r)       # loop


def _slab(c, o, m, prof, y0, t0, t1, s, ln, r):
    """A (x, z) profile from y0 out to y0 + t(z): t0 at the shoulder line s, t1 at the hem s - ln."""
    n = len(prof)
    t = lambda z: t1 + (t0 - t1) * max(0.0, min(1.0, (z - s + ln) / ln))
    v = [(x, y0, z) for x, z in prof] + [(x, y0 + t(z), z) for x, z in prof]
    f = [list(range(n))[::-1], list(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    hc.add(c, o, m, v, f, r)
