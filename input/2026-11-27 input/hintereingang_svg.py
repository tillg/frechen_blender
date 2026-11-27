"""Draft drawing for issue #61: Hintereingang variants A/B and Garderobe G1/G2 (house coordinates, 1 m = S px).
Usage: python3 hintereingang_svg.py hintereingang_optionen.svg. The user chose B and G1 (2026-11-27)."""
import math, sys
S, X0, X1, Y0, Y1 = 110, -0.9, 6.7, 4.9, 9.15
PW, PH = (X1 - X0) * S, (Y1 - Y0) * S

def P(x, y): return ((x - X0) * S, (Y1 - y) * S)
def rect(x0, x1, y0, y1, fill="#bbb", stroke="#333", sw=1, dash=None, op=1):
    (a, b), (c, d) = P(x0, y1), P(x1, y0)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{a:.1f}" y="{b:.1f}" width="{c-a:.1f}" height="{d-b:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>'
def line(x0, y0, x1, y1, stroke="#333", sw=1.5, dash=None):
    (a, b), (c, d) = P(x0, y0), P(x1, y1)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{stroke}" stroke-width="{sw}"{da}/>'
def text(x, y, s, size=13, anchor="middle", color="#000", weight="normal", rot=0):
    a, b = P(x, y)
    tr = f' transform="rotate({rot} {a:.1f} {b:.1f})"' if rot else ""
    return f'<text x="{a:.1f}" y="{b:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}" font-family="Helvetica, Arial"{tr}>{s}</text>'
def arc(hx, hy, r, a0, a1, color="#333"):
    pts = [P(hx + r * math.cos(math.radians(a0 + (a1 - a0) * i / 16)), hy + r * math.sin(math.radians(a0 + (a1 - a0) * i / 16))) for i in range(17)]
    return f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="4 3"/>'
def door(hx, hy, r, a_closed, a_open, color="#333"):
    ex, ey = hx + r * math.cos(math.radians(a_open)), hy + r * math.sin(math.radians(a_open))
    return line(hx, hy, ex, ey, color, 3) + arc(hx, hy, r, a_closed, a_open, color)
def poly(pts, fill="#fff", stroke="#333", sw=1.2):
    return f'<polygon points="{" ".join("%.1f,%.1f" % P(x, y) for x, y in pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def toilet(cx, wy, fy=1):   # on a wall at y = wy facing +y (fy=1) or a wall at x
    out = rect(cx - 0.20, cx + 0.20, wy, wy + 0.19 * fy, "#fff") if fy > 0 else ""
    pts = [(cx + 0.18 * math.cos(math.pi * i / 12), wy + 0.19 + 0.33 * math.sin(math.pi * i / 12)) for i in range(13)]
    return out + poly([(cx + 0.18, wy + 0.19)] + pts + [(cx - 0.18, wy + 0.19)]) + text(cx, wy + 0.33, "WC", 11)
def dim(x0, y0, x1, y1, s, off=0.0, color="#c00"):
    return line(x0, y0, x1, y1, color, 1) + text((x0 + x1) / 2, (y0 + y1) / 2 + 0.05, s, 11, color=color)

WALL = "#9a9a9a"
def base(wc_north=True, door_x=None):
    o = []
    o.append(rect(0, 0.31, 5.145, 7.408, WALL)); o.append(rect(0, 0.31, 8.377, 9.15, WALL))   # west outer wall, back door gap
    o.append(rect(0.05, 0.26, 5.724, 6.324, "#dff", "#333", 1)); o.append(text(-0.35, 6.02, "Fenster", 11, rot=-90))
    o.append(rect(0.31, 2.358, 5.145, 5.475, WALL))                                          # WC south wall
    o.append(rect(2.358, 2.772, 4.9, 5.849, WALL))                                           # Speis/Essen west wall
    o.append(rect(2.358, 6.10, 5.849, 6.349, WALL)); o.append(rect(6.96, 6.7, 5.849, 6.349, WALL))   # Flur south wall, Küche door gap
    o.append(rect(2.358, 2.657, 6.349, 7.408, WALL)); o.append(rect(2.358, 2.657, 8.506, 9.15, WALL)) # wall to the big Flur, Windfang door gap
    o.append(rect(0.31, 2.358, 8.506, 8.656, WALL)); o.append(rect(0.31, 2.358, 8.656, 9.15, "#eee", "#999"))  # back hall north wall, Bad
    o.append(rect(2.657, 4.406, 8.576, 8.876, WALL)); o.append(rect(5.335, 6.7, 8.576, 8.876, WALL))     # Flur north wall, Oma&Opa door gap
    o.append(rect(2.772, 5.24, 4.9, 5.849, "#f4efe4", "#999")); o.append(text(4.0, 5.3, "Speis", 13, color="#666"))
    o.append(rect(5.49, 6.7, 4.9, 5.849, "#f4efe4", "#999")); o.append(text(6.1, 5.3, "Küche", 13, color="#666"))
    o.append(text(1.33, 8.85, "Bad Großeltern", 12, color="#666")); o.append(text(3.5, 9.0, "Oma &amp; Opa", 12, color="#666"))
    o.append(rect(0.31, 2.358, 6.574, 6.723, "none", "#c00", 1, "5 4")); o.append(text(1.33, 6.60, "alte Wand", 10, color="#c00"))
    # back door (outside, west wall): hinged north, opens inward 90 deg; Windfang door: hinged north, opens west
    o.append(door(0.31, 8.377, 0.969, -90, 0)); o.append(text(-0.45, 7.9, "Hintertür", 12, weight="bold", rot=-90))
    o.append(text(-0.72, 7.9, "(raus in den Garten)", 10, rot=-90))
    o.append(door(2.358, 8.506, 1.098, -90, -180)); o.append(text(2.85, 7.95, "zum großen Flur", 11, anchor="start"))
    o.append(text(1.33, 8.15, "Durchgang (hinterer Flur)", 12, weight="bold"))
    o.append(text(4.6, 7.55, "großer Flur", 14, weight="bold", color="#555"))
    o.append(door(6.10, 5.849, 0.86, 90, 0) if False else "")
    return o

def wc_north(door_a, door_b):
    return [rect(0.31, door_a, 6.774, 6.923, WALL), rect(door_b, 2.358, 6.774, 6.923, WALL)]

def option_a():
    o = base() + wc_north(1.25, 2.01)
    o.append(rect(0.31, 1.21, 5.475, 6.774, "#e8eef6", "none"))                      # shower floor
    o.append(line(1.21, 5.475, 1.21, 6.225, "#2a7ab0", 4)); o.append(text(0.76, 6.0, "Dusche", 13, weight="bold"))
    o.append(text(0.76, 5.83, "90 × 130", 11)); o.append(text(1.12, 6.45, "Einstieg 55", 10, rot=-90))
    o.append(f'<circle cx="{P(0.76,5.9)[0]:.1f}" cy="{P(0.76,5.6)[1]:.1f}" r="6" fill="none" stroke="#333"/>')
    o.append(toilet(1.62, 5.475))
    o.append(rect(2.078, 2.358, 6.15, 6.55, "#fff")); o.append(text(2.2, 6.35, "HWB", 10, rot=-90))
    o.append(line(2.34, 6.10, 2.34, 6.60, "#2a7ab0", 3))                             # mirror
    o.append(door(2.01, 6.923, 0.76, 180, 90)); o.append(text(1.63, 6.85, "Tür 76", 10))
    o.append(rect(0.31, 1.15, 6.923, 7.223, "#d9b98a")); o.append(text(0.73, 7.04, "Schuhregal", 11))
    o.append(dim(0.31, 5.36, 2.358, 5.36, "205")); o.append(dim(2.45, 5.475, 2.45, 6.774, "")); o.append(text(2.53, 6.12, "130", 11, color="#c00", rot=-90))
    return o

def option_b():
    o = base() + wc_north(0.65, 1.41)
    o.append(rect(1.458, 2.358, 5.475, 6.774, "#e8eef6", "none"))
    o.append(line(1.458, 5.475, 1.458, 6.225, "#2a7ab0", 4)); o.append(text(1.91, 6.0, "Dusche", 13, weight="bold"))
    o.append(text(1.91, 5.83, "90 × 130", 11)); o.append(text(1.37, 6.45, "Einstieg 55", 10, rot=-90))
    o.append(f'<circle cx="{P(1.91,5.9)[0]:.1f}" cy="{P(1.91,5.6)[1]:.1f}" r="6" fill="none" stroke="#333"/>')
    o.append(toilet(0.85, 5.475))
    o.append(rect(0.31, 0.59, 6.35, 6.75, "#fff")); o.append(text(0.47, 6.55, "HWB", 10, rot=-90))
    o.append(door(1.41, 6.923, 0.76, 180, 90)); o.append(text(1.03, 6.85, "Tür 76", 10))
    o.append(rect(1.50, 2.358, 6.923, 7.223, "#d9b98a")); o.append(text(1.93, 7.04, "Schuhregal", 11))
    o.append(dim(0.31, 5.36, 2.358, 5.36, "205")); o.append(dim(2.45, 5.475, 2.45, 6.774, "")); o.append(text(2.53, 6.12, "130", 11, color="#c00", rot=-90))
    return o

def garderobe():
    o = base() + wc_north(1.25, 2.01)
    o.append(rect(0.31, 2.358, 5.475, 6.774, "#f2f2f2", "none")); o.append(text(1.33, 6.1, "neues Bad (Variante A oder B)", 11, color="#666"))
    o.append(rect(0.31, 1.15, 6.923, 7.223, "#d9b98a"))
    # G1: south wall of the big Flur, x 2.80..4.80
    o.append(rect(2.80, 4.80, 6.349, 6.38, "#a0522d")); o.append(rect(2.80, 4.80, 6.38, 6.70, "#a0522d", "#a0522d", 1, "4 3", 0.25))
    o.append(text(3.80, 6.52, "G1 Garderobe Südwand ~200", 12, weight="bold", color="#7a3a10"))
    # G2: north wall, x 2.75..4.30
    o.append(rect(2.75, 4.30, 8.545, 8.576, "#3a6ea5")); o.append(rect(2.75, 4.30, 8.225, 8.545, "#3a6ea5", "#3a6ea5", 1, "4 3", 0.25))
    o.append(text(3.52, 8.35, "G2 Garderobe Nordwand ~155", 12, weight="bold", color="#24507e"))
    o.append(door(4.406, 8.876, 0.929, 0, 90)); o.append(text(4.87, 8.45, "Tür Oma&amp;Opa", 10))
    o.append(door(6.10, 6.349, 0.86, 0, 90) if False else "")
    o.append(text(6.3, 6.15, "Küchentür", 10))
    return o

panels = [("Variante A – Dusche West (Fenster in der Dusche)", option_a()),
          ("Variante B – Dusche Ost", option_b()),
          ("Garderobe im großen Flur: G1 (Südwand) oder G2 (Nordwand)", garderobe())]
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW:.0f}" height="{(PH + 40) * 3:.0f}" viewBox="0 0 {PW:.0f} {(PH + 40) * 3:.0f}">',
       f'<rect width="100%" height="100%" fill="#fff"/>']
for i, (title, items) in enumerate(panels):
    out.append(f'<g transform="translate(0 {i * (PH + 40) + 30:.0f})">')
    out.append(f'<text x="10" y="-8" font-size="17" font-weight="bold" font-family="Helvetica, Arial">{title}</text>')
    out += items
    out.append(f'<text x="{PW-10:.0f}" y="16" font-size="12" text-anchor="end" font-family="Helvetica, Arial">N ↑   1 m = {S} px</text>')
    out.append('</g>')
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out))
