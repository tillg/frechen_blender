"""Draft drawing: Bad Großeltern with the shower in the WC room, variants A/B for basin and the new west window
(house coordinates, 1 m = S px). Usage: python3 bad_grosseltern_svg.py bad_grosseltern_optionen.svg"""
import math, sys
S, X0, X1, Y0, Y1 = 120, -0.9, 5.6, 8.25, 12.95
PW, PH = (X1 - X0) * S, (Y1 - Y0) * S
EW, EH = 5.2 * S, 5.4 * S                       # elevation panel

def P(x, y): return ((x - X0) * S, (Y1 - y) * S)
def rect(x0, x1, y0, y1, fill="#bbb", stroke="#333", sw=1, dash=None, op=1, PP=None):
    PP = PP or P
    (a, b), (c, d) = PP(x0, y1), PP(x1, y0)
    a, c = min(a, c), max(a, c); b, d = min(b, d), max(b, d)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{a:.1f}" y="{b:.1f}" width="{c-a:.1f}" height="{d-b:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>'
def line(x0, y0, x1, y1, stroke="#333", sw=1.5, dash=None, PP=None):
    PP = PP or P
    (a, b), (c, d) = PP(x0, y0), PP(x1, y1)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{stroke}" stroke-width="{sw}"{da}/>'
def text(x, y, s, size=13, anchor="middle", color="#000", weight="normal", rot=0, PP=None):
    a, b = (PP or P)(x, y)
    tr = f' transform="rotate({rot} {a:.1f} {b:.1f})"' if rot else ""
    return f'<text x="{a:.1f}" y="{b:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}" font-family="Helvetica, Arial"{tr}>{s}</text>'
def poly(pts, fill="#fff", stroke="#333", sw=1.2):
    return f'<polygon points="{" ".join("%.1f,%.1f" % P(x, y) for x, y in pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def toilet(cx, wy):
    pts = [(cx + 0.18 * math.cos(math.pi * i / 12), wy + 0.19 + 0.33 * math.sin(math.pi * i / 12)) for i in range(13)]
    return rect(cx - 0.20, cx + 0.20, wy, wy + 0.19, "#fff") + poly([(cx + 0.18, wy + 0.19)] + pts + [(cx - 0.18, wy + 0.19)]) + text(cx, wy + 0.33, "WC", 11)
def dim(x0, y0, x1, y1, s, rot=0, PP=None):
    return line(x0, y0, x1, y1, "#c00", 1, PP=PP) + text((x0 + x1) / 2 + (0.06 if rot else 0), (y0 + y1) / 2 + (0 if rot else 0.05), s, 11, color="#c00", rot=rot, PP=PP)

WALL, GLASS, WIN = "#9a9a9a", "#2a7ab0", "#cfeefc"
BX0, BX1, BY0, BY1 = 0.31, 2.358, 8.656, 12.473        # the Bad's inner faces
NF = BY0 + 1.30                                        # new niche front wall: clear 130 (as the Duschbad)
NB = NF + 0.12
WP = BX0 + 1.024                                       # opening over the WC (as now)
XS, GL = 1.458, 0.75                                   # shower glass line, glass from the south wall (as the Duschbad)
WN = (10.25, 11.24)                                    # variant A: window 99 (as the OG west windows)
WB = (10.25, 12.23)                                    # variant B: window 198 (as the Yoga window above)

def base(win):
    o = [rect(0, BX0, 8.3, 12.887, WALL), rect(0, BX1 + 0.3, BY1, 12.887, WALL),           # west, north outer walls
         rect(BX0, BX1, 8.506, BY0, WALL),                                                  # south wall (back hall)
         rect(BX1, 2.657, 8.3, BY0, WALL), rect(BX1, 2.657, NB - 0.0, NB + 0.0, WALL)]
    o.append(rect(BX1, 2.657, BY0, NB, WALL))                                               # east wall along the new room
    o.append(text(3.35, 11.2, "Schlafzimmer", 13, color="#666")); o.append(text(3.35, 11.0, "Oma &amp; Opa", 13, color="#666"))
    o.append(text(1.33, 8.38, "hinterer Flur", 11, color="#666"))
    o.append(rect(0.03, 0.28, 9.12, 9.69, WIN, "#333", 1)); o.append(text(-0.3, 9.4, "WC-Fenster (bleibt)", 10, rot=-90))
    o.append(rect(1.109, 2.008, BY1 + 0.03, BY1 + 0.38, WIN, "#333", 1)); o.append(text(1.56, 12.68, "Nordfenster (bleibt)", 10))
    o.append(rect(0.0, BX0, win[0], win[1], WIN, GLASS, 2)); o.append(text(-0.32, (win[0] + win[1]) / 2, f"NEU: Fenster {round((win[1]-win[0])*100)}", 12, weight="bold", color=GLASS, rot=-90))
    o.append(text(-0.6, (win[0] + win[1]) / 2, "Brüstung 75, bis zur Decke", 10, color=GLASS, rot=-90))
    # old layout, dashed
    o.append(rect(BX0, BX1, BY0 + 1.08, BY0 + 1.20, "none", "#c00", 1, "5 4")); o.append(text(1.9, BY0 + 1.235, "alte Wand", 9, color="#c00"))
    o.append(rect(BX0, 1.26, 10.923, BY1, "none", "#c00", 1, "5 4")); o.append(text(1.0, 11.05, "alte Dusche (weg)", 10, color="#c00"))
    o.append(rect(1.26, 1.38, 10.923, 12.123, "none", "#c00", 1, "5 4"))
    # the new WC + shower room
    o.append(rect(BX0, BX1, BY0, NF, "#eef2f6", "none"))
    o.append(rect(WP, BX1, NF, NB, WALL)); o.append(line(BX0, NF + 0.06, WP, NF + 0.06, "#333", 1, "2 3"))   # front wall, lintel
    o.append(rect(XS, BX1, BY0, NF, "#dbe7f3", "none"))
    o.append(line(XS, BY0, XS, BY0 + GL, GLASS, 4)); o.append(text((XS + BX1) / 2, 9.45, "Dusche", 13, weight="bold"))
    o.append(text((XS + BX1) / 2, 9.28, "90 × 130", 11)); o.append(text(XS - 0.07, (BY0 + GL + NF) / 2, "Einstieg 55", 10, rot=-90))
    o.append(f'<circle cx="{P((XS+BX1)/2, 0)[0]:.1f}" cy="{P(0, 9.0)[1]:.1f}" r="7" fill="none" stroke="#333"/>')
    o.append(toilet(0.792, BY0))
    o.append(rect(WP - 0.03, BX1 - 0.005, NB + 0.01, NB + 0.05, "#c8a46e", "#333", 1)); o.append(text(1.85, NB + 0.13, "Schiebetür (offen)", 10))
    o.append(line(BX0 + 0.02, NB + 0.03, WP - 0.03, NB + 0.03, "#c8a46e", 2, "6 4")); o.append(text(0.82, NB + 0.13, "← schließt", 10))
    o.append(text(0.9, 9.45, "WC + Dusche", 13, weight="bold"))
    o.append(dim(BX0, BY0 + 1.12, XS, BY0 + 1.12, "WC-Teil 115"))
    o.append(dim(2.50, BY0, 2.50, NF, "")); o.append(text(2.58, (BY0 + NF) / 2, "130 (bisher 108)", 11, color="#c00", rot=-90))
    o.append(dim(BX0 + 0.05, NB, BX0 + 0.05, BY1, "")); o.append(text(BX0 + 0.12, 10.6, f"{round((BY1-NB)*100)}", 11, color="#c00", rot=-90))
    o.append(text(1.6, 11.0, "Bad", 15, weight="bold", color="#555")); o.append(text(1.6, 10.8, "(Eiche)", 10, color="#555"))
    o.append(text(2.51, 11.3, "offen zum", 9, color="#666", rot=-90)); o.append(text(2.62, 11.3, "Schlafzimmer", 9, color="#666", rot=-90))
    return o

def option_a():
    o = base(WN)
    o.append(rect(BX0, BX0 + 0.47, 11.42, 12.42, "#fff")); o.append(text(BX0 + 0.24, 11.92, "HWB doppelt 100", 10, rot=-90))
    o.append(line(BX0 + 0.015, 11.47, BX0 + 0.015, 12.37, GLASS, 3)); o.append(text(BX0 + 0.62, 11.92, "Spiegel", 10, color=GLASS, rot=-90))
    return o

def option_b():
    o = base(WB)
    o.append(rect(0.41, 1.01, BY1 - 0.45, BY1, "#fff")); o.append(text(0.71, 12.2, "HWB 60", 10))
    o.append(line(0.46, BY1 - 0.015, 0.96, BY1 - 0.015, GLASS, 3)); o.append(text(0.71, 11.88, "Spiegel", 10, color=GLASS))
    return o

def elevation():
    """West facade seen from the west (north left): EG + OG windows over the Bad."""
    Q = lambda y, z: ((12.95 - y) * S + 20, (5.15 - z) * S + 10)
    o = [rect(8.3, 12.887, 0, 4.9, "#efe6d6", "#333", 1, PP=Q)]
    o.append(line(8.3, 2.40, 12.887, 2.40, "#999", 1, "4 4", PP=Q)); o.append(text(8.35, 2.45, "Decke EG 2,40", 10, "start", "#777", PP=Q))
    o.append(line(8.3, 2.70, 12.887, 2.70, "#999", 1, "4 4", PP=Q)); o.append(text(8.35, 2.75, "OG", 10, "start", "#777", PP=Q))
    o.append(rect(8.96, 10.94, 3.45, 4.90, WIN, "#333", 1, PP=Q)); o.append(text(9.95, 4.1, "OG Yoga (deckenhoch)", 11, PP=Q))
    o.append(rect(9.12, 9.69, 1.57, 2.17, WIN, "#333", 1, PP=Q)); o.append(text(9.4, 1.4, "WC", 10, PP=Q))
    for (a, b), name, col in ((WN, "A", GLASS), (WB, "B", "#d07020")):
        o.append(rect(a, b, 0.75, 2.40, WIN if name == "A" else "none", col, 2, None if name == "A" else "6 4", PP=Q))
    o.append(text(10.75, 1.55, "A", 16, weight="bold", color=GLASS, PP=Q)); o.append(text(11.75, 1.55, "B", 16, weight="bold", color="#d07020", PP=Q))
    o.append(dim(10.10, 0, 10.10, 0.75, "", PP=Q)); o.append(text(10.02, 0.3, "75", 11, color="#c00", PP=Q))
    o.append(line(8.3, 0, 12.887, 0, "#333", 2, PP=Q)); o.append(text(12.85, -0.2, "Norden ←", 11, "start", PP=Q))
    o.append(text(8.5, -0.2, "→ Süden (Hintertür)", 11, "end", PP=Q))
    return o

panels = [("Variante A – Waschbecken an der Westwand (alte Duschecke), Fenster 99 breit", option_a(), PH),
          ("Variante B – Waschbecken an der Nordwand (alte Duschecke), Fenster 198 breit", option_b(), PH),
          ("Westansicht: neues Fenster Brüstung 75 bis zur Decke, wie die OG-Fenster dieser Seite", elevation(), EH)]
H = sum(h + 50 for _, _, h in panels)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{max(PW, EW):.0f}" height="{H:.0f}" viewBox="0 0 {max(PW, EW):.0f} {H:.0f}">',
       '<rect width="100%" height="100%" fill="#fff"/>']
y = 30
for title, items, h in panels:
    out.append(f'<g transform="translate(0 {y:.0f})">')
    out.append(f'<text x="10" y="-8" font-size="17" font-weight="bold" font-family="Helvetica, Arial">{title}</text>')
    out += items
    out.append(f'<text x="{max(PW, EW)-10:.0f}" y="16" font-size="12" text-anchor="end" font-family="Helvetica, Arial">{"N ↑   " if h == PH else ""}1 m = {S} px</text>')
    out.append('</g>')
    y += h + 50
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out))
