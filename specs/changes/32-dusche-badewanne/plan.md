---
feature: 32-dusche-badewanne
title: "Plan: shower and bathtub in the Gästebad"
status: applying
order: 4
created: 2026-11-15
edited: 2026-11-15
---
# Plan: shower and bathtub in the Gästebad

## Steps

- [x] [python] New layout in `gaestebad.py`: shower SW, built-in tub along the west wall under the window, partition to 6.15, WC niche SE, basin + mirror on the north wall, 4 lamps
  - Test first: `tests/test_core.py` › `test_gaestebad_og_walls`, `test_gaestebad_og_shower_and_tub` (was `_og_shower`), new `test_gaestebad_clearances`, `test_gaestebad_submodel` (labels, 4 lamps) and the OG wall-light counts — fail today: old layout
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "gaestebad or wall_lights"` → green; Show top-down (page + house) and from the door at 1.6 m
  - Applied: also rewritten for the new layout: `WCS` (the niche moves SE), `test_wc_fixtures_after_the_photo` (toilet axis), `test_waschbecken_og_baeder` (single 60, mirror 80, clear of shower and tub), `test_wandlampen_over_the_og_mirrors`, `test_wandlampen_og_placements`; the lamp count (66 → 65) in `test_gltf.py`, `test_tour.py`, `web/src/lighting.test.js` (pool indices ≥ 8 shift by one), `web/e2e/stages.spec.js`. Dimension labels moved apart after the first Show.
- [x] [python] Rundgang and Standpunkte keep ≥ 0.25 m from the Gästebad's Parts
  - Test first: none — a guard: the route is unchanged (it peeks in from the Flur at x 2.8), so `tests/test_tour.py` › new `test_routes_and_spots_clear_the_gaestebad` passes on both layouts; it asserts the tub is among its boxes
  - Verify: `.venv/bin/python -m pytest -q tests/test_tour.py` → green
- [x] [web] `web/src/gaestebad.js`: header comment and the `door` view; e2e labels; lamp counts in `lighting.test.js`, `stages.spec.js`
  - Test first: `web/e2e/gaestebad.spec.js` with the new labels — failed on the old core's glb, passes on the new
  - Verify: `cd web && npx playwright test gaestebad && npm test` → green
- [x] [docs] README (component list), CLAUDE.md Gästebad bullet, plan sheets re-exported
  - Test first: none — docs; the plan sheets are pinned by `tests/test_plans.py` (slow)
  - Verify: `python3 code/export_plans.py plans/ && .venv/bin/python -m pytest -q tests/test_plans.py` → green

- [x] [python] The user's addition (run-2026-11-15-1633-17): limestone shower floor (no tray) and walls (west around the small window, south), glass instead of the partition to y 6.24, tub 170, toilet centred between glass and east wall; floor slabs end under the glass; README, CLAUDE.md, web labels, plan sheets follow
  - Test first: `tests/test_core.py` › `test_gaestebad_og_walls` (glass, no partition), `test_gaestebad_og_shower_and_tub` (no tray, limestone floor and walls, window free, tub 170), `test_gaestebad_clearances` (entrance from the glass, toilet centred, tiles), `test_gaestebad_submodel` labels, lamp and basin positions — failed on the first layout (5 red), green after
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "gaestebad or wandlampen or waschbecken or wc_"` → green; `check.sh quick` green; Show again (page top, house top, door at 1.6 m)
  - Applied: the Gästebad leaves `WCS` (three tiled walls no longer: glass on one side), its tiles are checked in `test_gaestebad_clearances`; the floor as one rectangle put the WC 2,30's probe on a joint, so `BATHS_OG` splits at the glass line instead (where the slabs would end anyway).

System docs are updated at `/spec:archive`.
