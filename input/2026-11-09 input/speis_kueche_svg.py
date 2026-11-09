"""Draws the Speis/Küche proposal (v1) as SVG, world coordinates from house_core (metres)."""
import os, sys
V = os.environ.get("KV", "b")        # a: whole kitchen 60 south (as asked), b: peninsula stays

OUT = sys.argv[1]
S, XA, YB = 120, 1.55, 7.15          # px per metre, world x at left, world y at top
ML, MT = 40, 70                      # margins
W, H = 1420, 1010


def X(x): return ML + (x - XA) * S
def Y(y): return MT + (YB - y) * S


o = []
def rect(x0, x1, y0, y1, cls, extra=""):
    o.append(f'<rect x="{X(x0):.1f}" y="{Y(y1):.1f}" width="{(x1-x0)*S:.1f}" height="{(y1-y0)*S:.1f}" class="{cls}" {extra}/>')
def line(x0, y0, x1, y1, cls):
    o.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" class="{cls}"/>')
def text(x, y, s, cls, anchor="middle", rot=None):
    t = f' transform="rotate({rot} {X(x):.1f} {Y(y):.1f})"' if rot else ""
    o.append(f'<text x="{X(x):.1f}" y="{Y(y):.1f}" class="{cls}" text-anchor="{anchor}"{t}>{s}</text>')
def arc(hx, hy, ax, ay, bx, by, cls, sweep):
    """Door swing: leaf hinge (hx,hy) -> open leaf end (ax,ay), arc to closed end (bx,by)."""
    r = ((ax-hx)**2 + (ay-hy)**2) ** 0.5 * S
    o.append(f'<path d="M{X(hx):.1f},{Y(hy):.1f} L{X(ax):.1f},{Y(ay):.1f} A{r:.1f},{r:.1f} 0 0 {sweep} {X(bx):.1f},{Y(by):.1f}" class="{cls}"/>')


# ------------------------------------------------------------------ Bestand (walls)
WALLS = [
    (2.358, 3.831, 0, 0.415), (4.730, 6.618, 0, 0.415), (7.917, 9.4, 0, 0.415),       # south facade
    (2.358, 2.772, 0.415, 5.849),                                                      # west wall
    (2.358, 6.14, 5.849, 6.349), (6.95, 9.4, 5.849, 6.349),                            # north (Flur), door from photo
    (8.557, 9.056, 0.415, 0.54), (8.557, 9.056, 2.938, 5.849),                         # Küche / Stube
    (5.240, 5.490, 5.249, 5.849),                                                      # Speis/Küche, north of new door
    (5.240, 5.490, 3.13, 4.33),                                                        # ... south of new door, ends at the cabinet
]
for w in WALLS:
    rect(*w, "wall")
rect(3.831, 4.730, 0, 0.415, "win"); rect(6.618, 7.917, 0, 0.415, "win")
line(3.831, 0.2075, 4.730, 0.2075, "thin"); line(6.618, 0.2075, 7.917, 0.2075, "thin")
text(4.28, -0.17, "Fenster", "s2"); text(7.27, -0.17, "Fenstertür", "s2")
# Küche–Flur door, measured from the photo (scale from the 15 cm tiles, ±5 cm):
# wall -> frame 54, frame 100 wide, clear opening 65 .. 146 (81), frame -> Kamin 120, Kamin 33
KI, DL, DR, ZL, ZR, KA = 5.49, 6.14, 6.95, 6.03, 7.03, 8.227
rect(ZL, DL, 5.825, 5.849, "zarge"); rect(DR, ZR, 5.825, 5.849, "zarge")
arc(DL, 5.849, DL, 5.849 - 0.81, DR, 5.849, "swing", 0)           # as built: hinged west, opens into the kitchen
rect(DL - 0.04, DL, 5.849 - 0.81, 5.849, "leaf")
# Besenschrank behind the open leaf (55 deep so the Speis sliding leaf passes in front of the wall)
rect(5.492, 6.00, 5.30, 5.847, "cab")
text(5.746, 5.62, "Besen-", "lbl"); text(5.746, 5.48, "schrank", "lbl"); text(5.746, 5.36, "51 × 55", "s2")
rect(7.045, 7.944, 5.849, 6.349, "gone_o")                        # where the plan has it
text(7.49, 6.07, "Tür laut Plan", "n")
text(9.0, 6.75, "Flur", "h")

# ------------------------------------------------------------------ entfällt
rect(2.772, 5.240, 3.13, 3.29, "gone")                     # wall Speis / Essen
text(3.30, 2.98, "Wand Speis/Essen (16) entfällt", "n", "start")
rect(5.240, 5.490, 3.002, 3.13, "gone")                    # 13 cm of the Speis/Küche wall

