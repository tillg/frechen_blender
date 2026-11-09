---
feature: kueche-speis
title: "Proposal: Küche as a sub-model, new Speis, sub-model drop-down"
status: applied
order: 1
created: 2026-11-09
edited: 2026-11-09
---
# Proposal: Küche as a sub-model, new Speis, sub-model drop-down

## What

The Küche becomes a sub-model `code/kueche.py` (sink run, Wamsler wood cooker with its hood,
60 cm east run, peninsula with the induction cooktop, wall cabinets, Besenschrank, the flue box),
embedded in the house like the Ofen, the desk and the Bad, with its own page `web/kueche.html`.
The Speis gets the agreed fit-out (open shelf, 91.9 aisle, open shelf, back-to-back cabinet with
doors to the Essen; all to the ceiling) in place of today's shelves and the Speis/Essen wall, and
a sliding door on the kitchen side. The kitchen door to the Flur sits where it really is. The
viewer's links to the sub-models become one drop-down on every page.

## Why

The plan's kitchen door is about 1 m too far east (photo of 2026-11-09), so the plan's sink run
stands in front of the real door. The owners want the Speis as a walk-in pantry with storage
towards the dining table. With four sub-models, a row of links no longer fits the tool bar.

## Scope

- In:
  - Agreed drawing `input/2026-11-09 input/speis_kueche_v6.svg` (+ `.png`, generator `.py`).
  - Kitchen door to the Flur at the measured position (opening 6.10–6.96, clear 81 cm), hinged
    west, leaf opened 90° into the Küche.
  - `code/kueche.py`: `KUECHE_AT`, `kueche_neu(c, x0, y0)` → dims; `house_core.build_kueche()`;
    `export_gltf.py --kueche`; `web/kueche.html`.
  - Kitchen layout v6: sink run from the door frame (x 7.05) into the NE corner (≈ 150), east run
    60 from the peninsula, the Wamsler directly south of the sink run's corner gap, its hood moved
    with it, wall cabinets over the sink run up to the flue box and over the east run up to the
    hood, Besenschrank 51 × 55 × 2.20 behind the open kitchen door, flue box (Abzug) in the NE
    corner from 1.80 m to the ceiling. Peninsula and cooktop unchanged.
  - Speis: wall Speis/Essen removed; wall Speis/Küche ends at y 3.13 with a 91.9 opening
    (y 4.33–5.249); shelf A (north wall, 60, open south), aisle 91.9 (west end free), shelf B (60,
    open north), cabinet C back to back with B (60, doors south); A/B/C to the ceiling; sliding
    door 100 on the kitchen face, slid open to the south (left as seen from the Küche).
  - Drop-down "Teilmodell" navigation on the house page and every sub-model page.
  - Rundgang route through the new door and into the Speis aisle; tour golden.
- Out (non-goals): film re-capture; routing the Wamsler's pipe to the flue box (the model keeps
  its pipe into the east wall); colours/materials of the kitchen; the OG.

## Expected outcome

- Still of the Küche from the Flur door: Besenschrank left, leaf at 90°, sink run to the corner
  under the flue box, Herd + hood beside it, peninsula unchanged.
- Still of the Speis aisle from the sliding door: A and B to the ceiling, C seen from the Essen
  with its doors, no Speis/Essen wall.
- `http://localhost:5377/kueche.html` shows the kitchen with dimension labels; every page has a
  drop-down that reaches every other page.
- Rundgang camera ≥ 0.25 m from all geometry, no ray hits between frames.

## Open questions

none — settled in the conversation of 2026-11-09 (v1–v6 of the drawing).
