"""Draws the proposal "Schrank im Büro" (v1) as SVG: the Tegernsee bookcase (regal_tegernsee.jpeg,
2.38 high, elements 94/94/94/52) around the east window of the Bibliothek (Büro end), world
coordinates from house_core (metres). Plan (north up), elevation of the east wall (looking east) and
a section through the window (looking north).
Usage: python3 buero_regal_svg.py buero_regal_v1.svg
       python3 buero_regal_svg.py buero_regal_v2.svg v2
v1: looking at the window: 94 column left (north), 94 split under / over the window, 52 right
(south); the Büro door moved west far enough to open 90 deg past the 52 element. Depths estimated
from the photo (42, middle base 48), the photo's heights estimated too.
v2: symmetric: a 94 column right of the window too (the open door stands in front of it anyway);
the 52 element is left out here."""
import math, sys

OUT = sys.argv[1]
V2 = sys.argv[2:] == ["v2"]
S, XA, YB = 200, 12.05, 13.05        # plan: px per metre, world x at left, world y at top
ML, MT = 30, 90
W, H = 1660, 1265 if sys.argv[2:] == ["v2"] else 1240


def X(x): return ML + (x - XA) * S
def Y(y): return MT + (YB - y) * S
def cm(a, b): return "%d" % round(abs(b - a) * 100)


o = []
def rect(x0, x1, y0, y1, cls):
    o.append(f'<rect x="{X(x0):.1f}" y="{Y(y1):.1f}" width="{(x1-x0)*S:.1f}" height="{(y1-y0)*S:.1f}" class="{cls}"/>')
def line(x0, y0, x1, y1, cls):
    o.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" class="{cls}"/>')
def text(x, y, s, cls, anchor="middle", rot=None):
    t = f' transform="rotate({rot} {X(x):.1f} {Y(y):.1f})"' if rot else ""
    o.append(f'<text x="{X(x):.1f}" y="{Y(y):.1f}" class="{cls}" text-anchor="{anchor}"{t}>{s}</text>')
def swing(hx, hy, r, a0, a1, cls="swing"):
    """Door: leaf from hinge (hx, hy) at angle a1 (open), arc back to a0 (closed); degrees, world."""
    pts = [(hx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 24)),
            hy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 24))) for i in range(25)]
    d = f"M{X(hx):.1f},{Y(hy):.1f} " + " ".join(f"L{X(x):.1f},{Y(y):.1f}" for x, y in pts[::-1])
    o.append(f'<path d="{d}" class="{cls}"/>')
def vdim(x, ys, labels, rot=-90):
    line(x, ys[0], x, ys[-1], "dim")
    for y in ys:
        line(x - 0.04, y - 0.04, x + 0.04, y + 0.04, "dim")
    for (a, b), s in zip(zip(ys, ys[1:]), labels):
        text(x + (0.03 if rot > 0 else -0.03), (a + b) / 2, s, "d", rot=rot)
def hdim(y, xs, labels):
    line(xs[0], y, xs[-1], y, "dim")
    for x in xs:
        line(x - 0.04, y - 0.04, x + 0.04, y + 0.04, "dim")
    for (a, b), s in zip(zip(xs, xs[1:]), labels):
        text((a + b) / 2, y + 0.03, s, "d")


