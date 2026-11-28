"""Draft drawing: the Stube's Ofen as a triangle in the NW corner, its glass front towards the room (request
2026-11-28). House coordinates, north up, 1 m = S px. Usage: python3 ofen_dreieck_svg.py ofen_dreieck_optionen.svg"""
import math, sys
S, X0, X1, Y0, Y1 = 100, 8.1, 14.6, 0.2, 6.75
PW, PH = (X1 - X0) * S, (Y1 - Y0) * S
CX, CY = 9.06, 5.845                                   # the stove's corner: Stube west wall x Flur wall

def P(x, y): return ((x - X0) * S, (Y1 - y) * S)
def pts(ps): return " ".join("%.1f,%.1f" % P(x, y) for x, y in ps)
def poly(ps, fill="#fff", stroke="#333", sw=1.2, dash=None, op=1):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polygon points="{pts(ps)}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>'
def rect(x0, x1, y0, y1, **k): return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **k)
def line(x0, y0, x1, y1, stroke="#333", sw=1.5, dash=None):
    (a, b), (c, d) = P(x0, y0), P(x1, y1)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{stroke}" stroke-width="{sw}"{da}/>'
def text(x, y, s, size=13, anchor="middle", color="#000", weight="normal", rot=0):
    a, b = P(x, y)
    tr = f' transform="rotate({rot} {a:.1f} {b:.1f})"' if rot else ""
    return f'<text x="{a:.1f}" y="{b:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}" font-family="Helvetica, Arial"{tr}>{s}</text>'
def arrow(x0, y0, x1, y1, color="#e07000"):
    (a, b), (c, d) = P(x0, y0), P(x1, y1)
    return (f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{color}" stroke-width="2" '
            f'stroke-dasharray="7 5" marker-end="url(#ah)"/>')

WALL, GLASS, FIRE = "#9a9a9a", "#2a7ab0", "#f08a24"

def base():
    o = [rect(8.557, 9.056, 2.938, 6.349, fill=WALL), rect(8.557, 9.056, 0.2, 0.54, fill=WALL),   # Stube west wall (passage
         rect(9.056, 14.6, 5.849, 6.349, fill=WALL), text(8.42, 1.75, "Durchgang Essen", 10, rot=-90),   # to the Essen), Flur wall
         rect(9.056, 14.6, 0.2, 0.415, fill=WALL)]
    o.append(rect(11.004, 11.803, 5.849, 6.349, fill="#fff", stroke="#fff"))                # Stube door
    o.append(line(11.004, 5.849, 11.004, 5.05, "#333", 1)); o.append(text(11.4, 5.55, "Tür Stube", 11))
    o.append(rect(9.78 - 0.24, 9.78 + 0.24, 5.849, 6.349, fill="#fde3c4", stroke="#c06000"))  # back door to the Flur
    o.append(text(9.78, 6.5, "Feuertür Flur (bleibt)", 11, color="#c06000"))
    o.append(text(11.8, 6.55, "Flur", 14, weight="bold", color="#555"))
    o.append(text(12.4, 2.4, "Stube", 18, weight="bold", color="#555"))
    # sofa (back to the stove) and the Sitzecke in the SE
    a = math.atan2(0.415 - 4.64, 14.351 - 10.96); sx, sy = 14.351 + 0.75 * (10.96 - 14.351), 0.415 + 0.75 * (4.64 - 0.415)
    ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    sofa = [(sx + ux * du + vx * dv, sy + uy * du + vy * dv) for du, dv in ((-0.45, -1.1), (0.45, -1.1), (0.45, 1.1), (-0.45, 1.1))]
    o.append(poly(sofa, fill="#e9e2d0", stroke="#999")); o.append(text(sx, sy - 0.05, "Sofa", 11, color="#777"))
    o.append(f'<circle cx="{P(13.4, 0)[0]:.1f}" cy="{P(0, 1.35)[1]:.1f}" r="{0.3*S:.0f}" fill="#e9e2d0" stroke="#999"/>')
    o.append(text(13.4, 1.32, "Sitzecke", 11, color="#777"))
    o.append(f'<circle cx="{P(11.7, 0)[0]:.1f}" cy="{P(0, 3.13)[1]:.1f}" r="4" fill="#333"/>'); o.append(text(11.7, 2.95, "Raummitte", 10, color="#333"))
    return o

def bed(o):
    o.append(rect(9.06, 10.96, 5.145, 5.845, fill="none", stroke="#8a6a3a", sw=1.2, dash="6 4"))
    o.append(text(11.0, 5.27, "Bett oben 70 × 190 (bleibt, gestrichelt)", 10, "start", color="#8a6a3a"))

