---
feature: 27-garderobe-jacken
title: "Plan: Garderobe für viele Jacken"
status: proposed
order: 4
created: 2026-11-15
edited: 2026-11-15
---
# Plan: Garderobe für viele Jacken

## Steps

- [ ] [python] Garderobe without bench: hook board over the east wall with 23 hooks in two rows, hat shelf, hanging rod, shoe shelf with two 20 cm levels
  - Test first: `tests/test_core.py` › `test_gaeste_wc_submodel` (bench asserts replaced, as the issue removes the bench) + new `test_garderobe_jacken` — no bench, ≥ 20 hooks in two rows, rod wall to wall at 1.70–1.80, shoe shelf levels 20 cm clear — fails today: bench still there, six hooks, no rod/shelf
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "gaeste_wc or garderobe"` → green
- [ ] [python] Five coats on hangers and 12 shoes in `<c>_Kleidung` (furniture), own `random.Random(27)`, new fabric/shoe materials
  - Test first: `tests/test_core.py` › `test_garderobe_jacken` extended: 5 coats, 12 shoes on the shelf levels, coat hems above the shelf top, no Garderobe/Kleidung part clashes with walls, Wandlampen or the three door leaves (both states), tour keys ≥ 0.25 m; `EG_Kleidung` in `FURNITURE`; object-name sets in `test_gaeste_wc_submodel` and `tests/test_gltf.py` — fails today: no `_Kleidung`
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_gltf.py` → green; other objects' geometry/rnd hashes unchanged
- [ ] [web] Sub-model page: colour for `GaesteWC_Kleidung`, labels without the bench
  - Test first: `web/e2e/gaeste_wc.spec.js` label list (new rod / shoe-shelf labels instead of `Bank 35 × 110`, `59 frei`) — fails today: labels missing
  - Verify: `cd web && npx playwright test e2e/gaeste_wc.spec.js` → green; Show screenshots (sub-model + house at 1.6 m) read at 1×
- [ ] [docs] Plan sheets, README, CLAUDE.md
  - Test first: none — docs/generated; `tests/test_plans.py` checks the sheets
  - Verify: `python3 code/export_plans.py plans/` and `grep -n "Kleiderstange" README.md CLAUDE.md` → matches

System docs are updated at `/spec:archive`.