# ------------------------------------------------------------------ coordinates (house_core)
E, EO = 14.575, 14.885               # east wall inner / outer face
FS, FSS = 8.876, 8.576               # Flur wall: Bibliothek face / Windfang face
FN, FNO = 12.473, 12.887             # north wall inner / outer face
WA, WB, SILL, HEAD = 10.315, 11.214, 1.0, 2.0     # east window (wall(), "W")
WF0, WF1 = 14.69, 14.77              # its frame in the wall (EG_Fenster_Tueren)
FDA, FDB = 12.867, 13.766            # north french door ("Balkontür")
WFX, WFA, WFB = 12.38, 8.45, 8.425   # Windfang wall east face, its door's north end, open north leaf
WFL = 13.324                         # tip of that leaf (opened 90 deg into the Flur)
OLD_A, OLD_B = 13.517, 14.575        # Büro door today (hinge at OLD_B, leaf along the east wall)
LEAF, LT0, LT1 = 1.002, 0.065, 0.025 # leaf length; leaf faces this far west of the hinge
ZC = 2.40                            # ceiling (Z_EG_TOP)
# the bookcase (regal_tegernsee.jpeg)
RH, BW, NW = 2.38, 0.94, 0.52        # height, wide / narrow element
D, DM = 0.42, 0.48                   # depth (estimated): columns, 52, bridge / middle base
M0 = (WA + WB) / 2 - BW / 2          # middle element centred on the window
M1, N1, S0 = M0 + BW, M0 + 2 * BW, M0 - (BW if V2 else NW)
BASE = 0.95                          # middle base top, 5 under the sill
BRIDGE = 2.02                        # bridge underside, 2 over the head
CORN, CO = 2.24, 0.03                # cornice bottom, overhang
# the Büro door moved west: open 90 deg its leaf and lever stand clear of the column (first drawn with 46,
# then 50 everywhere, as code/regal.py: a lever needs more than 6.5 cm)
SHIFT = 0.50
DA, DB = OLD_A - SHIFT, OLD_B - SHIFT
LX0, LX1 = DB - LT0, DB - LT1        # open leaf, x extent

assert M0 - WA <= 0 and M1 >= WB, "middle element must cover the window"
assert N1 <= FN, "north column runs into the north wall"
assert S0 - FS < LEAF, "check: leaf reaches past the 52 (else no shift needed)"
assert LX1 < E - D, "open door leaf hits the 52 element"
assert BASE < SILL and BRIDGE > HEAD and RH < ZC

# ------------------------------------------------------------------ walls
rect(E, EO, 8.25, WA, "wall"); rect(E, EO, WB, FNO, "wall")                  # east wall
rect(WF0, WF1, WA, WB, "win"); line((WF0 + WF1) / 2, WA, (WF0 + WF1) / 2, WB, "thin")
rect(XA, FDA, FN, FNO, "wall"); rect(FDB, E, FN, FNO, "wall")                # north wall
rect(FDA, FDB, FN + 0.15, FN + 0.23, "win")
rect(XA, DA, FSS, FS, "wall"); rect(OLD_B, EO, FSS, FS, "wall")             # Flur wall
rect(DB, OLD_B, FSS, FS, "new")                                              # closed up
rect(DA, OLD_A, FSS, FS, "cut")                                              # new opening
rect(12.25, WFX, WFA, FSS, "wall"); rect(12.25, WFX, 8.25, 8.25, "wall")     # Windfang wall stub
# old bookcase and old leaf (dashed)
rect(XA, 13.42, 8.88, 9.24, "abbr")
rect(E - LT0, E - LT1, FS, FS + LEAF, "abbr")
# the bookcase
rect(E - D, E, M1, N1, "cab"); rect(E - D, E, S0, M0, "cab")                 # 94 north, 52 south
rect(E - DM, E, M0, M1, "cab")                                               # middle base
rect(E - D - CO, E, M0, M1, "shelf")                                         # bridge over the window
rect(E - D - CO, E, S0 - CO, N1 + CO, "shelf")                               # cornice (above)
if not V2:
    line(E - 0.40, S0 + 0.02, E - 0.40, M0 - 0.02, "glass")                 # 52: glass door
# window leaves (over the base) and french door leaves, opening inwards (two each; closed -> open)
for h, a0, a1 in ((WA, 90, 180), (WB, -90, -180)):
    swing(WF0, h, (WB - WA) / 2, a0, a1, "opt")
for h, a0, a1 in ((FDA, 0, -90), (FDB, 180, 270)):
    swing(h, FN + 0.15, (FDB - FDA) / 2, a0, a1, "opt")
# the moved door
swing(DB, FS, LEAF, 180, 90)
rect(LX0, LX1, FS, FS + LEAF, "leaf")
rect(WFX, WFL, WFB - 0.04, WFB, "leafo")                                    # Windfang leaf, open

