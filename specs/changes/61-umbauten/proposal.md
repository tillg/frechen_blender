---
feature: 61-umbauten
title: "Proposal: Umbauten EG/OG (Speis-Trockenwand, Muldenlüfter, Bad Oma & Opa, Waschküche, Hintereingang, Flur-Garderobe)"
status: applied
order: 1
created: 2026-11-27
edited: 2026-11-27
---
# Proposal: Umbauten EG/OG (Speis-Trockenwand, Muldenlüfter, Bad Oma & Opa, Waschküche, Hintereingang, Flur-Garderobe)

## What

Seven changes the user asked for on 2026-11-27 (issue #61), one plan step each:

1. **Speis**: a thin drywall (7.4 cm) behind shelf B on the Essen side, from cabinet C's front to the Küche wall; Speis, B's board back and C unchanged; the two Wandlampen on B's back move onto the drywall's face.
2. **Küche**: the hood over the Halbinsel (`_Haube`, incl. its spot strip and light) is gone; the cooktop gets a downdraft vent (Muldenlüfter) between its burners. The Abzug (Kaminschacht) and the Wamsler pipe stay.
3. **Bad Oma & Opa**: the niche's middle wall and the second sliding leaf are gone: WC and Schrank are one room, its front an opening (102.4) over the WC in the west and a wall piece in front of the cabinet in the east; one sliding leaf parks open in front of the wall piece and rolls over the opening; the Schrank becomes a white built-in cabinet with two doors up to the ceiling, inside the WC.
4. **Waschküche Oberlicht** (to the Bad Nadine & Till): half as high, at the top: sill 1.70 instead of 1.20 (room height 2.20).
5. **Waschküche**: the shower cabin is gone; the basket cupboard runs again to y 5.95 with three baskets per shelf (as before #29).
6. **Hintereingang** (variant B, drawing `input/2026-11-27 input/hintereingang_optionen.svg`): the WC's north wall moves 20 cm north (room 204.8 × 129.9); partition, Garderobe and the Flur basin are gone; one room: walk-in shower 90 × 130 in the east (glass 75 from the south wall, entry 55), toilet on the south wall in the west, basin 40 + mirror on the west wall north of the window; door 76 in the north wall (west part), opening outward into the back hall, hinged east; in the back hall east of the door a shoe rack with shoes.
7. **Flur-Garderobe** (G1): on the big Flur's south wall (back of the Speis), x 2.80–4.80: an old-spruce hook board with many iron hooks in two rows and a hat shelf on brackets, coats hanging on it; the two Flur Wandlampen there move up over the shelf.

## Why

The family's revised wishes for the rebuild (issue #61).

## Scope

- In: core modules (`house_core`, `kueche`, `bad`, `elternbad`, `waschkueche`, `gaeste_wc`, new `garderobe`), plan sheets, viewer sub-model names/colours, tests, README, CLAUDE.md.
- Out (non-goals): new light over the Halbinsel; the Waschküche door and Wandlampen (`LAMPE_H`) stay as they are; no new sub-model page for the Flur-Garderobe; the dormant Blender backend.

## Expected outcome

Viewer and plan sheets show the seven changes; `check.sh full` green; parts not touched keep their random draws (`rnd`), so nothing else changes look.