def benches(o, west_from):
    o.append(rect(9.06, 9.665, west_from - 1.60, west_from, fill="#d9b98a", stroke="#8a6a3a"))
    o.append(text(9.36, west_from - 0.8, "Bank 160", 10, rot=-90))
    o.append(rect(10.265, 10.865, 5.145, 5.845, fill="#d9b98a", stroke="#8a6a3a", op=0.6)); o.append(text(10.57, 5.3, "Bank", 10))

def stove_now():
    o = base()
    o.append(rect(9.06, 10.26, 5.345, 5.845, fill="#f4f1ea", stroke="#333", sw=2))
    o.append(line(9.66 - 0.325, 5.345, 9.66 + 0.325, 5.345, FIRE, 6)); o.append(text(9.66, 5.42, "Ofen 120 × 50", 11))
    bed(o); benches(o, 4.64)
    o.append(arrow(9.66, 5.30, 9.66, 4.0)); o.append(text(9.95, 3.85, "Feuer schaut auf die Bank", 11, "start", "#e07000"))
    return o

def stove_tri(a, title_w):
    """Isosceles right triangle with legs a along both walls; glass front (65) centred on the hypotenuse."""
    o = base()
    tri = [(CX, CY), (CX + a, CY), (CX, CY - a)]
    o.append(poly(tri, fill="#f4f1ea", stroke="#333", sw=2))
    mx, my = CX + a / 2, CY - a / 2                       # middle of the front
    d = 0.325 / math.sqrt(2)
    o.append(line(mx - d, my - d, mx + d, my + d, FIRE, 6))
    # firebox as now (about 55 x 40 inside), behind the glass
    fb = 0.40
    nx, ny = -1 / math.sqrt(2), 1 / math.sqrt(2)          # into the stove
    box = [(mx - d * 0.85, my - d * 0.85), (mx + d * 0.85, my + d * 0.85),
           (mx + d * 0.85 + nx * fb * 0.75, my + d * 0.85 + ny * fb * 0.75), (mx - d * 0.85 + nx * fb * 0.75, my - d * 0.85 + ny * fb * 0.75)]
    o.append(poly(box, fill="#3a2a20", stroke="none", op=0.8))
    bed(o); benches(o, CY - a - 0.005 if CY - a - 0.005 < 4.64 else 4.64)
    o.append(arrow(mx + 0.05, my - 0.05, 11.55, 3.28)); o.append(arrow(mx + 0.05, my - 0.05, 13.1, 1.6))
    o.append(text(mx + 0.75, my - 0.35, "Scheibe 65 zur Raummitte (45°)", 11, "start", "#e07000"))
    o.append(text(CX + a / 2, CY + 0.08, f"{round(a*100)}", 11, color="#c00")); o.append(text(CX - 0.12, CY - a / 2, f"{round(a*100)}", 11, color="#c00", rot=-90))
    o.append(text(mx + 0.33, my + 0.10, f"Front {round(a*math.sqrt(2)*100)}", 11, color="#c00", rot=-45))
    for k, t in enumerate([f"Ofen: Dreieck {round(a*100)} × {round(a*100)} in der Ecke, {round(a/math.sqrt(2)*100)} von der Ecke bis zur Front",
                           "dunkel: Brennraum, klein wie jetzt; Scheibe 65 mittig in der schrägen Front",
                           "Feuertür zum Flur bleibt, Höhe 115, Bett oben bleibt",
                           "Feuer sichtbar von Raummitte, Sitzecke und Stubentür"]):
        o.append(text(9.3, 1.25 - 0.22 * k, t, 12, "start", "#333"))
    return o

panels = [("Jetzt – Ofen 120 × 50, Scheibe nach Süden", stove_now()),
          ("Variante A – Dreieck 120 × 120, Front 170 schräg zur Raummitte", stove_tri(1.20, 0)),
          ("Variante B – Dreieck 100 × 100, Front 141 (kompakter)", stove_tri(1.00, 0))]
H = (PH + 50) * len(panels)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW:.0f}" height="{H:.0f}" viewBox="0 0 {PW:.0f} {H:.0f}">',
       '<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#e07000"/></marker></defs>',
       '<rect width="100%" height="100%" fill="#fff"/>']
for i, (title, items) in enumerate(panels):
    out.append(f'<g transform="translate(0 {i * (PH + 50) + 30:.0f})">')
    out.append(f'<text x="10" y="-8" font-size="17" font-weight="bold" font-family="Helvetica, Arial">{title}</text>')
    out += items
    out.append(f'<text x="{PW-10:.0f}" y="16" font-size="12" text-anchor="end" font-family="Helvetica, Arial">N ↑   1 m = {S} px</text>')
    out.append('</g>')
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out))
