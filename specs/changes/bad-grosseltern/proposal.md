---
feature: bad-grosseltern
title: "Proposal: Bad Großeltern as a sub-model"
status: applied
order: 1
created: 2026-11-08
edited: 2026-11-08
---
# Proposal: Bad Großeltern as a sub-model

## What

The Großeltern's bathroom with its WC and closet niche (EG, NW corner, x 0.31–2.358,
y 8.656–12.473) is rebuilt after the user's sketch `input/2026-11-08 input/plan_grosseltern_bad.jpeg`
and the dimensions given in the session (agreed drawing: `input/2026-11-08 input/grosseltern_v4.svg`). It
becomes a sub-model like the Ofen and the Schreibtisch: its own module `code/bad.py`, its own page
`web/bad.html` with dimension lines (linked from the house, linking back), and the same parts
placed into the house at `BAD_AT`, replacing today's Bad/WC layout there.

The room, from north to south:

- **Walk-in shower** 0.80 m wide in the NW corner (it must stay clear of the north french door,
  which starts at x 1.109), 1.55 m deep, open to the south; rain head on the north wall; shower
  walls clad with the floor's limestone up to 2.0 m, floor flush with the bathroom floor.
- East of it a partition from the north wall: **thin clear glass** 0.35 m, then a **wall 1.20 m
  long, 1.00 m high, 12 cm thick**, with clear glass on it up to the ceiling (like the 35 cm
  strip).
- One large **trough washbasin** (Trog), **1.00 m wide**, white ceramic, wall-hung on the east
  face of that wall, with two deck mixers; no mirror (the glass is above the wall).
- To the south a **niche 1.20 m deep** over the full room width, split by a **12 cm wall** into two
  equal halves (0.964 m each): **WC** (west, the existing Mallnitz-style toilet and green tiles) and
  **Schrank** (east).
- The niche is closed by **two interlocking sliding doors** on two slightly offset tracks: the WC
  leaf (rear track) slides east behind the Schrank leaf, the Schrank leaf (front track) slides west
  in front of the WC leaf, so both are closed or exactly one is open. In the model the **WC leaf
  is open** (slid behind the Schrank leaf), in the house and the sub-model alike. Above the leaves
  a plastered lintel from 2.05 m to the ceiling carries the rail.
- In the Schrank, open and white like the interior doors: at the back a **cabinet 0.60 m deep**
  over the full width with shelves; along the left side (the 12 cm wall) up to it a **hanging
  wardrobe 0.60 m deep** with a rail and a hat shelf.
- Walls in the house: the wall between today's WC and Bad (y 10.10–10.25) and its sliding door go;
  the wall between niche and bedroom (x 2.358–2.657) ends at the niche front (y 9.856), so Bad and
  bedroom are open to each other from the niche to the north wall (the stub by the shaft stays).
- Floor: limestone in the Bad (as in the EG Flur and the OG Bäder); WC and Schrank keep oak.

## Why

The user is designing the grandparents' bathroom and wants to look at it on its own, with
dimensions, the way the Ofen and the desk can be looked at; the house shows the same parts. Today's
Bad Großeltern is a placeholder ("rebuilt later", `BATHS_OG` comment in the core).

## Scope

- In: `code/bad.py` (builders, `BAD_AT`, dims), `house_core.build_bad()`, the wall changes in
  `build_eg()`, removal of today's Bad/WC fixtures in `build_sanitary()` (shower, basin, WC hand
  basin) and of `sliding_door()`, the WC entry in `WCS`, the limestone floor area, glTF `--bad`,
  `web/bad.html` + `bad.js` (via `submodel.js`), link from the house page, tests, README,
  CLAUDE.md.
- Changed existing tests (they pin today's layout; agreed by the user):
  `test_bathrooms_have_limestone_like_the_eg_corridor` (the Bad point becomes limestone),
  the `WCS` table in `tests/test_core.py` (WC Großeltern rectangle and door span) and
  `test_wc_fixtures_after_the_photo` (toilet moves to the niche's middle, the WC hand basin goes).
- Out (non-goals): mirrors, towel rails, lights or room-light changes in the Bad; cabinet doors and
  contents; the Mallnitz photo for anything but the existing WC look; re-rendering the film.

## Expected outcome

- `http://localhost:5377/bad.html` shows the room with dimension lines 80, 35, 120 (100 hoch), 100,
  96.4 / 12 / 96.4, 120 tief, 60, 60; the house page links to it.
- In the house the Großeltern's bedroom opens onto the Bad; the old WC/Bad wall is gone; a still
  from the bedroom shows shower glass, low wall with glass, trough basin, the open WC and the
  closed Schrank door.
- `python3 -m pytest -q` (incl. parity with a regenerated golden), `npm test`, `npx playwright test`
  green; Rundgang camera clearance ≥ 0.25 m.

The user agreed on 2026-11-08 to change the three existing tests listed under Scope.
