---
feature: 29-waschkueche-becken-dusche
title: "Proposal: basin and shower in the Waschküche"
status: proposed
order: 1
created: 2026-11-15
edited: 2026-11-15
---
# Proposal: basin and shower in the Waschküche

## What

Issue #29: the OG Waschküche (x 5.59 .. 8.59, y 2.79 .. 6.06; door in the north wall x 7.15 .. 8.17,
leaf open flat to the west; no window) gets a Waschbecken with blue tiles behind it and a small
floor-level shower cabin 1.10 × 1.10 with glass walls, one of them an opening glass door.

## Why

The user's request (issue #29, German): „In der Waschküche möchten wir ein Waschbecken und eine kleine
Dusche haben. Das Waschbecken soll eines unserer Standard Waschbecken sein und die Wand dahinter blau
gefliest. Die Dusche soll von der Konstruktion her ebenerdig sein, so wie die anderen, also einfach in
der Fliesenebene draufgesetzt. Die Duschkabine soll allerdings kleiner sein da reichen 1,10 m mal 1,10 m
mit Glaswänden, wovon eine Glaswand eine zu öffnende Tür ist. Bitte positioniere das Waschbecken und die
Dusche sinnvoll, so wie du denkst.“

## Scope

- In: a new module `code/waschkueche.py` (constants and builder, house only); the shower cabin on the
  west wall just north of the table (limestone floor patch in the floor's plane, limestone on the west
  wall to 2.0, head on the west wall, glass to the south, north and east, the east glass with a 60 cm
  door hinged north, opening out); the basin (Waschbecken einzeln 60 × 47) on the east wall north of the
  washer tower on Taubenblau tiles, a wood-framed mirror 80 × 85 above; the tower lamp moves over the
  mirror; the basket cupboard shortened to the wall between cabin and door leaf (two baskets per shelf);
  tests (layout, clearances, Rundgang); plan sheets; README, CLAUDE.md, Blender reload lists.
- Out (non-goals): the room's floor (oak until #28), its walls, door and the south wall's glazing (#30);
  a sub-model page; animating the glass door; the Blender backend (dormant, #35).

## Expected outcome

- Cabin outer 1.10 × 1.10 (x 5.59 .. 6.69, y 3.61 .. 4.71): limestone floor slabs at the room floor's
  tile plane (top +0.018, no tray), drain in the middle; glass panes 8 mm to 2.0 with a top rail; a glass
  door 60 wide in the east glass with two hinges and a bar handle; nothing within the door's 60 cm arc.
- Basin 60 × 47 centred y 5.28 on the east wall, Taubenblau tiles 84 wide behind it, mirror 80 × 85 at 1.17,
  one Wandlampe over it at 2.10; clear of the room door's leaf sweep (≥ 5 cm), 60 cm free in front.
- Nothing new on the south wall (#30 glazes its top metre); the table, machines and leaf untouched.
- Every Rundgang key and Standpunkt keeps ≥ 0.25 m from the new Parts.

## Open questions

none — decided and logged in `DECISIONS.md` (run-2026-11-15-1633-21 … -23; unattended run).