# ------------------------------------------------------------------ labels
text(E - D / 2 + 0.02, (M1 + N1) / 2, "Säule 94", "w", rot=-90)
text(E - DM / 2 + 0.02, (M0 + M1) / 2 + 0.2, "Mitte 94", "w", rot=-90)
text(E - D / 2 + 0.02, (S0 + M0) / 2, "Säule 94" if V2 else "Vitrine 52", "w", rot=-90)
text(13.15, 11.3, "Bibliothek", "h"); text(13.15, 11.15, "(Büro)", "s")
text(12.75, 9.12, "Bücherwand alt (entfällt)", "n")
text(13.15, 8.33, "Windfang", "s2")
text((FDA + FDB) / 2, FNO + 0.06, "Balkontür", "s2")
text(EO + 0.06, (WA + WB) / 2, f"Fenster BRH {cm(0, SILL)}", "s2", rot=90)
text(13.5, 9.55, "Tür neu, 90° offen", "n", anchor="end")
text(E - LT0 - 0.02, (FS + S0) / 2 if V2 else FS + LEAF / 2, "Tür heute", "s2", anchor="end", rot=-90)
# section marks
for x, y, dx, dy, s in ((13.9, 12.15, 0.2, 0, "A"), (13.9, 9.98, 0.2, 0, "A"), (13.75, 10.76, 0, 0.2, "B")):
    o.append(f'<line x1="{X(x):.1f}" y1="{Y(y):.1f}" x2="{X(x + dx):.1f}" y2="{Y(y + dy):.1f}" class="arrow"/>')
    text(x - 0.07, y - 0.03, s, "c")
line(13.9, 9.98, 13.9, 12.15, "axis"); line(13.65, 10.76, E, 10.76, "axis")

# ------------------------------------------------------------------ dimensions (cm, from the coordinates)
vdim(15.12, [FS, S0, M0, M1, N1, FN], [cm(FS, S0), cm(S0, M0), cm(M0, M1), cm(M1, N1), cm(N1, FN)], rot=90)
vdim(15.35, [FS, WA, WB, FN], [cm(FS, WA), cm(WA, WB), cm(WB, FN)], rot=90)
vdim(15.58, [FS, FN], [cm(FS, FN) + " lichte Wandlänge"], rot=90)
hdim(8.12, [DA, DB, OLD_B], [cm(DA, DB) + f" Tür ({cm(0, SHIFT)} nach W)", cm(DB, OLD_B) + " zu"])
hdim(12.36, [FDB, E - D], [cm(FDB, E - D) + " frei"])                      # Balkontür -> column
hdim(N1 - 0.10, [E - D, E], [cm(0, D)])
hdim(M1 - 0.10, [E - DM, E], [cm(0, DM)])
hdim(9.70, [LX1, E - D], [("%.1f" % ((E - D - LX1) * 100)).replace(".", ",")])
text(E - D - 0.03, 9.62, "Luft", "s2", anchor="end")
hdim(8.70, [WFL, LX0], [cm(WFL, LX0) + " frei"])

# ------------------------------------------------------------------ A: elevation of the east wall (looking east)
SA, AX, AZ = 150, 760, 520          # north left, south right
def ax(y): return AX + (12.95 - y) * SA
def az(z): return AZ - z * SA
def arect(y0, y1, z0, z1, cls):
    a, b = sorted((ax(y0), ax(y1)))
    o.append(f'<rect x="{a:.1f}" y="{az(z1):.1f}" width="{b-a:.1f}" height="{(z1-z0)*SA:.1f}" class="{cls}"/>')
def aline(y0, z0, y1, z1, cls):
    o.append(f'<line x1="{ax(y0):.1f}" y1="{az(z0):.1f}" x2="{ax(y1):.1f}" y2="{az(z1):.1f}" class="{cls}"/>')
