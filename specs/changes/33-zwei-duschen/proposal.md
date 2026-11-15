---
feature: 33-zwei-duschen
title: "Proposal: two showers in the Bad Nadine & Till"
status: applied
order: 1
created: 2026-11-15
edited: 2026-11-15
---
# Proposal: two showers in the Bad Nadine & Till

## What

Issue #33: the OG Bad Nadine & Till (`code/elternbad.py`) gets two walk-in showers on one strip along
the back wall (the west wall, opposite the door `TUER` in the east wall): one head in the back-left
(SW) corner, one in the back-right (NW) corner, one glass pane per shower towards the room, a 60 cm
passage between the panes in the middle. Toilet and basin move into the rest of the room.

## Why

The user's request (issue #33, German): "Wir möchten in unserem Bad zwei Duschen haben … an der
hinteren Wand … in der Mitte … ein 60 cm breiter Durchgang … Bitte finde eine sinnvolle Aufteilung,
wo dann Toilette und Waschbecken positioniert werden."

## Scope

- In: `elternbad.py` layout (showers, glass, limestone, toilet, basin, mirror, lamps, tiles, dims),
  its tests, the Rundgang's stop in the Bad (it walks through the new south pane today), the sub-model
  page comment/views, README, CLAUDE.md, the plan sheets.
- Out (non-goals): #30 (glass in the Waschküche partition) and #29 (Waschküche basin + shower); the
  room's walls, door and window stay. The Blender backend is dormant (#35).

## Expected outcome

- Strip 90 deep along the west wall, over the room's full 2.22; panes at x = WI + 0.90, each from its
  side wall to 30 cm short of the middle: 60 cm clear between their Parts.
- Toilet on the north wall between the glass and the basin, ≥ 20 cm free each side, ≥ 60 free in
  front; basin (single 60) with an 80 × 85 wood mirror on the east wall north of the door; the open
  leaf clears everything (pytest on Part boxes).
- Nothing on the north wall (the Waschküche partition) above 1.20 (#30's future glass sill).
- Every Rundgang key in the Bad keeps ≥ 0.25 m from the new Parts.

## Open questions

none — decided and logged in `DECISIONS.md` (unattended run).