# ------------------------------------------------------------------ neu: Speis
x0, x1 = 2.774, 5.238
yN, y1, y2, y3, y4 = 5.847, 5.249, 4.33, 3.73, 3.13
rect(x0, x1, y1, yN, "shelf")                              # A: open shelf on the north wall
for k in range(1, 4):
    line(x0 + k * (x1 - x0) / 4, y1, x0 + k * (x1 - x0) / 4, yN, "div")
text((x0+x1)/2, 5.50, "A  Regal offen, 60 tief, bis Decke", "lbl")
text((x0+x1)/2, 4.80, "Gang 91,9 – Westende frei", "lblg")
rect(x0, x1, y3, y2, "shelf")                              # B: open shelf, open to the Gang
for k in range(1, 4):
    line(x0 + k * (x1 - x0) / 4, y3, x0 + k * (x1 - x0) / 4, y2, "div")
text((x0+x1)/2, 4.00, "B  Regal offen zum Gang, 60, bis Decke", "lbl")
rect(x0, x1, y4, y3, "cab")                                # C: cabinet with doors towards the table
line(x0, y3, x1, y3, "back")
n = 4
for k in range(n):
    a, b = x0 + k * (x1 - x0) / n, x0 + (k + 1) * (x1 - x0) / n
    line(a + 0.005, y4 - 0.012, b - 0.005, y4 - 0.012, "front")
    if k:
        line(a, y4, a, y3, "div")
text((x0+x1)/2, 3.40, "C  Schrank, Türen → Esstisch, 60, bis Decke", "lbl")
# open front edges (dashed) of the shelves
line(x0, y1, x1, y1, "openf"); line(x0, y2, x1, y2, "openf")
text(3.25, 4.55, "Speis", "h")
rect(5.240, 5.490, 3.631, 4.33, "gone_o")                  # old door opening, now closed
text(5.365, 3.85, "alte Tür → zu", "n", rot=-90)

# new Speis door in the Gang: 90 opening, leaf opens into the Küche (proposal)
# Speis: sliding leaf on the kitchen face, slides left as seen from the kitchen (= south) in front of the wall
line(5.545, 3.26, 5.545, 5.285, "rail")
rect(5.495, 5.53, 4.28, 5.28, "slide")                     # closed (opening 4.33 .. 5.249)
rect(5.495, 5.53, 3.28, 4.28, "slideo")                    # open
line(5.66, 5.05, 5.66, 3.75, "arrow")
text(5.74, 4.62, "Schiebetür 100, Küchenseite", "q2", "start")
text(5.74, 4.47, "schiebt nach links (von der", "q2", "start")
text(5.74, 4.32, "Küche aus) vor die Wand", "q2", "start")

# ------------------------------------------------------------------ Bestand: Küche, Esstisch
# sink run right of the kitchen door (water connection there today), up to the Herd
# Herd and east run 60 south; the sink run reaches into the NE corner (the flue box hangs above ~1.8 m)
dy = -0.60 if V == "a" else 0.0                              # peninsula moves only in variant a
for b in ((6.57, 8.555, 3.05, 3.64), (7.977, 8.555, 3.64, 4.90), (7.977, 8.555, 4.94, 5.74)):
    if V == "b" and b[2] == 3.05:
        continue
    rect(*b, "kitold")                                        # where it stands in the plan
rect(7.05, 8.555, 5.269, 5.847, "kitn"); rect(7.21, 7.71, 5.33, 5.76, "kitl")
rect(6.57, 8.555, 3.05 + dy, 3.64 + dy, "kitm")              # peninsula
rect(7.977, 8.555, 3.64 + dy, 4.26, "kitm")                  # east run
rect(7.977, 8.555, 4.30, 5.10, "kitm"); text(8.27, 4.68, "Herd", "s2")
for cx, cy, rr in ((7.36, 3.24, 0.08), (7.36, 3.46, 0.06), (7.76, 3.24, 0.06), (7.76, 3.46, 0.09)):
    o.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy + dy):.1f}" r="{rr*S:.1f}" class="kitl"/>')
text(7.45, 4.25, "Küche", "h")
rect(KA, 8.557, 5.55, 5.849, "kaminup"); text(8.39, 5.66, "Abzug", "s2")   # flue box only from ~1.8 m up
rect(4.262, 7.848, 1.18, 1.91, "tab"); line(6.05, 1.18, 6.05, 1.91, "thin")
for x in (4.58, 5.15, 5.73, 6.39, 6.95, 7.53):
    rect(x - 0.21, x + 0.21, 2.12 - 0.21, 2.12 + 0.21, "clash" if V == "a" and x > 6.3 else "chair")
    rect(x - 0.21, x + 0.21, 0.97 - 0.21, 0.97 + 0.21, "chair")
