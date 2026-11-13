---
feature: 19-wandlampen-og
title: "Proposal: Wandlampen im 1. Stock"
status: applying
order: 1
created: 2026-11-13
edited: 2026-11-13
---
# Proposal: Wandlampen im 1. Stock

## What

A first set of wall lamps (Wandlampen), after `input/2026-11-13 input/wandlampe.png` (issue #19).
The lamp is brass with an opal-glass bell shade. The maker gives: shade Ø 16 cm, height 11 cm,
reach from the wall 21 cm, E27 socket. Every lamp sits on a round brass rosette with a gooseneck
arm and a stepped brass gallery.

29 lamps go into the OG. They replace the abstract fill lights (`ROOM_LIGHTS`) of the rooms they
light: at dusk each lamp's bulb is a warm light, and its shade glows.

| Room | Lamps | Where (wall, between …) |
|---|---|---|
| Gästebad | 4 + 1 | 4 over the mirror; 1 on the west wall, between the small and the big window |
| Flur, basin | 2 | over the mirror |
| Flur | 1 | north wall, between the Yoga and the Jugend door |
| Flur | 2 | north wall, between the Jugend and the Bichlach door (over the stair) |
| Flur | 1 | south wall, between the Schlafzimmer door and the Flur's east end |
| Yoga | 3 | east wall (to the Jugendzimmer), middle; north wall, between the NW corner and the balcony door; south wall, between the open door's end and the SE corner |
| Jugend | 2 | south wall, between the door and the front (east) bunk bed; east wall, between that bed and the north wall |
| Bichlach | 2 | south wall, between the door and the east wall; north wall, between the two balcony doors |
| Schlafzimmer (Nadine & Till) | 3 | south wall, between balcony door and window; east wall, between the two balcony doors; WC's east wall, between the open door's end and the wall corner by the Kaminofen |
| WC (OG) | 2 | over the cistern (south wall); over the mirror (east wall) |
| Waschküche | 5 | 4 over the big table (south wall); 1 on the east wall, between the Flur wall and the washer tower |
| Saschi | 1 | east wall, between the Flur wall and the nightstand |

Mirrors: the Gästebad's mirror becomes 140 × 85 (was 95), and the Flur's 110 × 85 (was 95).
Each keeps its bottom at 1.17, so its top drops 10 cm and leaves room for the lamps.

## Why

The user wants the real lamps they chose instead of invisible fill lights, so that the rooms read
as they will be lit. The OG comes first. The EG, the bedside lamps and Nadine & Till's Bad follow
later.

## Scope

- In:
  - the lamp as a reusable core builder
  - the 29 OG placements
  - the two mirrors shortened
  - the OG fill lights replaced by per-lamp lights in Blender (film) and the viewer (dusk)
  - the Gästebad sub-model showing its five lamps
- Out (non-goals):
  - EG lamps
  - bedside lamps
  - Nadine & Till's Bad, which keeps its fill light
  - switching lamps individually
  - a sub-model page for the lamp alone
  - showing the lamps on the plan sheets: they hang above the OG cut at 1.55 m, so the Grundriss doesn't show them

## Readings of the request (correct me)

| Request | Reading |
|---|---|
| "170 cm" | Height of the wall outlet, i.e. the rosette centre, above the finished floor. Constant `WANDLAMPE_H = 1.70`. |
| "außer denen über einem Spiegel" | All lamps over mirrors share one height, `WANDLAMPE_SPIEGEL_H = 2.10` (rosette centre). This height is set by the OG WC mirror, whose frame top is at 2.05 and is not shortened. The neck then tops out at 2.185, under the 2.20 ceiling. Over the shortened mirrors (top 2.02) the rosette sits 4 cm clear. The shade hangs in front of the mirror's top edge, 5–21 cm off the wall. |
| Gästebad: "eine auf gleicher Höhe" | Same height as the four mirror lamps (2.10), not 1.70. |
| "zwischen A und B" | Centred in the free wall span between A and B. Two lamps in one span split it into thirds. Lamps over a mirror are centred on equal shares of its width. |
| Flur, Yoga–Jugend door | No count is given, so 1 lamp. |
| Yoga, "links von der Balkontüre" | Seen from inside, facing the door: the west side, towards the NW corner. |
| Yoga, "links vom Ende der geöffneten Türe" | The leaf lies open flat against the south wall to x 5.07. Facing it, left is east, so the lamp goes between the leaf's end and the SE corner. |
| "vorne", "Vorderfront", "vordere Hauswand" | The east side of the house: the balconies and the Schlafzimmer's "Balkontüren zur Vorderfront". |
| Jugend, "vorderes Bett" | The east bunk bed. On the west wall the door leaf and the west bunk leave only 6.6 cm. "Hintere Wand" is the north (outside) wall. |
| Bichlach, "die beiden Balkontüren" | The two in the north wall. The third door, in the east wall, is behind the wardrobe corner. |
| Schlafzimmer, "Wandkante zum Kaminofen" | The corner of the WC block (x 10.07, y 3.84), beyond which the Kaminofen stands. The lamp goes on the block's east face, between that corner and the open door's end. |
| Waschküche, "Wand zum Gang" | The north wall. The lamp goes on the east wall, between it and the washer + dryer tower. |

## Expected outcome

- All 29 lamps stand where the table says, each at its height, clear of door leaves, furniture,
  wall openings and the ceiling. A test checks this.
- No OG fill light is left except the one in Bad S. 14 `ROOM_LIGHTS` remain.
- At dusk in the viewer, the lamps near the camera light their rooms (light pool) and their
  shades glow. In the Blender film, every lamp is a small warm light.
- In the Gästebad sub-model page, the lamps hang over the mirror, which now measures 140 × 85.

## Open questions

none
