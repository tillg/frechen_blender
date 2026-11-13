"""Draws the Schrankbett (v1, issue #7) as SVG: Grundriss, Ansicht Süd and Schnitt of the 2 x 2 m wall bed
in the Yoga room (OG). Every number comes from code/schrankbett.py (local coordinates: origin at the room's
inner SW corner, x east, y north, z up from the floor slab); nothing is repeated here.
Usage: python3 schrankbett_svg.py schrankbett_v1.svg"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "code"))
import schrankbett as s
from schrankbett import W, D, YC, YB, BT, T, PLINTH, NW, SW, BW, L, A, DU, ZU, YP, ZP, YH, BLENDE, TOP, CEIL, MAT, FL, cm

OUT = sys.argv[1]
RX, RY = 5.74, 3.625                          # the room (local), from the task
WT, WS = 0.31, 0.29                           # west / south wall thickness
WIN = (0.10, 1.09, 0.75)                      # west window: y0, y1, sill
DOOR = (s.DOOR[0] - s.SCHRANKBETT_AT[0], s.DOOR[1] - s.SCHRANKBETT_AT[0])   # Yoga door, local x
DH = s.hc.DOOR_H
XA, XB = SW + 0.01, SW + 0.01 + BW            # the bed's sides
YF = YH + L                                   # foot end, down
ZTOP = ZP - A + L                             # bed folded up: top
R = math.hypot(L - A, 0.16 - DU)              # swing radius of the far top corner of the side rails
A0 = math.degrees(math.atan2(0.16 - DU, L - A))
assert ZP + R < BLENDE and ZTOP < BLENDE and TOP < CEIL
o = []


class V:
    """One view: u to the right, v up, sc px per metre, flip mirrors u (looking south: west is right)."""
    def __init__(s, ox, oy, sc, flip=False): s.ox, s.oy, s.sc, s.flip = ox, oy, sc, flip
    def X(s, u): return s.ox + (-u if s.flip else u) * s.sc
    def Y(s, v): return s.oy - v * s.sc
    def rect(s, u0, u1, v0, v1, cls):
        (a, b), (c, d) = sorted((s.X(u0), s.X(u1))), sorted((s.Y(v0), s.Y(v1)))
        o.append(f'<rect x="{a:.1f}" y="{c:.1f}" width="{b-a:.1f}" height="{d-c:.1f}" class="{cls}"/>')
    def line(s, u0, v0, u1, v1, cls):
        o.append(f'<line x1="{s.X(u0):.1f}" y1="{s.Y(v0):.1f}" x2="{s.X(u1):.1f}" y2="{s.Y(v1):.1f}" class="{cls}"/>')
    def poly(s, pts, cls):
        o.append('<polygon points="' + " ".join(f"{s.X(u):.1f},{s.Y(v):.1f}" for u, v in pts) + f'" class="{cls}"/>')
    def arc(s, c, r, a0, a1, cls, n=40):
        pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        o.append('<polyline points="' + " ".join(f"{s.X(u):.1f},{s.Y(v):.1f}" for u, v in pts) + f'" class="{cls}"/>')
    def text(s, u, v, t, cls="d", a="middle", rot=None, dx=0, dy=0):
        x, y = s.X(u) + dx, s.Y(v) + dy
        r = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
        o.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{a}"{r}>{t}</text>')
    def tick(s, u, v):
        o.append(f'<line x1="{s.X(u)-4:.1f}" y1="{s.Y(v)+4:.1f}" x2="{s.X(u)+4:.1f}" y2="{s.Y(v)-4:.1f}" class="dim"/>')
    def hdim(s, v, us, labels, below=False):
        s.line(us[0], v, us[-1], v, "dim")
        for u in us: s.tick(u, v)
        for (a, b), t in zip(zip(us, us[1:]), labels): s.text((a + b) / 2, v, t, "d", dy=15 if below else -5)
    def vdim(s, u, vs, labels):
        s.line(u, vs[0], u, vs[-1], "dim")
        for v in vs: s.tick(u, v)
        for (a, b), t in zip(zip(vs, vs[1:]), labels): s.text(u, (a + b) / 2, t, "d", rot=-90, dx=-5)


# ------------------------------------------------------------------ Grundriss (north up)
P = V(172.5, 665, 150)
o.append('<text x="30" y="96" class="t">Grundriss OG, Yoga (Schnitt in 1 m Höhe)</text>')
P.rect(-WT, 0, 0, WIN[0], "wall"); P.rect(-WT, 0, WIN[1], RY, "wall"); P.rect(-WT, 0, WIN[0], WIN[1], "win")
P.line(-WT / 2, WIN[0], -WT / 2, WIN[1], "thin")
P.text(-WT / 2, (WIN[0] + WIN[1]) / 2, f"Fenster BRH {cm(0, WIN[2])}", "s2", rot=-90, dx=-4)
P.rect(-WT, DOOR[0], -WS, 0, "wall"); P.rect(DOOR[1], RX, -WS, 0, "wall")
P.line(RX, 0, RX, RY, "abbr"); P.line(0, RY, RX, RY, "abbr")                       # the room beyond the drawing's interest
P.arc((DOOR[1], 0.04), DOOR[1] - DOOR[0], 180, 0, "swing")                          # Yoga door: hinged east, 180 deg open
P.rect(DOOR[1], DOOR[1] + (DOOR[1] - DOOR[0]), 0, 0.04, "leaf")
P.text(DOOR[1], 0.55, "Tür Yoga, öffnet", "n"); P.text(DOOR[1], 0.40, "180° an die Wand", "n")
P.text(4.4, 2.6, "Yoga (OG)", "h")
for a, b in ((0, SW), (W - SW, W)): P.rect(a, b, YB, D, "cab"); P.rect(a + T, b - T, YB + BT, YC, "open")   # side cabinets, hollow
P.rect(SW, W - SW, YB, YB + BT, "cabc")
P.rect(XA, XB, D - 0.16, D, "up"); P.rect(XA + 0.02, XB - 0.02, D - MAT - 0.08, D, "up")  # bed folded up, inside the niche
P.rect(XA, XB, YH, YF, "bed"); P.rect(XA + 0.02, XB - 0.02, YH + 0.02, YF - 0.02, "mat")   # bed folded down
P.line((XA + XB) / 2, YH + 0.02, (XA + XB) / 2, YF - 0.02, "thin")
for k in range(2):
    xm = XA + 0.02 + (k + 0.5)
    P.rect(xm - 0.25, xm + 0.25, YH + 0.06, YH + 0.41, "pil")
P.rect(XA + 0.03, XB - 0.03, YH + 0.45, YF - 0.03, "duv")
P.text((XA + XB) / 2, 1.30, "Liegefläche 200 × 200", "h", dy=0)
P.text((XA + XB) / 2, 1.15, f"Bett ausgeklappt, {cm(0, BW)} breit, {cm(0, L)} lang", "s2")
P.text(1.4, 0.05, "Bett hochgeklappt (gestrichelt)", "nb")
P.line(SW, YP, W - SW, YP, "axis")
P.text(W - SW - 0.04, YP + 0.03, "Drehachse", "axt", a="end", dy=-3)
# dimensions: along the south wall, west wall, on the bed
P.hdim(-0.55, [0, SW, W - SW, W], [f"Schrank {cm(0, SW)}", f"Bett {cm(0, NW)}", f"Schrank {cm(0, SW)}"], below=True)
P.hdim(-0.80, [0, W], [f"Schrankwand {cm(0, W)}"], below=True)
for v in (0, SW, W - SW, W): P.line(v, -WS, v, -0.60 if v in (0, W) else -0.52, "ext")
P.vdim(-0.55, [0, D], [f"Tiefe {cm(0, D)}"]); P.line(-0.60, D, 0, D, "ext")
P.vdim(-0.80, [0, YF], [f"ausgeklappt {cm(0, YF)} ab Wand"]); P.line(-0.85, YF, XA, YF, "ext")
P.hdim(YF + 0.14, [XA + 0.02, XB - 0.02], [cm(0, 2.0)]); P.vdim(XB - 0.07, [YH + 0.02, YF - 0.02], [cm(0, 2.0)])
P.line(XA + 0.02, YF - 0.02, XA + 0.02, YF + 0.20, "ext"); P.line(XB - 0.02, YF - 0.02, XB - 0.02, YF + 0.20, "ext")

# ------------------------------------------------------------------ Ansicht Süd (looking south, west on the right)
E = V(1640, 520, 130, flip=True)
o.append(f'<text x="1075" y="{E.Y(CEIL) - 100:.1f}" class="t">Ansicht Süd (Blick aus dem Raum, Bett hoch)</text>')
XR = 4.0
E.rect(-WT, 0, -0.15, CEIL + 0.15, "wall"); E.rect(-WT, XR, -0.15, 0, "wall"); E.rect(-WT, XR, CEIL, CEIL + 0.15, "wall")
E.rect(0, XR, FL, CEIL, "wallf"); E.rect(0, XR, 0, FL, "win")
E.rect(DOOR[0], DOOR[1], 0, DH, "leaf"); E.text((DOOR[0] + DOOR[1]) / 2, 1.0, "Tür Yoga", "w", rot=-90)
E.rect(SW, W - SW, FL, BLENDE, "open")                                              # niche, dark behind the bed
E.rect(XA, XB, ZP - A, ZTOP, "bedu")                                                # the bed's underside, folded up
E.text((XA + XB) / 2, 1.0, "Bett hochgeklappt: Unterseite Fichte", "w", rot=-90)
for xs in (XA + 0.10, XB - 0.16): E.rect(xs, xs + 0.06, ZTOP - 0.06, ZTOP - 0.03, "feet")   # feet at the foot end
for a, b, h in ((0.0, SW, SW - 0.05), (W - SW, W, W - SW + 0.05)):
    E.rect(a + T, b - T, FL, PLINTH, "open")
    E.rect(a + 0.002, b - 0.002, PLINTH + 0.003, TOP - 0.003, "cab")
    E.rect(a + 0.03, b - 0.03, PLINTH + 0.03, TOP - 0.03, "panel")
    E.rect(h - 0.008, h + 0.008, 0.95, 1.25, "metal")
E.rect(SW, W - SW, BLENDE, TOP, "cab"); E.text(W / 2, BLENDE + 0.04, "Blende", "w", dy=4)
E.line(-WT, CEIL, XR, CEIL, "ceil"); E.text(3.4, CEIL + 0.07, "Decke 2,20", "s2")
E.hdim(-0.38, [0, SW, W - SW, W], [cm(0, SW), cm(0, NW), cm(0, SW)], below=True)
E.hdim(CEIL + 0.34, [0, W], [f"Schrankwand {cm(0, W)}"])
E.hdim(-0.60, [DOOR[0], DOOR[1]], [f"Tür {cm(*DOOR)}"], below=True)
E.vdim(-0.45, [0, CEIL], [f"Raumhöhe {cm(0, CEIL)}"]); E.vdim(-0.72, [0, ZTOP], [f"Bett hoch, OK {cm(0, ZTOP)}"])
E.vdim(-0.98, [BLENDE, TOP], [f"Blende ab {cm(0, BLENDE)}"])

# ------------------------------------------------------------------ Schnitt (through the niche, looking west: y to the right)
S = V(1140, 1130, 170)
o.append('<text x="1075" y="695" class="t">Schnitt durch die Nische (Blick nach Westen)</text>')
YE = 2.60
S.rect(-WS, 0, -0.15, CEIL + 0.15, "wall"); S.rect(-WS, YE, -0.15, 0, "wall"); S.rect(-WS, YE, CEIL, CEIL + 0.15, "wall")
S.rect(0, YE, 0, FL, "win"); S.text(YE - 0.05, CEIL + 0.08, "Decke", "s2", a="end"); S.text(-WS / 2, 1.0, "Südwand", "s2", rot=-90, dx=4)
S.rect(YB + BT, D, FL, TOP, "beyond")                                              # left side cabinet, seen beyond
S.rect(D, D + 0.025, 0.95, 1.25, "metal"); S.rect(YP - 0.04, YP + 0.04, ZP - 0.04, ZP + 0.04, "metal")
S.rect(YB, YB + BT, FL, TOP, "cabc"); S.rect(YB + BT, YC, TOP - T, TOP, "cabc"); S.rect(YC, D, BLENDE, TOP, "cabc")
S.text(D + 0.04, TOP - 0.02, "Blende", "n", a="start")


def Tb(l, w, up):                       # bed coordinates (from the head end, above the underside) -> (y, z)
    return (D - w, ZP - A + l) if up else (YH + l, ZU + w)
def part(l0, l1, w0, w1, cls, up=False):
    S.poly([Tb(l0, w0, up), Tb(l1, w0, up), Tb(l1, w1, up), Tb(l0, w1, up)], cls)
for l0, l1, w0, w1, cls in ((0, L, 0, 0.02, "cabc"), (0, 0.02, 0.02, 0.16, "cabc"), (L - 0.02, L, 0.02, 0.16, "cabc"),
                            (0.02, L - 0.02, 0.03, 0.05, "cabc"), (0.02, L - 0.02, 0.05, MAT, "mat"), (0.06, 0.41, MAT, MAT + 0.08, "pil"),
                            (0.45, L - 0.03, MAT, MAT + 0.04, "duv"), (L - 0.06, L - 0.03, FL - ZU, 0, "cabc")):
    part(l0, l1, w0, w1, cls)
part(0, L, 0, 0.16, "up", True); part(0.02, L - 0.02, 0.16, MAT + 0.08, "up", True); part(L - 0.06, L - 0.03, FL - ZU, 0, "up", True)
S.arc((YP, ZP), R, A0, A0 + 90, "arc")
S.text(0.95, BLENDE + 0.025, f"Schwenk max. {ZP + R:.2f}".replace(".", ",") + f" (Luft {100 * (BLENDE - ZP - R):.1f} zur Blende)".replace(".", ","), "nb", a="start")
S.rect(YP - 0.02, YP + 0.02, ZP - 0.02, ZP + 0.02, "pivot")
S.text(0.56, 0.06, "Drehachse", "axt", a="start"); S.line(0.55, 0.07, YP + 0.03, ZP - 0.03, "thin")
S.text(YF, ZU + MAT + 0.14, "Bett ausgeklappt", "s2", a="middle")
S.vdim(YF + 0.28, [0, ZU + MAT], [""]); S.text(YF + 0.28, ZU + MAT / 2, f"Liegehöhe {cm(0, ZU + MAT)}", "d", rot=-90, dx=16, dy=-20); S.vdim(-0.50, [0, CEIL], [f"Raumhöhe {cm(0, CEIL)}"])
S.hdim(-0.30, [0, YH, YP, D], [cm(0, YH), cm(YH, YP), cm(YP, D)], below=True)
S.hdim(-0.50, [0, D], [f"Tiefe {cm(0, D)}"], below=True); S.hdim(-0.70, [0, YF], [f"ausgeklappt {cm(0, YF)} ab Wand"], below=True)

# ------------------------------------------------------------------ notes, legend
LY = 930
notes = [("t", "Schrankbett v1 · 2 × 2 m Klappbett im Yoga-Zimmer (OG), Schrankwand an der Südwand"),
         ("s", f"Von der Westwand bis zur Yoga-Tür {cm(0, W)} breit: Schrank {cm(0, SW)}, Nische {cm(0, NW)} (Bett {cm(0, BW)} + je 1), Schrank {cm(0, SW)}; Tiefe {cm(0, D)} bis Türfront."),
         ("s", f"Bett {cm(0, BW)} × {cm(0, L)}, Liegefläche 200 × 200, Liegehöhe {cm(0, ZU + MAT)}; ausgeklappt {cm(0, YF)} ab Wand (Kopfende {cm(0, YH)})."),
         ("s", f"Drehachse {cm(0, A)} vom Kopfende, {cm(0, DU)} über der Unterseite ({cm(0, ZP)} über Boden); hochgeklappt bündig mit den Türfronten, OK {cm(0, ZTOP)}."),
         ("s", f"Höchster Punkt des Schwenks {ZP + R:.2f} (Seitenschiene, Fußende) unter der Blende ab {BLENDE:.2f}; Blende bis {TOP:.3f}, Decke {CEIL:.2f}".replace(".", ",") + "."),
         ("q", "Der linke Schrank verdeckt einen Teil der Fensterlaibung (abgesprochen). Fichte wie die übrigen OG-Möbel (angenommen)."),
         ("q", "Nicht maßstäblich; Maße in cm. Füße stehen hochgeklappt 15 über die Türfront (real: an die Unterseite geklappt).")]
for cls, t in notes:
    o.append(f'<text x="30" y="{LY}" class="{cls}">{t}</text>'); LY += 28 if cls == "t" else 22
for i, (cls, t) in enumerate((("wall", "Wand (Schnitt)"), ("cab", "Schrank, Türfront"), ("bed", "Bett ausgeklappt"), ("up", "Bett hochgeklappt"),
                              ("leaf", "Türblatt"), ("arc", "Schwenkkreis"))):
    lx, ly = 30 + (i % 3) * 230, LY + 20 + (i // 3) * 26
    o.append(f'<rect x="{lx}" y="{ly-13}" width="34" height="16" class="{cls}"/><text x="{lx+42}" y="{ly}" class="s">{t}</text>')
o.append('<text x="30" y="40" class="t">Schrankbett Yoga (Vorschlag v1, 2026-11-13)</text>')
o.append('<text x="30" y="62" class="s2">Grundriss, Ansicht Süd und Schnitt; alle Maße aus code/schrankbett.py (Ursprung: innere SW-Ecke des Yoga-Zimmers)</text>')
o.append(f'<path d="M{P.X(5.2):.1f},{P.Y(RY)+34:.1f} l-9,24 l9,-7 l9,7 z" fill="#333"/><text x="{P.X(5.2):.1f}" y="{P.Y(RY)+30:.1f}" class="s" text-anchor="middle">N</text>')

STYLE = """<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="6" height="6" fill="#ddd"/><line x1="0" y1="0" x2="0" y2="6" stroke="#999" stroke-width="1.5"/></pattern></defs>
<style>
.wall{fill:url(#hatch);stroke:#555;stroke-width:1}.win{fill:#fff;stroke:#555;stroke-width:1}.wallf{fill:#f4f1ea;stroke:#555;stroke-width:1}
.thin{stroke:#555;stroke-width:1}.ext{stroke:#999;stroke-width:0.6}.ceil{stroke:#555;stroke-width:1.5}
.abbr{fill:none;stroke:#555;stroke-width:1;stroke-dasharray:3 3}.axis{stroke:#26a;stroke-width:0.8;stroke-dasharray:10 3 2 3}
.cab{fill:#8a5a3c;stroke:#3a2214;stroke-width:1}.cabc{fill:#6b4029;stroke:#2a170c;stroke-width:1}.open{fill:#4a2c1c;stroke:#3a2214;stroke-width:1}
.panel{fill:none;stroke:#3a2214;stroke-width:1}.metal{fill:#333;stroke:#000;stroke-width:0.5}
.bed{fill:#d9b98a;stroke:#6b4029;stroke-width:1}.bedu{fill:#c79a62;stroke:#3a2214;stroke-width:1}.feet{fill:#6b4029;stroke:#2a170c;stroke-width:1}
.mat{fill:#f1ebdc;stroke:#888;stroke-width:1}.pil{fill:#fff;stroke:#888;stroke-width:1}.duv{fill:#9fb7c4;fill-opacity:0.6;stroke:#567;stroke-width:1}
.up{fill:none;stroke:#26a;stroke-width:1.2;stroke-dasharray:6 4}.beyond{fill:#efe4d8;stroke:#865;stroke-width:1;stroke-dasharray:4 3}
.pivot{fill:#d33;stroke:#900;stroke-width:1}.arc{fill:none;stroke:#d33;stroke-width:1.5;stroke-dasharray:2 3}
.swing{fill:none;stroke:#777;stroke-width:1}.leaf{fill:#f6c;stroke:#900;stroke-width:1}
.dim{stroke:#333;stroke-width:1}
text{font-family:Helvetica,Arial,sans-serif}
.t{font-size:20px;font-weight:bold}.s{font-size:15px}.s2{font-size:12px;fill:#555}.n{font-size:12px;fill:#900}
.nb{font-size:12px;fill:#26a;font-weight:bold;paint-order:stroke;stroke:#fff;stroke-width:3px}
.axt{font-size:12px;fill:#900;paint-order:stroke;stroke:#fff;stroke-width:3px}
.q{font-size:14px;fill:#a60;font-style:italic}.d{font-size:12px;fill:#000;font-weight:bold}
.w{font-size:12px;fill:#fff;font-weight:bold}.h{font-size:18px;font-weight:bold;paint-order:stroke;stroke:#fff;stroke-width:3px}
</style>"""
Wd, Hd = 1800, 1300
with open(OUT, "w") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{Hd}" viewBox="0 0 {Wd} {Hd}">\n{STYLE}'
            f'<rect width="{Wd}" height="{Hd}" fill="#fff"/>\n' + "\n".join(o) + "\n</svg>\n")
print(OUT)