def atext(y, z, s, cls, anchor="middle", rot=None):
    t = f' transform="rotate({rot} {ax(y):.1f} {az(z):.1f})"' if rot else ""
    o.append(f'<text x="{ax(y):.1f}" y="{az(z):.1f}" class="{cls}" text-anchor="{anchor}"{t}>{s}</text>')
def doors(y0, y1, z0, z1, n, cls="cab"):
    w = (y1 - y0) / n
    for k in range(n):
        a, b = y0 + k * w, y0 + (k + 1) * w
        arect(a + 0.015, b - 0.015, z0 + 0.015, z1 - 0.015, cls)
        arect(a + 0.07, b - 0.07, z0 + 0.07, z1 - 0.07, "panel")
def column(y0, y1, shelves, cab_top):
    """Front view of one element: carcass, plinth, cabinet doors, open shelves, frieze, cornice."""
    arect(y0, y1, 0, CORN, "cab")
    arect(y0 + 0.03, y1 - 0.03, cab_top, 2.11, "open")
    for z in shelves:
        arect(y0 + 0.03, y1 - 0.03, z - 0.025, z, "cab")
    arect(y0 + 0.01, y1 - 0.01, 0, 0.10, "cab")
    doors(y0 + 0.03, y1 - 0.03, 0.10, cab_top, 2 if y1 - y0 > 0.6 else 1)

o.append(f'<text x="{ax(10.7):.1f}" y="{az(ZC) - 46:.1f}" class="t" text-anchor="middle">A · Ansicht Ostwand (Blick nach Osten: links N, rechts S)</text>')
arect(FN, 12.95, -0.15, ZC + 0.15, "wall")                                   # north wall (cut, solid at A)
arect(FSS, FS, HEAD, ZC + 0.15, "wall")                                      # Flur wall: A cuts the door, lintel
arect(FSS, 12.95, -0.15, 0, "wall"); arect(FSS, 12.95, ZC, ZC + 0.15, "wall")
arect(WA, WB, SILL, HEAD, "win")
aline((WA + WB) / 2, SILL, (WA + WB) / 2, HEAD, "thin")
for z in (1.33, 1.67):
    aline(WA + 0.05, z, WB - 0.05, z, "thin")
column(M1, N1, [0.66, 1.03, 1.46, 1.83], 0.66)                               # 94 north (photo, left bay)
if V2:
    column(S0, M0, [0.66, 1.03, 1.46, 1.83], 0.66)                           # 94 south, like the north one
else:
    arect(S0, M0, 0, CORN, "cab"); arect(S0 + 0.01, M0 - 0.01, 0, 0.10, "cab")  # 52: vitrine
    doors(S0 + 0.03, M0 - 0.03, 0.10, 0.68, 1)
    arect(S0 + 0.05, M0 - 0.05, 0.70, 2.09, "glassf")
    for z in (1.04, 1.44, 1.85):
        aline(S0 + 0.06, z, M0 - 0.06, z, "thin")
arect(M0, M1, 0, BASE, "cab"); arect(M0 + 0.03, M1 - 0.03, 0.52, BASE - 0.03, "open")   # middle base
arect(M0 + 0.01, M1 - 0.01, 0, 0.10, "cab"); doors(M0 + 0.03, M1 - 0.03, 0.10, 0.49, 2)
arect(M0, M1, BRIDGE, CORN, "cab")                                           # bridge: frieze over the window
arect(S0 - CO, N1 + CO, CORN, RH, "cab")                                     # cornice
for z in (CORN + 0.04, RH - 0.03):
    aline(S0 - CO, z, N1 + CO, z, "thin")
arect(FS, FS + LEAF, 0.01, 1.97, "leafa")                                    # open door leaf, in front
atext(FS + LEAF / 2, 1.0, "Türblatt offen", "n", rot=-90)
def azdim(y, zs, labels):
    aline(y, zs[0], y, zs[-1], "dim")
    for z in zs:
        aline(y - 0.027, z - 0.027, y + 0.027, z + 0.027, "dim")
    for (a, b), s in zip(zip(zs, zs[1:]), labels):
        atext(y + 0.03, (a + b) / 2, s, "d", rot=-90)
