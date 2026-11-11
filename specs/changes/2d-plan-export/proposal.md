---
feature: 2d-plan-export
title: "Proposal: 2D plan export"
status: applying
order: 1
created: 2026-11-11
edited: 2026-11-11
---
# Proposal: 2D plan export

## What

A deterministic export turns the model into six 2D plan sheets as SVG for the architect: **Grundriss EG**, **Grundriss OG** and the four **Ansichten** (Nord, Ost, Süd, West). The sheets carry dimensions and look like the architect's own plans in `input/2026-11-03 input/*.pdf`.

The export is a third backend next to Blender and glTF: `code/export_plans.py`, pure Python. It reads the same Blueprint and writes `plans/*.svg`, which are committed. The same model always gives byte-identical files.

## Why

The family changes the house in the model: Bad Großeltern, Küche, Gäste-WC, furniture, doors. The architect works from 2D plans. Today every change goes back to the architect as screenshots and hand-written dimensions, which they must redraw.

A plan sheet straight from the model removes that step and the transcription errors. Because the output is deterministic and committed, `git diff plans/` shows what a model change did to the drawings.

## Scope

**In:**

- **Sheets:** six sheets, each A3 landscape at 1:100. The SVG is sized in mm, so printing at 100 % gives true scale. Every sheet has its own title block with project, sheet name, scale and the model state (a hash, not a date), plus a north arrow on the floor plans. No architect branding.
- **Floor plans:**
  - Horizontal section at a fixed cut height per storey. Cut walls are filled with diagonal hatching inside a heavy outline that runs round the wall as a whole, with no seams between the boxes it is built from. Other cut parts get a thin outline.
  - The built-ins below the cut are drawn in thin lines, seen from above: stairs, kitchen, sanitary, stoves, Speis shelves, built-in cabinets. Loose furniture (the model's `FURNITURE`: tables, chairs, beds, sofas, desk, pantry stock) is left out.
  - Windows and doors show as gaps in the cut, and door swings as arcs.
  - Each room gets a label with the architect's room name and the net area in m², computed from the model.
- **Floor-plan dimensions:** chains on all four sides, in the architect's style: tick marks, cm below 1 m, a superscript 5 for half centimetres. Three chains per side: openings, walls and rooms along the facade, and the overall length.
- **Elevations:** an orthographic view of each facade with hidden lines removed. That covers walls, windows, shutters, cladding, roof, balconies, annex, terrace and lamps. Below ±0,00 there is a grey ground band, as on the architect's sheets.
- **Elevation dimensions:** level marks (Höhenkoten) for ±0,00, OK FFB OG, eaves and ridge, plus the overall width. The architect's elevations carry none; this set is settled.
- **Running it:** a command (`python3 code/export_plans.py plans/`), tests, and a README section.

**Out (non-goals):**

- PDF, DXF and DWG output.
- Cross-sections (Schnitte).
- Interior dimension chains.
- Shadows on the elevations.
- Marking new versus existing construction (the architect's pink).
- Dashed lines for parts above the cut (balcony, roof overhang).
- Loose furniture in the floor plans, and furniture symbols in the architect's style.
- Plan export from the web viewer.
- Garden, grass and windrose.

## Expected outcome

- `python3 code/export_plans.py plans/` writes `eg.svg`, `og.svg`, `nord.svg`, `ost.svg`, `sued.svg` and `west.svg`. That takes ≤ 30 s, each file is ≤ 2 MB, and the files parse as XML. The spike gave the south elevation in about 3 s at 0.5 MB.
- Two runs in separate processes with different `PYTHONHASHSEED` give byte-identical files.
- Printed at 100 % on A3, 1 m in the model measures 10 mm, and the scale bar on the sheet checks it.
- The overall chains of the EG plan read the model's footprint, `W_OUT` = 14.88⁵ and `D_OUT` = 12.88⁵. The opening chain matches `OPENINGS`, and every chain sums to its overall dimension.
- Every room has exactly one label. The Bad Großeltern area equals its inner dimensions from `bad.py` (without the niche, which is apart behind its lintel; user 2026-11-11).
- A test fails when `plans/` is older than the model, so the committed plans are always current.
- Rasterised with `rsvg-convert` and laid over `grundriss_eg.png`/`grundriss_og.png`, the walls line up with the architect's plan. Where the model deliberately differs (Bad, Küche, Gäste-WC), it shows the model.
