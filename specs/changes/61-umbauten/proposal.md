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
8. **Ofen** (follow-up 2026-11-27): much narrower, only about 50 cm deep into the Stube: a block 1.20 along the Flur wall, 0.50 deep, the fire door in its front; the bed above stays 70 wide but straight (70 × 190). The long bench stays where it was, 70 cm clear of the fire door.
9. **Essen:** instead of the big blue cabinet C a big wooden Bauernschrank (the OG Flur's, 2.10 × 2.25), in the middle of the west wall; C's dishes go with it, the drywall now runs from the west wall.
10. **Speis door:** a normal panel door instead of the saloon leaves, hinged south, open flat into the Küche.
11. **Schuhregal** in the back hall: 2 m high (nine levels).
12. **Bad Oma & Opa:** the Einbauschrank turned 90°: on the niche's east wall from the south wall to the front wall, its doors towards the WC.
14. **Bauernschränke** (follow-up): freestanding wooden Bauernschränke (the OG Flur's) in place of the built-in wardrobes in Saschi's room, the Schlafzimmer Nadine & Till and the Bichlach (1.40 wide there, north of the balcony door). The Essen's Bauernschrank sits in the middle of its wall; the shoe rack is about half full, shoes spread over all levels.
13. **Flur-Garderobe:** under it a wooden bench after the user's photo (dark plank, green splayed legs); the photo into the Garderobe gallery.

## Why

The family's revised wishes for the rebuild (issue #61).

## Scope

- In: core modules (`house_core`, `kueche`, `bad`, `elternbad`, `waschkueche`, `gaeste_wc`, new `garderobe`), plan sheets, viewer sub-model names/colours, tests, README, CLAUDE.md.
- Out (non-goals): new light over the Halbinsel; the Waschküche door and Wandlampen (`LAMPE_H`) stay as they are; no new sub-model page for the Flur-Garderobe; the dormant Blender backend.

## Expected outcome

Viewer and plan sheets show the seven changes; `check.sh full` green; parts not touched keep their random draws (`rnd`), so nothing else changes look.
