---
feature: gaeste-wc
title: "Proposal: Gäste-WC und Garderobe am Hintereingang"
status: applied
order: 1
created: 2026-11-10
edited: 2026-11-10
---
# Proposal: Gäste-WC und Garderobe am Hintereingang

## What

The WC by the back hall (EG, 2.05 × 1.10 m) becomes the agreed variant v3 of
`input/2026-11-10 input/gaeste_wc_v3.svg` (generator `gaeste_wc_svg.py` beside it): a new 10 cm
partition splits it into the **WC** (west, 101) and the **Garderobe** (east, 94). The WC gets a new
door opening (76) in the existing north wall, its leaf opening outward into the Flur, hinged at the
partition side; the toilet stands centred on the south wall, Taubenblau tiles in the WC only. The
Garderobe keeps the old opening (80) without a door and gets a Mallnitz-style bench (35 × 110, wall
to wall) with a hook board, hooks and a hat shelf. A hand basin 40/28 hangs on the Flur east wall,
centred between the WC wall and the Windfang door, Taubenblau tiles behind it and a mirror 40 × 60
in a 7 cm wooden frame above.

Like the Bad Großeltern it is a **sub-model**: `code/gaeste_wc.py`, built into the house and on its
own page `web/gaeste_wc.html` ("Teilmodell" drop-down) with dimension lines.

## Why

The user's chosen plan for the back entrance (2026-11-10). Seeing it in 3D and on its own page with
measurements, like the Bad and the Küche, is how the family decides details.

## Scope

- In: partition, WC door opening + leaf, the north wall (into the sub-model), toilet, WC tiles, Flur
  basin + tiles + framed mirror, Garderobe bench / hook board / hooks / hat shelf, own page with
  dimensions, `show.py --page gaeste_wc`, parity golden and `.blend` rebuilt.
- In (request 2026-11-10, mid-apply): the back hall's three doors (Hintertür, WC door, Windfang
  door) open and close at random in the viewer, to show where they get in each other's way: every
  3 s one door, 3 s per swing; on the sub-model page and in the house (stage Eingerichtet), not in
  the film nor the Rundgang (doors as built). Hintertür and Windfang door move into the sub-model.
- In (request 2026-11-10): Hintertür and Windfang door both hinged north, so that open they lie
  along the back hall's north wall (both open into the back hall).
- Out (non-goals): water pipes, a door to the Garderobe, the floor (stays limestone), the
  Rundgang route (unchanged; only its clearance is checked), re-rendering the film.

## Expected outcome

- The house and the page show v3; the drawing's numbers hold in the model: 101 / 10 / 94, door 76
  (17 from the west wall), toilet axis 50 / 50 with 40 free in front (drawing: 41; the model's toilet seat
  reaches 70 from the wall, the drawing's 69), Garderobe 59 free beside the
  bench, 83 from the WC door's hinge jamb to the basin, basin 14 / 40 / 14 on the 69 wall piece,
  heights 85 (basin) / ≈112 (tiles) / 120–194 (mirror), bench 45, hooks 165, hat shelf 185.
- Tests green (quick and full), the camera still clears all geometry (no new grazing frames).

## Open questions

- Mirror frame 7 cm beside the Windfang door's architrave (gap ≈ 3 mm in the model): kept at 40 cm
  glass as drawn; the drawing's own open question.
