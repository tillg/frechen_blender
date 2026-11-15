---
feature: 32-dusche-badewanne
title: "Proposal: shower and bathtub in the Gästebad"
status: proposed
order: 1
created: 2026-11-15
edited: 2026-11-15
---
# Proposal: shower and bathtub in the Gästebad

## What

Issue #32: the OG Gästebad (`code/gaestebad.py`) gets a bathtub besides the shower. Entering through
the Flur door (east wall) one faces the back wall (the west wall, outer wall with the big window
y 6.77 .. 7.76, sill 0.75): the shower on the left (SW corner), the tub to its right along the back
wall under the window, so one looks out of it from the tub. Toilet and basin move to sensible places.

## Why

The user's request (issue #32, German): "Das Gästebad im 1. Stock soll nicht nur eine Dusche sondern
auch eine Badewanne haben. Wenn man rein kommt, an der hinteren Wand sinnvollerweise links die Dusche
und rechts davon entlang der hinteren Wand die Badewanne. So dass man in der Badewanne liegend aus
dem hinteren Fenster schauen kann. Bitte überlege eine sinnvolle Anordnung, wo dann Waschbecken und
Toilette hinkommen."

## Scope

- In: `gaestebad.py` layout (shower, new tub, partition length, WC niche, toilet, tiles, basin,
  mirror, lamps, dims), its tests, `web/src/gaestebad.js` (comment, views) and its e2e labels, the
  OG lamp counts, a Rundgang clearance test, README, CLAUDE.md, the plan sheets.
- Out (non-goals): the room's walls, windows and door; the EG Gäste-WC below; the Blender backend
  (dormant, #35).

## Expected outcome

- Shower 101 × 131 in the SW corner (west wall to the partition, south wall to the tub), walk-in,
  head on the south wall; its entrance on the east side between the partition (now ending at y 6.15)
  and the tub: ≥ 60 cm clear.
- Tub 180 × 75 built in along the west wall from y 6.77 to the north wall, rim 0.58 below the
  window sill 0.75, the window over the tub's south half; limestone apron.
- Toilet centred in the WC niche east of the partition (≥ 20 cm free each side, ≥ 60 in front),
  Taubenblau tiles on the niche's walls.
- Basin single 60 on the north wall between tub and door with a wood mirror 80 × 85; nothing touches
  the open leaf; the door's opening stays free.
- Every Rundgang key and Standpunkt keeps ≥ 0.25 m from the Gästebad's Parts.

## Open questions

none — decided and logged in `DECISIONS.md` (run-2026-11-15-1633-15, -16; unattended run).