def ahdim(z, ys, labels):
    aline(ys[0], z, ys[-1], z, "dim")
    for y in ys:
        aline(y - 0.027, z - 0.027, y + 0.027, z + 0.027, "dim")
    for (a, b), s in zip(zip(ys, ys[1:]), labels):
        atext((a + b) / 2, z - 0.03, s, "d")
zs = [0, BASE, SILL, HEAD, BRIDGE, RH, ZC]
zr = [round(z * 100) for z in zs]
azdim(8.30, zs, ["%d" % (b - a) for a, b in zip(zr, zr[1:])])
ahdim(-0.32, [FN, N1, M1, M0, S0, FS], [cm(N1, FN), cm(M1, N1), cm(M0, M1), cm(S0, M0), cm(FS, S0)])
for z, s in ((BASE, f"Unterteil {cm(0, BASE)}"), (SILL + 0.03, f"BRH {cm(0, SILL)}"), (HEAD - 0.05, f"Sturz {cm(0, HEAD)}"),
             (BRIDGE + 0.06, f"Brücke ab {cm(0, BRIDGE)}"), (RH + 0.01, f"OK Regal {cm(0, RH)}")):
    atext(8.22, z - 0.03, s, "n", anchor="start")
atext(10.7, -0.55, f"Raumhöhe {cm(0, ZC)} · Fächer, Türen und Höhen nach Foto geschätzt", "s2")

# ------------------------------------------------------------------ B: section through the window (looking north)
SB, BX, BZ = 160, 1340, 1045       # west left, east right
def bx(x): return BX + (x - 14.0) * SB
def bz(z): return BZ - z * SB
def brect(x0, x1, z0, z1, cls):
    o.append(f'<rect x="{bx(x0):.1f}" y="{bz(z1):.1f}" width="{(x1-x0)*SB:.1f}" height="{(z1-z0)*SB:.1f}" class="{cls}"/>')
def bline(x0, z0, x1, z1, cls):
    o.append(f'<line x1="{bx(x0):.1f}" y1="{bz(z0):.1f}" x2="{bx(x1):.1f}" y2="{bz(z1):.1f}" class="{cls}"/>')
def btext(x, z, s, cls, anchor="middle", rot=None):
    t = f' transform="rotate({rot} {bx(x):.1f} {bz(z):.1f})"' if rot else ""
    o.append(f'<text x="{bx(x):.1f}" y="{bz(z):.1f}" class="{cls}" text-anchor="{anchor}"{t}>{s}</text>')
o.append(f'<text x="{bx(13.72):.1f}" y="{bz(ZC) - 62:.1f}" class="t" text-anchor="start">B · Schnitt Fenster (Blick nach N)</text>')
brect(E - D, E, 0, RH, "beyond")                                             # 94 column behind, seen
brect(E, EO, -0.15, SILL, "wall"); brect(E, EO, HEAD, ZC + 0.15, "wall")
brect(WF0, WF1, SILL, HEAD, "win")
brect(13.6, EO, -0.15, 0, "wall"); brect(13.6, EO, ZC, ZC + 0.15, "wall")
brect(E - DM, E, 0, BASE, "cabc"); brect(E - DM + 0.03, E - 0.012, 0, 0.10, "cab")
brect(E - D, E, BRIDGE, CORN, "cabc"); brect(E - D - CO, E, CORN, RH, "cabc")
brect(WF0 - (WB - WA) / 2, WF0, SILL, HEAD, "leafb")                         # north window leaf, open 90
btext(WF0 - (WB - WA) / 4, 1.5, "Flügel offen", "n", rot=-90)
def bhdim(z, xs, labels):
    bline(xs[0], z, xs[-1], z, "dim")
    for x in xs:
        bline(x - 0.025, z - 0.025, x + 0.025, z + 0.025, "dim")
    for (a, b), s in zip(zip(xs, xs[1:]), labels):
        btext((a + b) / 2, z + 0.03, s, "d")
