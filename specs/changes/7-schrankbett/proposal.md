---
feature: 7-schrankbett
title: "Proposal: Schrankbett im Yoga-Zimmer"
status: applied
order: 1
created: 2026-11-13
edited: 2026-11-13
---
# Proposal: Schrankbett im Yoga-Zimmer

## What

The Yoga room's bed (OG, NW room, head at the south wall) becomes a **Schrankbett**: a 2 × 2 m
bed that folds up into a wall of cabinets on the south wall. Folded up, the bed's underside is a
wooden face between two narrow cabinets, a Blende above it up to the ceiling: one closed
Schrankwand, 45 cm deep. Folded down it lies where the bed lies today (shifted north by the
cabinet depth). It is a new sub-model "Schrankbett" (`code/schrankbett.py`, `web/schrankbett.html`)
and is built into the house. Issue #7.

## Why

Till wants the Yoga room usable as a yoga room and as a guest room: the bed out of the way by day,
a full 2 × 2 m bed at night, plus storage.

## Scope

- In:
  - an agreed drawing first (plan, front, section with the fold arc), like the other sub-models:
    `input/2026-11-13 input/schrankbett_v1.svg` + generator beside it
  - `code/schrankbett.py`: carcass with two side cabinets (doors, handles), Blende, the folding
    bed (wooden underside panel with grip, frame, mattress, bedding, fold-out foot), own
    `random.Random`
  - house: replaces `bed("OG", 0.86, 2.45, 8.862, 10.85, "S", …)`; built folded down
  - sub-model page "Schrankbett" in the Modell drop-down, with the pieces of the south wall (door
    opening) and the west wall (window) and dimension lines
  - the viewer folds the bed up and down (sub-model page, house stage Eingerichtet); film,
    Rundgang and plan sheets keep it down
- Out (non-goals): inner fittings of the side cabinets (shelves, rail), a lift mechanism
  (springs, linkage), any change to the room's walls, door or window; a cabinet above the bed

## Expected outcome

- Sub-model page shows the Schrankwand, the bed folds up and down without passing through wall,
  floor, Blende or ceiling (a test sweeps it 0–90°).
- Unit: x from the west wall (0.31) to just west of the door casing (~3.10), 45 cm deep, up to
  the ceiling (2.20 m room height); lying area 2.00 × 2.00; side cabinets ~36–40 cm wide.
- In the house the bed lies down at y ≈ 9.3 … 11.3; the Rundgang still clears all geometry
  (≥ 0.25 m).

## Decisions taken with Till (2026-11-13)

- Above the bed only a Blende up to the ceiling, no cabinet (2.20 m room, the bed folded up is
  ≥ 2.05 m high).
- On the south wall, from the west wall to the door, ~40 cm cabinet each side; the left cabinet
  covers ~35 cm of the west window's inner reveal (y 8.96 … 9.95) and stops its leaf from opening
  fully: accepted.
- Depth 45 cm.

## Open questions

- Fold geometry: with a simple pivot, a 2.04 m body has to swing under 2.19 m clear height.
  Pivot place and body thickness (~36–40 cm) are found by the sweep test; if no pivot clears, the
  Blende gets thinner or the body thinner — the drawing (step 1) shows the result for Till's OK.
- Wood: spruce like the other OG furniture (assumed), or another species?
