"""Draws the agreed EG lamp plan (v1, issue #22) as SVG: the Grundriss EG of plans/eg.svg with every lamp
of the core as a numbered marker and a tick into the room (red: both layouts, orange: default layout only,
blue: Alternativ only, purple: the hood's spots). Every position comes from code/house_core.py
(WANDLAMPEN_EG), code/ofen.py (the bed's Wandlampe) and code/kueche.py (the hood); nothing is repeated here.
The numbers are the issue's order, as agreed on 2026-11-14 (6: the Ofen bed, 9: the hood).
Usage: python3 lampen_eg_svg.py lampen_eg_v1.svg"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "code"))
import house_core as hc, export_plans as ep, ofen, kueche

NUMBERS = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14] + list(range(15, 37))   # WANDLAMPEN_EG in its order
assert len(NUMBERS) == len(hc.WANDLAMPEN_EG)
COLOUR = {None: "#d0021b", "main": "#e07b00", "alt": "#1f6fd1", "spot": "#7b3fb5"}

x0, y0 = ofen.OFEN_AT
lamps = [(n, x, y, fx, fy, v) for n, (x, y, fx, fy, h, v) in zip(NUMBERS, hc.WANDLAMPEN_EG)]
lamps.append((6, x0, y0 - 0.35, 1, 0, None))                         # the bed's (sub-model (0.35, 0), y = 0 wall)
lamps.append((9, kueche.XE - 0.04, (kueche.HY0 + kueche.HY1) / 2, -1, 0, "spot"))   # the hood's strip
T = ep.plan_to_sheet()
g = ['<g id="lamps">']
for n, x, y, fx, fy, v in sorted(lamps):
    c = COLOUR[v]
    (sx, sy), (tx, ty), (lx, ly) = T((x, y)), T((x + fx * 0.35, y + fy * 0.35)), T((x + fx * 0.75, y + fy * 0.75))
    g.append(f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{tx:.2f}" y2="{ty:.2f}" stroke="{c}" stroke-width="0.35"/>')
    g.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="0.9" fill="{c}"/>')
    g.append(f'<text x="{lx:.2f}" y="{ly + 0.9:.2f}" font-size="2.6" font-weight="bold" fill="{c}" text-anchor="middle">{n}</text>')
g.append('</g>')
svg = open(os.path.join(HERE, "..", "..", "plans", "eg.svg")).read()
open(sys.argv[1], "w").write(svg.replace("</svg>", "\n".join(g) + "\n</svg>"))
