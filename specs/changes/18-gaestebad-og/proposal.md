---
feature: 18-gaestebad-og
title: "Proposal: Gästebad im 1. Stock"
status: applied
order: 1
created: 2026-11-13
edited: 2026-11-13
---
# Proposal: Gästebad im 1. Stock

## What

The OG Bad at the end of the Flur (NW, the architect's "Bad 6,98 m²" with "WC 2,26 m²"; issue #18)
is rearranged after the Gäste-WC below it in the EG ([gaeste_wc.py](../../../code/gaeste_wc.py)).

- Its partition moves onto the EG partition (x 1.319–1.419).
- West of it is an open WC niche, with no wall or door towards the Bad. The toilet is centred on
  its south wall and faces north, as in the EG.
- East of it is a walk-in shower, 115 cm wide and 139 cm long. It reaches to 5 cm short of the
  Flur door's leaf, which lies open flat against the east wall. On the shower's north edge a 65 cm
  glass panel runs from the east wall, so it "lands just before the open door". Beside the
  partition 50 cm stay open, and there is no door.
- The Waschbecken doppelt 120 moves to the middle of the north wall, under a 140 × 95 mirror in a
  10 cm wooden frame like the OG Flur's.

The Gästebad becomes a module of its own, `code/gaestebad.py`, and a sub-model page
`web/gaestebad.html` that shows it with its four walls and its dimensions.

## Why

Issue #18: toilet and shower oriented as in the Gäste-WC in the EG; the shower glass longer so the
shower needs no door; the toilet without a door; the basin in the middle of the wall; above it a
mirror wider than the basin with a wooden frame, like the mirror in the OG Flur. The 90 cm shower
alcove can't take a longer glass and still leave an entry; over the EG partition it gets 115 cm.

The user made these choices on 2026-11-13:
- the partition goes over the EG one, and the WC wall is removed
- after the first review, the shower gets longer, so the half glass wall ends just before the open door
- the Gästebad becomes a sub-model with dimensions

## Scope

- In:
  - the OG partition
  - the WC wall and door (removed)
  - toilet, shower (tray, glass, head), Waschbecken and mirror
  - the WC tiles and the floors of the Bad
  - the plan's room label "WC" (OG NW)
  - the new module `code/gaestebad.py` and the sub-model page `web/gaestebad.html` (export,
    Show, Modell menu, e2e and preview tests)
  - README, CLAUDE.md and the plan sheets
- Out (non-goals):
  - the Bad's outer walls and windows
  - Bad S, WC 2,30 and the OG Flur basin
  - the EG below

## Expected outcome

- The toilet sits at x 0.8145 on the south wall (y 5.46), facing north. Taubenblau tiles cover the
  niche's south, west and partition walls; there are none on its open north side.
- There is no door leaf and no wall between the WC niche and the Bad. A 10 cm partition stands at
  x 1.319–1.419, y 5.46–6.54.
- The shower tray covers x 1.419–2.57, y 5.46–6.85. The glass runs from x 1.92 to 2.57 on y 6.85,
  3–7 cm short of the open leaf (y 6.906). The head sits on the south wall behind the glass.
- The basin (120 × 47, two mixers) is centred at x 1.44 on the north wall, clear of the Flur door's
  leaf. Above it hangs a wood-framed mirror 140 × 95, also centred at x 1.44.
- Limestone covers the whole Bad, the WC niche and the shower, with no oak strip where the old walls stood.
- The OG plan sheet shows one "Bad" region and no "WC" label in the NW.
- `gaestebad.html` is listed in the Modell menu as "Gästebad". It shows the room with its four walls
  and the dimensions WC 101, Dusche 115 × 139, Glas 65, 50 offen, Waschbecken 120, Spiegel 140 × 95
  and Tür 81.
