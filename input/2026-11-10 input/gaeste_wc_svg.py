"""Draws the proposal WC + Garderobe at the back entrance (v1) as SVG, world coordinates from
house_core (metres): plan (north up) and a section looking south from the Flur.
Usage: python3 gaeste_wc_svg.py gaeste_wc_v1.svg
       python3 gaeste_wc_svg.py gaeste_wc_v2.svg v2
       python3 gaeste_wc_svg.py gaeste_wc_v3.svg v3
v2: WC north wall (Bestand) rebuilt 5 cm further north, hand basin moved out of the WC onto the
Flur east wall south of the Windfang door.
v3: wall stays (Bestand), WC centred in the room, bench up to the north wall, basin centred on the
Flur wall piece, blue tiles behind it, mirror with a 7 cm wooden frame; plus an elevation of that wall."""
import math, sys

OUT = sys.argv[1]
V2, V3 = sys.argv[2:] == ["v2"], sys.argv[2:] == ["v3"]
FL = V2 or V3                        # hand basin in the Flur
S, XA, YB = 200, -0.55, 8.85         # plan: px per metre, world x at left, world y at top
ML, MT = 30, 80
W, H = 1620, 1500 if V3 else 1110


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
WI, WO = 0.31, 2.358                 # WC inner west / east face (Bestand)
YS, YN, YF = 5.475, 6.574, 6.723     # WC south face, north wall room / Flur face
YN0, YF0 = YN, YF                    # Bestand
DY = 0.05 if V2 else 0.0             # v2: north wall rebuilt 5 cm further into the Flur
YN, YF = YN + DY, YF + DY
PA, PB = 1.319, 1.419                # new partition (east face = existing door jamb)
DA, DB = 0.48, 1.24                  # new WC door, rough opening 76, hinged at DB (partition side)
GA, GB = 1.419, 2.218                # existing opening (old WC door) -> Garderobe
WINA, WINB, SILL = 5.724, 6.324, 1.57
BDA, BDB = 7.408, 8.377              # back door, hinged north, opens into the Flur (plan)
FWA, FWB = 7.408, 8.506              # Windfang door (plan: into the Gang, hinged north)
TX, TD = 0.90, 0.69                  # WC axis, depth from the wall incl. tiles (house_core.toilet)
if V3:
    TX = (WI + PA) / 2               # WC centred between west wall and partition
BA, BB, BD = 6.10, 6.50, 0.29        # hand basin 40 x 28 (+1 tile) on the west wall
BK, BL = 0.35, 1.00                  # bench depth / length, east wall
if V3:
    BL = YN - YS                     # bench from wall to wall
if FL:                               # basin on the Flur east wall, centred between WC wall and Windfang door
    BA, BB = (YF + FWA) / 2 - 0.20, (YF + FWA) / 2 + 0.20
TILE = 0.015 + 14 * 0.075 + 0.05     # wainscot top (house_core.wainscot)
MF, MGW, MGH, MZ = 0.07, 0.40, 0.60, 1.20   # v3 mirror: frame width, glass w x h, bottom of frame

# clearance checks: door sweeps must not meet each other (quarter circles)
assert math.dist((DB, YF), (WI, BDB)) > (DB - DA) + (BDB - BDA), "WC door hits back door"
assert DB <= GA, "WC door sweep reaches the Garderobe door sweep"
assert abs((PA - WI) + (PB - PA) + (WO - PB) - (WO - WI)) < 1e-9

# ------------------------------------------------------------------ walls (Bestand)
WALLS = [(0, WI, 5.145, WINA), (0, WI, WINB, BDA), (0, WI, BDB, YB),           # west facade
         (WI, WO, 5.145, YS),                                                  # WC south (annex)
         (WO, 2.772, 4.75, 5.849), (WO, 3.95, 5.849, 6.349),                    # Speis / Küche-Flur wall
         (WO, 2.657, 6.349, FWA), (WO, 2.657, FWB, YB),                         # Windfang wall
         (WI, WO, 8.506, 8.656)]                                               # Flur north (closed door)