bhdim(-0.30, [E - DM, E, WF0, WF1, EO], [cm(0, DM), cm(E, WF0), "", cm(WF1, EO)])
bhdim(ZC + 0.22, [E - D - CO, E - D, E], [cm(0, CO), cm(0, D)])
btext(E - DM / 2, 0.55, "Unterteil", "w"); btext(E - D / 2, 2.12, "Brücke", "w")

# ------------------------------------------------------------------ title, notes, legend
LX, LY = 30, 1110
notes = [("t", "Vorschlag v1 · Regal vom Tegernsee um das Ostfenster der Bibliothek"),
         ("s", f"Blick aufs Fenster: links (N) Säule 94, Mitte 94 geteilt, rechts (S) Vitrine 52; zusammen "
               f"{cm(S0, N1)} von {cm(FS, FN)} Wand."),
         ("s", f"Mitte genau über dem Fenster ({cm(WA, WB)}): unten Sockelschrank + offenes Fach bis {cm(0, BASE)}, "
               f"oben eine Brücke {cm(BRIDGE, CORN)} + Gesims {cm(CORN, RH)} (kein Fach: nur {cm(HEAD, RH)} über dem Sturz)."),
         ("s", f"Bürotür {cm(0, SHIFT)} nach Westen (Band weiter östlich): 90° offen bleibt "
               + ("%.1f" % ((E - D - LX1) * 100)).replace(".", ",") + " Luft zur Vitrine. "
               + f"Mit offenem Windfang-Flügel {cm(WFL, LX0)} frei."),
         ("q", f"Geschätzt: Tiefe {cm(0, D)} (Mitte unten {cm(0, DM)}), Fächer und Türen nach Foto. "
               f"Nord: {cm(N1, FN)} bis zur Ecke bleiben frei (Blende?)."),
         ("q", "Offen: Vitrine 52 – Glastür nach links (zur Tür hin) oder rechts? Brücke: Blende oder flaches Fach?")]
if V2:
    notes = [("t", "Variante v2 · symmetrisch: Säule 94 links und rechts vom Fenster"),
             ("s", f"Blick aufs Fenster: Säule 94 | Mitte 94 geteilt | Säule 94; zusammen {cm(S0, N1)} von {cm(FS, FN)} Wand, "
                   f"symmetrisch zum Fenster."),
             notes[2],
             ("s", f"Frei bleiben {cm(N1, FN)} zur Nordwand und {cm(FS, S0)} zur Flurwand. Vitrine 52: Westwand, NW-Eck hinter dem Klavier."),
             ("s", f"Bürotür {cm(0, SHIFT)} nach Westen (Band weiter östlich): 90° offen bleibt "
                   + ("%.1f" % ((E - D - LX1) * 100)).replace(".", ",") + " Luft zur rechten Säule. "
                   + f"Mit offenem Windfang-Flügel {cm(WFL, LX0)} frei."),
             ("q", f"Die offene Bürotür steht {cm(S0, FS + LEAF)} breit vor der rechten Säule: deren rechte Sockeltür "
                   f"geht nur bei geschlossener Bürotür auf."),
             ("q", f"Geschätzt: Tiefe {cm(0, D)} (Mitte unten {cm(0, DM)}), Fächer und Türen nach Foto. "
                   f"Offen: Brücke Blende oder flaches Fach?")]
for cls, s in notes:
    o.append(f'<text x="{LX}" y="{LY}" class="{cls}">{s}</text>')
    LY += 26 if cls == "t" else 21
legend = [("wall", "Wand Bestand"), ("new", "Wand neu (Tür zu)"), ("cut", "Durchbruch neu"),
          ("cab", "Regal"), ("shelf", "Regal oben (Brücke, Gesims)"), ("abbr", "entfällt / heute"),
          ("leaf", "Türblatt neu"), ("leafo", "Türblatt Bestand"), ("opt", "Fenster-/Balkontürflügel")]
