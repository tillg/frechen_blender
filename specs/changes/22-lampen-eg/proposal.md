---
feature: 22-lampen-eg
title: "Proposal: Lampen im EG"
status: applied
order: 1
created: 2026-11-14
edited: 2026-11-14
---
# Proposal: Lampen im EG

## What

Issue #22: the house's standard Wandlampe (#19: brass gooseneck, opal bell) goes into the EG at the
places the owners listed. The Stube's reading lamp over the Ofen bed becomes a Wandlampe too, and
the Küche's hood gets a strip with 4 built-in spots at its back edge. As in the OG, the lamps replace
the abstract fill lights at dusk.

The placements were agreed on a plan drawing (2026-11-14, user's choices in bold where the text
allowed two readings); it is kept as `input/2026-11-14 input/lampen_eg_v1.svg`, drawn from the core.

| # | Room | Where (wall, between …) |
|---|---|---|
| 1, 2 | Windfang (vorne) | south wall, between the open Windfang door leaf and the front door's leaf as the film opens it (x 13.57, not 13.95 as drawn at first); north wall, between the Bürotür and the NE corner |
| 3–6 | Stube | north wall, between the open door leaf and the east wall; **east pier** of the SE corner between the big windows; west wall over the bench, ⅓ of the way from the Ofen towards the wall's end; over the Ofen bed (replaces the reading lamp, 2.10 high) |
| 7, 8, spots | Küche | over the sink (north wall); over the worktop right of the hood (east wall); 4 spots in a strip at the hood's back edge |
| 10 | Essen | south wall, between the terrace door and the window |
| 11, 12 | Essen, default layout | west wall, between the outer wall and Schrank C |
| 13, 14 | Essen, Alternativ | instead of 11, 12 (C covers the west wall there): on B's wooden back towards the Essen, each centred on a board (x 3.90, 4.72; the thirds fell on board joints) |
| 15–20 | Flur | stair side, between Windfangtür and the stair's foot; between the Bibliothek and the Oma & Opa door; between that and the back Windfang door; 2 on the south wall, between the Küche door and the back Windfang's wall; between the Küche door and the Ofen's back door |
| 21–26 | Bibliothek | 2 on the south wall, between the door to the Windfang and the stub behind the Werkstattofen; left of the door to the Flur; **2 on the west wall** (the back wall, the vitrine's corner behind the piano); north wall, between the window and the fireplace stub |
| 27–31 | Oma & Opa | on the stub right of the entrance door (its east face); north wall, between balcony door and the stub; Bad: west wall, between the limestone shower wall and the sliding doors; WC: over the cistern; Schrank: its right wall, in front of the shelves |
| 32–36 | Hinterer Windfang | over the mirror; **2 on the Garderobe's partition** opposite the hooks; Gäste-WC over the cistern; west wall, between back door and WC door |

Height: rosette centre at `WANDLAMPE_H` (1.70), over the mirror and the Ofen bed 2.10.

## Why

The owners want the lamps they chose, so the EG reads as it will be lit (the OG got them in #19).

## Scope

- In: the 35 Wandlampen (33 per layout), the Ofen bed lamp replaced, the hood's spot strip; layout
  tags for the lamps and their lights (11, 12 default only, 13, 14 Alternativ only); the EG's fill
  lights removed except the Speis's, and the OG Bad Nadine & Till's leftover fill light (#3 forgot it);
  Blender (film lights), viewer (dusk), Ofen sub-model page.
- Out (non-goals): pendant lamps ("Hängelampen machen wir nachher"), switching lamps, the lamps on the
  Grundriss sheets (`PLAN["skip_words"]`; in the Ansichten they show through the openings like the OG's and
  the other fixtures).

## Expected outcome

- Every lamp at its drawn place on solid wall, clear of door leaves, furniture and fixtures; the
  Rundgang and the Standpunkte ≥ 0.25 m from every lamp.
- At dusk the EG is lit by its lamps (and the Speis by its fill light); in the Alternativ layout the
  Essen's lamps follow the layout, lights included.
- The Ofen page and the house show the Wandlampe over the bed instead of the old reading lamp.

## Open questions

none