NORTH = [(WI, DA, YN, YF), (DB, GA, YN, YF), (GB, WO, YN, YF)]                 # WC north wall
for w in WALLS[:-1] + ([] if V2 else NORTH) + WALLS[-1:]:
    rect(*w, "wall")
rect(0, WI, WINA, WINB, "win"); line(0.155, WINA, 0.155, WINB, "thin")
if V2:
    rect(WI, WO, YN0, YF0, "abbr")                                             # Bestand, Abbruch
    for w in NORTH:
        rect(*w, "new")                                                        # neu, 5 cm nach Norden
else:
    rect(DA, DB, YN, YF, "cut")                                                # Durchbruch neu
rect(PA, PB, YS, YN, "new")                                                    # Trennwand neu
# sanitary: WC (cistern + bowl), hand basin
rect(TX - 0.20, TX + 0.20, YS + 0.01, YS + 0.22, "fix")
r = 0.18
pts = [(TX - r, YS + 0.17), (TX - r, YS + TD - r)] + \
      [(TX - r * math.cos(math.pi * i / 16), YS + TD - r + r * math.sin(math.pi * i / 16)) for i in range(17)] + \
      [(TX + r, YS + 0.17)]
o.append('<path d="M' + " L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts) + ' z" class="fix"/>')
o.append(f'<ellipse cx="{X(TX):.1f}" cy="{Y(YS + 0.47):.1f}" rx="{0.12*S:.1f}" ry="{0.16*S:.1f}" class="fixl"/>')
line(TX, YS + 0.02, TX, YS + TD + 0.04, "axis")
if V3:
    rect(WO - 0.012, WO, YF, FWA, "tile")                                      # wall tiles behind the basin
    rect(WO - BD, WO - 0.012, BA, BB, "fix"); rect(WO - BD + 0.03, WO - 0.05, BA + 0.03, BB - 0.03, "fixl")
    m = (BA + BB) / 2
    rect(WO - 0.040, WO - 0.012, m - MGW / 2 - MF, m + MGW / 2 + MF, "board")  # mirror frame (above)
    rect(WO - 0.030, WO - 0.012, m - MGW / 2, m + MGW / 2, "mirror")
elif V2:
    rect(WO - BD, WO, BA, BB, "fix"); rect(WO - BD + 0.03, WO - 0.04, BA + 0.03, BB - 0.03, "fixl")
    rect(WO - 0.015, WO, BA - 0.05, BB + 0.05, "mirror")                       # mirror above
else:
    rect(WI, WI + BD, BA, BB, "fix"); rect(WI + 0.04, WI + BD - 0.03, BA + 0.03, BB - 0.03, "fixl")
# Garderobe: bench, hook board, hat shelf (dashed, above)
rect(WO - BK, WO, YS, YS + BL, "cab")
rect(WO - 0.02, WO, YS, YS + BL, "board")
rect(WO - 0.28, WO, YS, YS + BL, "shelf")
for i in range(6):
    y = YS + 0.10 + i * (BL - 0.20) / 5
    line(WO - 0.02, y, WO - 0.12, y, "hook")
# doors
swing(DB, YF, DB - DA, 180, 90)                                               # WC: outward, hinge east
rect(DB - 0.04, DB, YF, YF + (DB - DA), "leaf")
if not FL:
    swing(GB, YF, GB - GA, 180, 90, "opt")                                     # Garderobe: optional
swing(WI, BDB, BDB - BDA, -90, 0)                                              # back door (plan)
rect(WI, WI + (BDB - BDA), BDB - 0.04, BDB, "leafo")
swing(2.657, FWB, FWB - FWA, -90, 0)                                           # Windfang door (plan)
rect(2.657, 2.657 + (FWB - FWA), FWB - 0.04, FWB, "leafo")

# ------------------------------------------------------------------ labels
aw, ag = (PA - WI) * (YN - YS), (WO - PB) * (YN - YS)
if V3:
    text(TX, 6.385, "WC (rechts)", "h"); text(TX, 6.295, f"{aw:.2f} m²".replace(".", ","), "s")
else:
    text(0.95, 6.42, "WC (rechts)", "h"); text(0.95, 6.32, f"{aw:.2f} m²".replace(".", ","), "s")
text((PB + WO - BK) / 2, 6.40, "Garderobe", "h"); text((PB + WO - BK) / 2, 6.29, "(links)", "s")
text((PB + WO - BK) / 2, 6.19, f"{ag:.2f} m²".replace(".", ","), "s")
text(WO - BK / 2, YS + BL / 2, f"Bank {cm(0, BK)} × {cm(0, BL)}", "s2", rot=-90)
text(1.33, 8.15, f"Flur (Hintereingang) {(WO - WI) * (8.506 - YF):.1f} m²".replace(".", ","), "h")
o.append(f'<line x1="{X(1.33):.1f}" y1="{Y(8.0):.1f}" x2="{X(1.33):.1f}" y2="{Y(7.62):.1f}" class="arrow"/>')
text(1.40, 7.84, "Blick vom Flur nach Süden", "c", anchor="start")
if FL:
    text(WO - BD - 0.04, (BA + BB) / 2 + 0.02, "HWB 40/28", "n", anchor="end")
    text(WO - BD - 0.04, (BA + BB) / 2 - 0.07, "Spiegel darüber", "n", anchor="end")
else:
    text(0.50, 5.95, "HWB 40/28", "n")
text(-0.10, (BDA + BDB) / 2, "Hintertür", "s2", rot=-90)
text(-0.10, (WINA + WINB) / 2 + 0.33, f"Fenster, BRH {cm(0, SILL)}", "s2", rot=-90)
text(3.35, 7.25, "Windfangtür (Plan:", "s2"); text(3.35, 7.13, "schlägt in den Gang)", "s2")
text(3.35, 6.75, "Gang", "s2"); text(3.35, 5.4, "Speis", "s2")
text(1.33, 5.03, "Anbau", "s2")

# ------------------------------------------------------------------ dimensions (cm, from the coordinates)
hdim(4.88, [WI, PA, PB, WO], [cm(WI, PA), cm(PA, PB), cm(PB, WO)])
hdim(4.68, [WI, WO], [cm(WI, WO) + " lichte Breite (Bestand)"])
hdim(YN - 0.10 if FL else 7.0, [WI, DA, DB, GA, GB, WO],
     [cm(WI, DA), cm(DA, DB) + " neu", cm(DB, GA), cm(GA, GB) + (" neu" if V2 else " Bestand"), cm(GB, WO)])
vdim(-0.42, [YS, YN], [cm(YS, YN) + " Tiefe" + (" (+5)" if V2 else "")])
vdim(-0.22, [YS, WINA, WINB, YN], [cm(YS, WINA), cm(WINA, WINB), cm(WINB, YN)])
vdim(1.24, [YS, YS + TD, YN], [cm(0, TD) + " WC", cm(YS + TD, YN) + " frei"], rot=90)
if FL:
    hdim(6.19 if V3 else 6.215, [WI, TX, PA], [cm(WI, TX), cm(TX, PA)])
    hdim(5.78, [PB, WO - BK], [cm(PB, WO - BK) + " frei"])
    vdim(2.80, [YF, BA, BB, FWA], [cm(YF, BA), cm(BA, BB), cm(BB, FWA)], rot=90)   # Flur east wall
    hdim(7.17, [DB, WO - BD], [cm(DB, WO - BD) + " frei"])             # open WC door leaf -> basin
    if V2:
        vdim(0.42, [YF, BDA], [cm(YF, BDA)])                           # WC wall -> back door
else:
    hdim(6.215, [WI + BD, TX, PA], [cm(WI + BD, TX), cm(TX, PA)])
    hdim(5.78, [PB, WO - BK], [cm(PB, WO - BK) + " frei"])
    hdim(6.545, [WI + BD, DB], [cm(WI + BD, DB) + " frei"])           # basin front -> WC door jamb

# ------------------------------------------------------------------ section looking south (east on the left)
SE, EX, EY = 150, 1050, 520
def sx(x): return EX + (2.772 - x) * SE
def sz(z): return EY - z * SE
def srect(x0, x1, z0, z1, cls):
    a, b = sorted((sx(x0), sx(x1)))
    o.append(f'<rect x="{a:.1f}" y="{sz(z1):.1f}" width="{b-a:.1f}" height="{(z1-z0)*SE:.1f}" class="{cls}"/>')
def sline(x0, z0, x1, z1, cls):
    o.append(f'<line x1="{sx(x0):.1f}" y1="{sz(z0):.1f}" x2="{sx(x1):.1f}" y2="{sz(z1):.1f}" class="{cls}"/>')
def stext(x, z, s, cls, anchor="middle", rot=None):
    t = f' transform="rotate({rot} {sx(x):.1f} {sz(z):.1f})"' if rot else ""
    o.append(f'<text x="{sx(x):.1f}" y="{sz(z):.1f}" class="{cls}" text-anchor="{anchor}"{t}>{s}</text>')
def zdim(x, zs, labels):
    sline(x, zs[0], x, zs[-1], "dim")
    for z in zs:
        sline(x - 0.027, z - 0.027, x + 0.027, z + 0.027, "dim")
    for (a, b), s in zip(zip(zs, zs[1:]), labels):
        stext(x + 0.02, (a + b) / 2, s, "d", rot=-90)

o.append(f'<text x="{sx(1.386):.1f}" y="{sz(2.55) - 40:.1f}" class="t" text-anchor="middle">Schnitt, Blick vom Flur nach Süden</text>')
stext(1.89, 2.55 + 0.08, "links: Garderobe", "t2"); stext(0.81, 2.55 + 0.08, "rechts: WC", "t2")
srect(0, WI, -0.15, 2.55, "wall"); srect(WO, 2.772, -0.15, 2.55, "wall")
srect(PA, PB, 0, 2.40, "new"); srect(0, 2.772, -0.15, 0, "wall"); srect(0, 2.772, 2.40, 2.55, "wall")
srect(WI, PA, 0.015, TILE, "tile")                                            # WC wainscot (back wall)
srect(0.0, WI, SILL, SILL + 0.60, "winsec")                                    # window in the side wall
# WC front view
srect(TX - 0.215, TX + 0.215, 0.78, 0.81, "fix"); srect(TX - 0.20, TX + 0.20, 0.42, 0.78, "fix")
srect(TX - 0.18, TX + 0.18, 0.32, 0.445, "fix"); srect(TX - 0.10, TX + 0.10, 0.05, 0.32, "fix")
srect(TX - 0.13, TX + 0.13, 0.014, 0.05, "fix")
# hand basin on the west wall, seen from the side (v2: in the Flur, in front of the section)
if not FL:
    srect(WI, WI + BD, 0.70, 0.85, "fix"); sline(WI + BD - 0.04, 0.70, WI + BD - 0.04, 0.0, "leg")
    sline(WI + 0.17, 0.85, WI + 0.17, 0.95, "leg")
# Garderobe: bench, hook board, hooks, hat shelf (east wall, seen from the side)
srect(WO - BK, WO, 0.42, 0.46, "cab"); srect(WO - BK + 0.02, WO - BK + 0.05, 0.0, 0.42, "cab")
srect(WO - 0.02, WO, 0.46, 1.90, "board")
sline(WO - 0.02, 1.65, WO - 0.12, 1.65, "hook"); sline(WO - 0.12, 1.65, WO - 0.12, 1.69, "hook")
srect(WO - 0.28, WO, 1.85, 1.88, "cab"); sline(WO - 0.02, 1.70, WO - 0.20, 1.85, "hook")
# heights
zdim(2.92, [0, 0.45, 1.65, 1.85, 2.40], ["45", "120", "20", "55"])
for z, s in ((0.45, "Bank 45"), (1.65, "Haken 165"), (1.85, "Hutablage 185")):
    stext(3.02, z - 0.03 if z < 1.8 else z + 0.01, s, "n", anchor="end")
zs = [0, TILE, SILL, 2.40] if FL else [0, 0.85, TILE, SILL, 2.40]
zr = [round(z * 100) for z in zs]                                    # labels from rounded heights: chain = 240
lab = ["%d" % (b - a) for a, b in zip(zr, zr[1:])]
if not FL:
    lab[0] = "85 HWB"
zdim(-0.17, zs, lab)
stext(-0.37, TILE / 2, f"Fliesen bis ≈ {cm(0, TILE)}", "n", rot=-90)
stext(-0.37, SILL + 0.30, f"Fenster in der Seitenwand, BRH {cm(0, SILL)}", "n", rot=-90)
stext(1.386, -0.32, "Raumhöhe 240", "s2")

# ------------------------------------------------------------------ title, notes, legend
LX, LY = 960, 650
notes = [("t", "Vorschlag v1 · Gäste-WC am Hintereingang → WC + Garderobe"),
         ("s", "„Gang“ = Flur 3,7 m² am Hintereingang; Blick nach Süden: links Garderobe, rechts WC."),
         ("s", "Trennwand neu 10 cm (Ständerwand, WC-Seite gefliest), bündig mit der Laibung der"),
         ("s", "bestehenden Türöffnung (80) – die bleibt als Zugang zur Garderobe."),
         ("s", "WC-Tür neu: Durchbruch 76 (Rohbau), schlägt nach außen; Band an der Trennwand-"),
         ("s", "seite, so kommt sie der Hintertür nicht in die Quere."),
         ("s", "Tiefe 110 bleibt, WC an der Südwand wie im Plan. Ein Stand-WC wie Mallnitz (69 tief)"),
         ("s", "lässt 41 bis zur Wand, ≈ 55 bis zum Türblatt – darum schlägt die Tür nach außen auf."),
         ("s", "Wand-WC mit Vorwand (≈ 55–60 tief) gäbe ≈ 10 cm mehr."),
         ("s", "WC wie Mallnitz: Stand-WC mit Spülkasten, Handwaschbecken 40/28 auf Konsole,"),
         ("s", "Metrofliesen mit Abschlussleiste bis ≈ 112."),
         ("s", "Garderobe wie Mallnitz: Bank 35 tief an der Ostwand (links), Hakenbrett, Hutablage."),
         ("s2", "Alternative: Bank an der Rückwand (94 lang), davor 75 frei statt 59."),
         ("q", "Offen: Spiegel – über dem Becken ist das Fenster (BRH 157); an die Trennwand?"),
         ("q", "Offen: HWB ragt 12 in die WC-Türöffnung, Durchgang dort 64 (kleineres Becken?)."),
         ("q", "Offen: Windfangtür – schlägt sie in den Gang (Plan)? Im 3D-Modell öffnet sie in den"),
         ("q", "Flur und stünde offen 69 vor der Garderobe.")]
if V2:
    notes = [("t", "Variante v2 · WC-Wand +5 cm, Handwaschbecken im Flur"),
             ("s", "WC-Nordwand ist Bestand (15 cm, grau im Plan; im OG steht keine Wand darüber)."),
             ("s", f"5 cm „raus“ = Abbruch + neue Wand 15 cm: Tiefe WC/Garderobe {cm(YS, YN0)} → {cm(YS, YN)};"),
             ("s", f"Wandstück Flur bis zur Hintertür {cm(YF0, BDA)} → {cm(YF, BDA)}. Statik der Wand vorher klären."),
             ("s2", "Alternative: neue 10-cm-Ständerwand, Flurseite bleibt, wo sie ist → ebenfalls +5, Flur unverändert."),
             ("s", f"HWB 40/28 an der Flur-Ostwand rechts neben der Windfangtür (Wandstück {cm(YF, FWA)}),"),
             ("s", f"Spiegel darüber; zwischen offener WC-Tür und Becken {cm(DB, WO - BD)} frei."),
             ("s", f"WC ohne Becken: Stand-WC {cm(0, TD)} tief, {cm(YS + TD, YN)} bis zur Wand; Türöffnung ohne Engstelle."),
             ("s", f"Garderobe wie v1: Bank {cm(0, BK)} an der Ostwand, {cm(PB, WO - BK)} frei; Tiefe jetzt {cm(YS, YN)}."),
             ("s2", f"Alternative: Bank an der Rückwand ({cm(PB, WO)} lang), davor {cm(YS + BK, YN)} frei."),
             ("q", "Garderobe ohne Tür: eine Tür nach außen schlüge gegen das Becken."),
             ("q", "Offen: Zu-/Abwasser zum HWB – vom WC her im Boden unter der Garderobe?"),
             ("q", "Windfangtür: Becken frei, ob sie in den Gang (Plan) oder in den Flur (3D-Modell,"),
             ("q", "Band Nord) aufschlägt.")]
if V3:
    notes = [("t", "Variante v3 · Wand bleibt, WC mittig, Becken im Flur"),
             ("s", "WC-Nordwand bleibt Bestand (15 cm), WC-Tür wie v1: Durchbruch 76, schlägt nach außen."),
             ("s", f"WC mittig im Raum ({cm(WI, TX)}/{cm(TX, PA)} zur Achse); {cm(YS + TD, YN)} vor dem WC bis zur Wand."),
             ("s", f"Bank {cm(0, BK)} × {cm(0, BL)} an der Ostwand von Wand zu Wand; daneben {cm(PB, WO - BK)} frei."),
             ("s", f"Sie ragt {cm(WO - BK, GB)} in die Garderobenöffnung (80), Durchgang dort {cm(GA, WO - BK)}."),
             ("s", f"HWB 40/28 mittig im Wandstück Windfangtür–Pfeiler ({cm(YF, FWA)}), 85 hoch;"),
             ("s", f"zwischen offener WC-Tür und Becken {cm(DB, WO - BD)} frei."),
             ("s", f"Wandstück hinter dem Becken mit Metrofliesen taubenblau wie im WC, bis ≈ {cm(0, TILE)}."),
             ("s", f"Spiegel {cm(0, MGW)} × {cm(0, MGH)} im Holzrahmen {cm(0, MF)} breit → außen "
                   f"{cm(0, MGW + 2 * MF)} × {cm(0, MGH + 2 * MF)}, UK {cm(0, MZ)}."),
             ("q", f"Rahmen lässt je {cm(0, (FWA - YF - MGW - 2 * MF) / 2)} zur Ecke bzw. Windfangtür – reicht das neben deren"),
             ("q", "Türbekleidung? Sonst Glas 36 breit."),
             ("q", "Garderobe ohne Tür (eine Tür nach außen schlüge gegen das Becken)."),
             ("q", "Offen: Zu-/Abwasser zum HWB – vom WC her im Boden unter der Garderobe?")]
y = LY
for cls, s in notes:
    o.append(f'<text x="{LX}" y="{y}" class="{cls}">{s}</text>')
    y += 26 if cls == "t" else 22
legend = [("wall", "Wand Bestand"), ("new", "Wand neu"), ("cut", "Durchbruch neu"),
          ("fix", "Sanitär"), ("cab", "Bank / Ablage (Holz)"), ("shelf", "Hutablage (oben)"),
          ("leaf", "Türblatt neu"), ("opt", "Tür optional")]
if V2:
    legend[2], legend[7] = ("abbr", "Abbruch Bestand"), ("mirror", "Spiegel")
if V3:
    legend[7:] = [("tile", "Fliesen taubenblau"), ("mirror", "Spiegel"), ("board", "Holzrahmen / Hakenbrett")]
y += 10
for i, (cls, s) in enumerate(legend):
    lx, ly = LX + (i % 3) * 200, y + (i // 3) * 26
    o.append(f'<rect x="{lx}" y="{ly-13}" width="34" height="16" class="{cls}"/>')
    o.append(f'<text x="{lx+42}" y="{ly}" class="s">{s}</text>')
o.append(f'<text x="{ML}" y="34" class="t">Gäste-WC Hintereingang: WC + Garderobe ({"Variante v2" if V2 else "Variante v3" if V3 else "Vorschlag v1"}, 2026-11-10)</text>')
o.append(f'<text x="{ML}" y="56" class="s2">Grundriss EG und Schnitt, nicht maßstäblich; Maße in cm (lichte Maße aus house_core; Bestand nach Plan 2026-11-03)</text>')
# north arrow
o.append(f'<path d="M{X(3.7):.1f},{Y(4.95):.1f} l-9,24 l9,-7 l9,7 z" fill="#333"/>')
o.append(f'<text x="{X(3.7):.1f}" y="{Y(4.95) - 4:.1f}" class="s" text-anchor="middle">N</text>')

# ------------------------------------------------------------------ v3: elevation of the Flur east wall
if V3:
    SA, AX, AZ = 150, 100, 1420                  # px per metre; looking east: north left, south right
    def ax(y): return AX + (8.70 - y) * SA
    def az(z): return AZ - z * SA
    def arect(y0, y1, z0, z1, cls):
        a, b = sorted((ax(y0), ax(y1)))
        o.append(f'<rect x="{a:.1f}" y="{az(z1):.1f}" width="{b-a:.1f}" height="{(z1-z0)*SA:.1f}" class="{cls}"/>')
    def aline(y0, z0, y1, z1, cls):
        o.append(f'<line x1="{ax(y0):.1f}" y1="{az(z0):.1f}" x2="{ax(y1):.1f}" y2="{az(z1):.1f}" class="{cls}"/>')
    def atext(y, z, s, cls, anchor="middle", rot=None):
        t = f' transform="rotate({rot} {ax(y):.1f} {az(z):.1f})"' if rot else ""
        o.append(f'<text x="{ax(y):.1f}" y="{az(z):.1f}" class="{cls}" text-anchor="{anchor}"{t}>{s}</text>')
    o.append(f'<text x="{ax(7.6):.1f}" y="{az(2.55) - 30:.1f}" class="t" text-anchor="middle">Ansicht Flur-Ostwand (Blick nach Osten)</text>')
    arect(8.506, 8.656, -0.15, 2.55, "wall"); arect(YN, YF, -0.15, 2.55, "wall")    # Flur north / WC north (cut)
    arect(YF, 8.506, -0.15, 0, "wall"); arect(YF, 8.506, 2.40, 2.55, "wall")        # floor / ceiling
    arect(FWA, FWB, 0, 2.0, "win")                                                   # Windfang door (glazed)
    for yy in ((FWA + FWB) / 2,):
        aline(yy, 0, yy, 2.0, "thin")
    aline(FWA + 0.08, 1.1, FWB - 0.08, 1.1, "thin")
    atext((FWA + FWB) / 2, 2.08, "Windfangtür", "s2")
    arect(YF, FWA, 0.015, TILE, "tile")                                              # tiles behind the basin
    m = (BA + BB) / 2
    arect(BA, BB, 0.70, 0.85, "fix"); arect(BA + 0.04, BB - 0.04, 0.74, 0.83, "fixl")   # basin
    for yy in (BA + 0.07, BB - 0.07):
        aline(yy, 0.70, yy, 0.0, "leg")                                              # chrome legs (Mallnitz)
    aline(BA + 0.07, 0.25, BB - 0.07, 0.25, "leg")
    aline(m + 0.06, 0.85, m + 0.06, 0.97, "leg"); aline(m + 0.06, 0.97, m - 0.02, 0.95, "leg")   # tap
    arect(m - MGW / 2 - MF, m + MGW / 2 + MF, MZ, MZ + MGH + 2 * MF, "board")       # frame
    arect(m - MGW / 2, m + MGW / 2, MZ + MF, MZ + MF + MGH, "mirror")                # glass
    atext(m, MZ + MF + MGH / 2, "Spiegel", "c")
    # dimensions
    def ahdim(z, ys, labels):
        aline(ys[0], z, ys[-1], z, "dim")
        for y in ys:
            aline(y - 0.03, z - 0.03, y + 0.03, z + 0.03, "dim")
        for (a, b), s in zip(zip(ys, ys[1:]), labels):
            atext((a + b) / 2, z + 0.03, s, "d")
    def azdim(y, zs, labels):
        aline(y, zs[0], y, zs[-1], "dim")
        for z in zs:
            aline(y - 0.03, z - 0.03, y + 0.03, z + 0.03, "dim")
        for (a, b), s in zip(zip(zs, zs[1:]), labels):
            atext(y - 0.03, (a + b) / 2, s, "d", rot=-90)
    ahdim(-0.30, [FWA, BB, BA, YF], [cm(BB, FWA), cm(BA, BB), cm(YF, BA)])
    mys = [m + MGW / 2 + MF, m + MGW / 2, m - MGW / 2, m - MGW / 2 - MF]
    ahdim(MZ + MGH + 2 * MF + 0.08, mys, [cm(0, MF), cm(0, MGW), cm(0, MF)])
    zs = [0, 0.85, TILE, MZ, MZ + MGH + 2 * MF, 2.40]
    zr = [round(z * 100) for z in zs]
    azdim(YN - 0.12, zs, ["%d" % (b - a) for a, b in zip(zr, zr[1:])])
    for z, s in ((0.85, "HWB 85"), (TILE - 0.06, f"Fliesen bis {cm(0, TILE)}"), (MZ + 0.02, f"UK Spiegel {cm(0, MZ)}"),
                 (MZ + MGH + 2 * MF, f"OK Spiegel {cm(0, MZ + MGH + 2 * MF)}")):
        atext(YN - 0.30, z - 0.02, s, "n", anchor="start")
    atext((YF + 8.506) / 2, -0.55, "Raumhöhe 240", "s2")

STYLE = """<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="6" height="6" fill="#ddd"/><line x1="0" y1="0" x2="0" y2="6" stroke="#999" stroke-width="1.5"/></pattern>
<pattern id="tiles" width="15" height="7.5" patternUnits="userSpaceOnUse"><rect width="15" height="7.5" fill="#cfe0ea"/>
<path d="M0,0 H15 M0,0 V7.5" stroke="#8aa8bb" stroke-width="0.6"/></pattern>
<marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#26a"/></marker></defs>
<style>
.wall{fill:url(#hatch);stroke:#555;stroke-width:1}.win{fill:#fff;stroke:#555;stroke-width:1}.thin{stroke:#555;stroke-width:1}
.new{fill:#d33;stroke:#900;stroke-width:1}.cut{fill:#fff;stroke:#d33;stroke-width:1.5;stroke-dasharray:5 3}
.fix{fill:#fff;stroke:#26a;stroke-width:1.5}.fixl{fill:none;stroke:#26a;stroke-width:1}
.axis{stroke:#26a;stroke-width:0.8;stroke-dasharray:10 3 2 3}
.cab{fill:#e8d2b0;stroke:#865;stroke-width:1}.board{fill:#c9a676;stroke:#865;stroke-width:1}
.shelf{fill:none;stroke:#865;stroke-width:1;stroke-dasharray:4 3}.hook{stroke:#333;stroke-width:2}
.tile{fill:url(#tiles);stroke:#8aa8bb;stroke-width:1}.winsec{fill:#fff;stroke:#555;stroke-width:1;stroke-dasharray:4 3}
.leg{stroke:#26a;stroke-width:2}
{V2CSS}.swing{fill:none;stroke:#777;stroke-width:1}.opt{fill:none;stroke:#aaa;stroke-width:1;stroke-dasharray:5 4}
.leaf{fill:#f6c;stroke:#900;stroke-width:1}.leafo{fill:#eee;stroke:#777;stroke-width:1}
.arrow{stroke:#26a;stroke-width:2;marker-end:url(#ah)}.dim{stroke:#333;stroke-width:1}
text{font-family:Helvetica,Arial,sans-serif}
.t{font-size:20px;font-weight:bold}.t2{font-size:15px;font-weight:bold;fill:#900}.s{font-size:15px}.s2{font-size:12px;fill:#555}
.n{font-size:12px;fill:#900}.q{font-size:14px;fill:#a60;font-style:italic}.c{font-size:13px;fill:#26a}
.d{font-size:12px;fill:#000;font-weight:bold}.h{font-size:18px;font-weight:bold}
</style>"""
STYLE = STYLE.replace("{V2CSS}", ".abbr{fill:none;stroke:#555;stroke-width:1;stroke-dasharray:3 3}"
                      ".mirror{fill:#bde;stroke:#26a;stroke-width:1}\n" if FL else "")
with open(OUT, "w") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n{STYLE}'
            f'<rect width="{W}" height="{H}" fill="#fff"/>\n' + "\n".join(o) + "\n</svg>\n")
print(OUT)