for i, (cls, s) in enumerate(legend):
    lx, ly = 1130 + (i % 2) * 260, 1132 + (i // 2) * 24
    o.append(f'<rect x="{lx}" y="{ly-13}" width="34" height="16" class="{cls}"/>')
    o.append(f'<text x="{lx+42}" y="{ly}" class="s">{s}</text>')
o.append(f'<text x="{ML}" y="34" class="t">Schrank im Büro: Regal Tegernsee ({"Variante v2" if V2 else "Vorschlag v1"}, 2026-11-11)</text>')
o.append(f'<text x="{ML}" y="56" class="s2">Grundriss EG, Ansicht A und Schnitt B, nicht maßstäblich; Maße in cm '
         f'(lichte Maße aus house_core; Regal 238 hoch, Elemente 94/94/94/52)</text>')
o.append(f'<path d="M{X(12.35):.1f},{Y(12.95):.1f} l-9,24 l9,-7 l9,7 z" fill="#333"/>')
o.append(f'<text x="{X(12.35):.1f}" y="{Y(12.95) - 4:.1f}" class="s" text-anchor="middle">N</text>')

STYLE = """<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="6" height="6" fill="#ddd"/><line x1="0" y1="0" x2="0" y2="6" stroke="#999" stroke-width="1.5"/></pattern>
<marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#26a"/></marker></defs>
<style>
.wall{fill:url(#hatch);stroke:#555;stroke-width:1}.win{fill:#fff;stroke:#555;stroke-width:1}.thin{stroke:#555;stroke-width:1}
.new{fill:#d33;stroke:#900;stroke-width:1}.cut{fill:#fff;stroke:#d33;stroke-width:1.5;stroke-dasharray:5 3}
.abbr{fill:none;stroke:#555;stroke-width:1;stroke-dasharray:3 3}
.axis{stroke:#26a;stroke-width:0.8;stroke-dasharray:10 3 2 3}
.cab{fill:#8a5a3c;stroke:#3a2214;stroke-width:1}.cabc{fill:#6b4029;stroke:#2a170c;stroke-width:1.5}
.panel{fill:none;stroke:#3a2214;stroke-width:1}.open{fill:#4a2c1c;stroke:#3a2214;stroke-width:1}
.glassf{fill:#9fb7c4;fill-opacity:0.55;stroke:#3a2214;stroke-width:1}.glass{stroke:#26a;stroke-width:2}
.shelf{fill:none;stroke:#3a2214;stroke-width:1;stroke-dasharray:4 3}
.beyond{fill:#efe4d8;stroke:#865;stroke-width:1;stroke-dasharray:4 3}
.swing{fill:none;stroke:#777;stroke-width:1}.opt{fill:none;stroke:#aaa;stroke-width:1;stroke-dasharray:5 4}
.leaf{fill:#f6c;stroke:#900;stroke-width:1}.leafo{fill:#eee;stroke:#777;stroke-width:1}
.leafa{fill:#f6c;fill-opacity:0.35;stroke:#900;stroke-width:1;stroke-dasharray:5 3}
.leafb{fill:none;stroke:#26a;stroke-width:1;stroke-dasharray:5 3}
.arrow{stroke:#26a;stroke-width:2;marker-end:url(#ah)}.dim{stroke:#333;stroke-width:1}
text{font-family:Helvetica,Arial,sans-serif}
.t{font-size:20px;font-weight:bold}.t2{font-size:15px;font-weight:bold;fill:#900}.s{font-size:15px}.s2{font-size:12px;fill:#555}
.n{font-size:12px;fill:#900}.q{font-size:14px;fill:#a60;font-style:italic}.c{font-size:13px;fill:#26a;font-weight:bold}
.d{font-size:12px;fill:#000;font-weight:bold}.w{font-size:12px;fill:#fff;font-weight:bold}.h{font-size:18px;font-weight:bold}
</style>"""
with open(OUT, "w") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n{STYLE}'
            f'<rect width="{W}" height="{H}" fill="#fff"/>\n' + "\n".join(o) + "\n</svg>\n")
print(OUT)