rect(4.05 - 0.21, 4.05 + 0.21, 1.545 - 0.21, 1.545 + 0.21, "chair")
rect(8.06 - 0.21, 8.06 + 0.21, 1.545 - 0.21, 1.545 + 0.21, "chair")
text(6.05, 1.47, "Esstisch", "s")
# cabinet door swing (one, to show the clearance to the chairs)
arc(x0 + 0.616, y4, x0 + 0.616, y4 - 0.616, x0, y4, "swing", 0)

# ------------------------------------------------------------------ dimensions
def vdim(x, ys, labels):
    line(x, ys[0], x, ys[-1], "dim")
    for y in ys:
        line(x - 0.06, y - 0.06, x + 0.06, y + 0.06, "dim")
    for (a, b), s in zip(zip(ys[:-1], ys[1:]), labels):
        text(x - 0.08, (a + b) / 2, s, "d", rot=-90)
def hdim(y, xs, labels):
    line(xs[0], y, xs[-1], y, "dim")
    for x in xs:
        line(x - 0.06, y - 0.06, x + 0.06, y + 0.06, "dim")
    for (a, b), s in zip(zip(xs[:-1], xs[1:]), labels):
        text((a + b) / 2, y + 0.06, s, "d")

vdim(2.05, [5.849, 5.249, 4.33, 3.73, 3.13], ["60", "91,9", "60", "60"])
vdim(1.80, [5.849, 3.13], ["271,9"])
hdim(6.53, [2.772, 5.240], ["246,8 lichte Breite Speis"])
hdim(6.53, [KI, ZL, ZR, KA, 8.557], ["54", "100 Zarge", "120", "33"])
hdim(6.78, [KI, DL, DR], ["65", "81 licht"])
hdim(7.03, [KI, 8.557], ["306,7 Küche innen"])
vdim(4.95, [3.13, 2.33], ["80 bis Stuhl"])
if V == "a":
    vdim(6.70, [3.03 + dy, 1.91], ["52"])
    text(6.62, 2.49, "nur 10 hinter den Stuhllehnen!", "n", "start")
vdim(7.86, [4.30, 5.10], ["Herd 80"]); vdim(7.86, [3.66 + dy, 4.26], ["%d" % round((4.26 - 3.66 - dy) * 100)])
hdim(5.19, [7.05, 8.555], ["≈ 150 Spülzeile bis ins Eck"])

# ------------------------------------------------------------------ legend / notes
LX = 1085
VT = {"a": "v6a – Küche komplett 60 nach Süden", "b": "v6 – vereinbart: Halbinsel bleibt, Ostzeile 60"}[V]
notes = [
    ("t", "Speis / Küche – " + VT.split(" – ")[0]),
    ("s2", VT.split(" – ")[1]),
    ("s2", "Maßstab ≈ 1:83 · Maße in cm · Norden oben"),
    ("s2", "Küchentür aus Foto geschätzt, ±5 cm"),
    ("", ""),
    ("h3", "Speis, von der Flurwand nach Süden:"),
    ("s", "A  Regal offen, 60 tief, bis zur Decke"),
    ("s", "    Gang 91,9, Westende frei"),
    ("s", "B  Regal offen zum Gang, 60, bis zur Decke"),
    ("s", "C  Schrank, Türen zum Esstisch, 60, bis Decke,"),
    ("s", "    Rücken an Rücken mit B, statt Wand Speis/Essen"),
    ("s", "Wand Speis/Küche endet bündig mit C (y 3,13)"),
    ("", ""),
    ("h3", "Küche:"),
    ("s", "Küchentür wie Bestand, öffnet in die Küche"),
    ("s", "Besenschrank hinter der offenen Tür, 51 × 55"),
    ("s", "Speis: Schiebetür 100, Küchenseite, nach links"),
    ("s", "Herd + Ostzeile 60 nach Süden (grau gepunktet:"),
    ("s", "    heutige Lage laut Plan)"),
    ("s", "Spülzeile rechts der Tür bis ins Eck ≈ 150"),
    ("s", "    (Abzug erst ab ≈ 1,8 m, gestrichelt)"),
    ("s", "Ofenrohr vom Herd zum Abzug geführt"),
] + ([
    ("s", "Halbinsel ebenfalls 60 nach Süden"),
    ("", ""),
    ("h3", "Zu klären:"),
    ("q", "1  Halbinsel nur noch 10 hinter den Stuhl-"),
    ("q", "    lehnen, 52 bis Tisch: so geht es nicht."),
    ("q", "    → Variante b (Halbinsel bleibt)?"),
] if V == "a" else [
    ("s", "Halbinsel bleibt; Ostzeile 60, Herd daneben"),
]) 
y = 60
for cls, s in notes:
    if s:
        o.append(f'<text x="{LX}" y="{y}" class="{cls}">{s}</text>')
    y += 26 if cls in ("t", "h3") else 21
