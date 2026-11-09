---
feature: kueche-speis
title: "Plan: Küche as a sub-model, new Speis, sub-model drop-down"
status: applied
order: 4
created: 2026-11-09
edited: 2026-11-09
---
# Plan: Küche as a sub-model, new Speis, sub-model drop-down

Baseline before step 1: `python3 -m pytest -q` (parity included), `cd web && npm test`.

## Steps

- [x] [python] `code/kueche.py`: `KUECHE_AT`, `kueche_neu(c, x0, y0)` (v6 layout, own
  `random.Random`, returns dims); `house_core.build_kueche()`; `build_eg()` calls it instead of
  `kitchen()` (removed)
  - Test first: `tests/test_core.py` › `test_kueche_submodel` — objects `Kueche_Kueche`,
    `Kueche_Herd`, `Kueche_Haube`, `Kueche_Waende`; sink run 7.05–8.555 into the corner, Ostzeile
    front 0.60, Herd 4.30–5.10, Besenschrank 5.492–6.00 × 5.30–5.847 up to 2.20, Abzug from 1.80
    (all as `KUECHE_AT` offsets), house parts = sub-model parts + `KUECHE_AT`, dims labels present
    — fails today: no `kueche` module. Existing kitchen tests updated to v6 positions (agreed).
  - Verify: `python3 -m pytest -q tests/test_core.py` → green
- [x] [python] Kitchen door at its real place; Speis wall, opening and fit-out A/B/C (`speis()`,
  `EG_Speis`), Speis/Essen wall gone, sliding leaf + rail, three Speis shelves gone
  - Test first: `tests/test_core.py` › `test_kuechentuer_as_built`, `test_speis_v6` — Flur wall
    open at x 6.10–6.96 (probed at 6.5) and closed at 7.5; kitchen leaf at 90° east of the Besenschrank, no clash;
    no wall at (4.0, 3.2); wall x 5.24–5.49 from 3.13, open 4.33–5.249; A/B/C extents and heights
    to ≥ 2.39; sliding leaf at x 5.50–5.54, y 3.28–4.28, in `LEAVES` — fails today: old layout
  - Verify: `python3 -m pytest -q` (parity excluded until the Blender step) → green
- [x] [python] Rundgang: look into the Speis aisle through the new opening, walk through the new
  kitchen door
  - Test first: `tests/test_tour.py` golden differs after the route change (seen red), then
    `UPDATE_TOUR_GOLDEN=1`
  - Verify: `python3 -m pytest -q tests/test_tour.py` → green
- [x] [python] `export_gltf.py --kueche` → `web/public/kueche.glb`
  - Test first: `tests/test_gltf.py` › `test_kueche_export` — nodes `Kueche_*`, dims in extras, no
    tour — fails today: no `--kueche`
  - Verify: `python3 -m pytest -q tests/test_gltf.py` → green
- [x] [blender] `reload(kueche)` in the Blender scripts; rebuild all six, save; golden
  - Test first: parity test red after the core change (golden differs)
  - Verify: `UPDATE_GOLDEN=1 python3 -m pytest -q tests/test_blender_parity.py`, review the diff
    (EG objects, rnd hashes), save `.blend`, `python3 -m pytest -q` → green; stills
    `tmp/details/kueche_from_door.png`, `tmp/details/speis_aisle.png`, `tmp/details/speis_from_essen.png`
    read; Rundgang clearance ≥ 0.25 m, 0 ray hits
- [x] [web] `nav.js` drop-down on all pages; `kueche.html` + `kueche.js`; vite input, blueprint
  script, `.gitignore`
  - Test first: `web/e2e/kueche.spec.js` (page draws, labels, no console errors), e2e "drop-down
    reaches every page" on house and a sub-model, preview spec "kueche page is part of the build"
    — fail today: no page/drop-down
  - Verify: `cd web && npm test && npx playwright test` → green; screenshots read at 1×
- [x] [docs] README component list + script table (`kueche.py`, `kueche.html`, drop-down),
  CLAUDE.md sub-model mentions, ADR-001-XEWL module list
  - Test first: none — docs
  - Verify: `grep -n "kueche.py" README.md CLAUDE.md specs/architecture/adr-001-xewl-shared-python-core.md`
    matches in all three

Apply notes (2026-11-09): the web specs could not be seen red first (the dev server on 5377
served another checkout until it was freed). Full run: 57/58; `tour.spec.js` › "at most ~30
frames per second" fails with ~11 fps also on the commit before this change (checked by stashing),
i.e. machine load, not this change.

System docs are updated at `/spec:archive`.