y += 10
for cls, s in (("wall", "Wand Bestand"), ("gone", "entfällt / laut Plan, passt nicht"), ("shelf", "Regal offen (neu)"),
               ("cab", "Schrank mit Türen (neu)"), ("kitn", "Spülzeile (neu)"), ("slide", "Schiebetür (neu)"), ("kitm", "Küche verschoben"), ("kitold", "Küche laut Plan")):
    o.append(f'<rect x="{LX}" y="{y-13}" width="34" height="16" class="{cls}"/>')
    o.append(f'<text x="{LX+44}" y="{y}" class="s">{s}</text>')
    y += 24

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="6" height="6" fill="#ddd"/><line x1="0" y1="0" x2="0" y2="6" stroke="#999" stroke-width="1.5"/></pattern>
<marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#26a"/></marker></defs>
<style>
.wall{{fill:url(#hatch);stroke:#555;stroke-width:1}}.win{{fill:#fff;stroke:#555;stroke-width:1}}.thin{{stroke:#777;stroke-width:1}}
.gone{{fill:#fde6e6;stroke:#c33;stroke-width:1.2;stroke-dasharray:5 3}}.gone_o{{fill:none;stroke:#c33;stroke-width:1.5;stroke-dasharray:4 3}}.gone_l{{fill:none;stroke:#c33;stroke-width:1;stroke-dasharray:5 3}}
.shelf{{fill:#f4e7d0;stroke:#865;stroke-width:1.5}}.cab{{fill:#e2c79c;stroke:#865;stroke-width:1.5}}
.div{{stroke:#a87;stroke-width:1}}.back{{stroke:#654;stroke-width:2.5}}.front{{stroke:#654;stroke-width:3}}
.openf{{stroke:#865;stroke-width:1.5;stroke-dasharray:6 4}}
.zarge{{fill:#a0612a;stroke:#6b3d14;stroke-width:1}}.swingo{{fill:none;stroke:#aaa;stroke-width:1;stroke-dasharray:3 3}}.kaminup{{fill:none;stroke:#666;stroke-width:1.2;stroke-dasharray:4 3}}.kamin{{fill:#ccc;stroke:#666;stroke-width:1}}.kitx{{fill:none;stroke:#c33;stroke-width:1.2;stroke-dasharray:5 3}}.leaf{{fill:#c98a4b;stroke:#6b3d14;stroke-width:1}}.kitn{{fill:#dfe9f2;stroke:#26a;stroke-width:1.5}}.rail{{stroke:#555;stroke-width:1.5}}.slide{{fill:#26a;stroke:#134;stroke-width:1}}.slideo{{fill:none;stroke:#26a;stroke-width:1.2;stroke-dasharray:4 3}}.arrow{{stroke:#26a;stroke-width:1.5;marker-end:url(#ah)}}.q2{{font-size:12px;fill:#26a}}.kitm{{fill:#e4e4e4;stroke:#555;stroke-width:1.2}}.kitold{{fill:none;stroke:#999;stroke-width:1;stroke-dasharray:2 3}}.clash{{fill:#fde6e6;stroke:#c33;stroke-width:1.5}}.kit{{fill:#eee;stroke:#888;stroke-width:1}}.kitl{{fill:none;stroke:#888;stroke-width:1}}
.tab{{fill:#f6f2ea;stroke:#888;stroke-width:1}}.chair{{fill:#fff;stroke:#aaa;stroke-width:1}}
.swing{{fill:none;stroke:#888;stroke-width:1}}.swingn{{fill:none;stroke:#26a;stroke-width:1.5;stroke-dasharray:6 3}}
.dim{{stroke:#333;stroke-width:1}}
text{{font-family:Helvetica,Arial,sans-serif}}
.t{{font-size:20px;font-weight:bold}}.h3{{font-size:16px;font-weight:bold}}.s{{font-size:14px}}.s2{{font-size:12px;fill:#555}}
.n{{font-size:12px;fill:#c33}}.q{{font-size:14px;fill:#26a}}.d{{font-size:12px;font-weight:bold}}
.h{{font-size:18px;font-weight:bold;fill:#444}}.lbl{{font-size:13px;fill:#432}}.lblg{{font-size:14px;fill:#26a;font-weight:bold}}
</style><rect width="{W}" height="{H}" fill="#fff"/>
''' + "\n".join(o) + "\n</svg>\n"
open(OUT, "w").write(svg)
