---
feature: 7-schrankbett
title: "Plan: Schrankbett im Yoga-Zimmer"
status: applied
order: 4
created: 2026-11-13
edited: 2026-11-13
---
# Plan: Schrankbett im Yoga-Zimmer

## Steps

- [x] [python] `code/schrankbett.py` + `house_core.build_schrankbett()`: carcass, side cabinets,
  Blende, folding bed with `PIVOT` + `CRANK`, walls, dims; own `random.Random`
  - Test first: `tests/test_core.py` › `test_schrankbett_submodel` (objects present; unit 45 deep,
    up to the ceiling; lying area 2.00 × 2.00; bed `CRANK` = 90° about x) and
    `test_schrankbett_fold_clears` (sweep the bed's vertices about `PIVOT` 0 → 90° in 5° steps:
    never behind the wall, under the floor, into the Blende or above the ceiling; at 90° inside the
    niche) — fail today: no module
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k schrankbett` → green
- [x] [python] House: the Yoga `bed()` replaced by `schrankbett_neu("OG", *SCHRANKBETT_AT, Z_OG)`;
  `OG_Klappbett` in `FURNITURE`
  - Test first: `tests/test_core.py` › `test_schrankbett_built_into_the_house` (no Yoga bed at
    y 8.862 … 10.85; unit between west wall and door casing; no clash with the Yoga door leaf in
    `LEAVES`; bed down inside the room) — fails today: old bed still there
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k schrankbett` → green; Show
    `code/show.py OG_Klappbett OG_Moebel`
- [x] [docs] Drawing from the core's numbers (Till: "bau es jetzt", 2026-11-13 — built first, the
  drawing documents it): `input/2026-11-13 input/schrankbett_svg.py` → `schrankbett_v1.svg` (plan,
  front folded up, section with the fold arc, dimensions)
  - Test first: none — a drawing for Till; the sweep is proven by `test_schrankbett_fold_clears`
  - Verify: `test -f "input/2026-11-13 input/schrankbett_v1.svg"`, read it rendered
- [x] [python] `export_gltf.py --schrankbett` (extras.crank on the bed node), `show.py --page schrankbett`
  - Test first: `tests/test_gltf.py` › `test_schrankbett_glb` and `tests/test_show.py` › schrankbett
    page case — fail today: unknown flag / page
  - Verify: `.venv/bin/python -m pytest -q tests/test_gltf.py tests/test_show.py -k schrankbett` → green
- [x] [web] Page `schrankbett.html` + `src/schrankbett.js` (views Schräg / Von vorn / Von oben, hook
  `__schrankbett`), vite input, `package.json` blueprint, toolbar Modell entry, `shot.js`
  - Test first: `web/e2e/schrankbett.spec.js` › "the bed folds up and back" (page loads, the bed node
    turns to 90° and back) — fails today: no page
  - Verify: `cd web && npx playwright test e2e/schrankbett.spec.js` → green; screenshots at 1×
    (folded up: closed Schrankwand; down: bed)
- [x] [web] Modell drop-down and preview build cover the new page
  - Test first: `web/e2e/nav.spec.js` (entry list) and `web/e2e-preview/preview.spec.js` (page loads
    under `/frechen_blender/`) extended — fail today: entry missing
  - Verify: `cd web && npx playwright test e2e/nav.spec.js e2e-preview/preview.spec.js` → green
- [x] [python] + [web] Request 2026-11-13 (Till, after seeing it): the feet fold in as the bed goes up
  (`<c>_Klappfuesse`, same `PIVOT`/`CRANK`, `FOLD` −90° about their hinge → `Blueprint.fold` →
  `extras.fold`, `slides.js` `liftingNodes` folds them in the turning frame); the underside gets a frame
  with six raised panels like the doors
  - Test first: `web/src/slides.test.js` › "a node with extras.fold also folds about its own hinge";
    `tests/test_core.py` schrankbett tests (feet object, `FOLD`, ≥ 14 underside parts, feet folded up
    stand out ≤ 3 cm); `tests/test_gltf.py` › `test_schrankbett_export` (`extras.fold`) — failed: no fold
  - Verify: `bash scripts/check.sh quick`, `npx playwright test e2e/schrankbett.spec.js` → green;
    screenshot folded up: closed front with six panels
- [x] [blender] `build_house.py`, `garden.py` reload `schrankbett`; rebuild, save, parity golden
  (`UPDATE_GOLDEN=1`, diff: new objects + shifted `rnd`), tour clearance
  - Test first: clearance check via MCP (every Rundgang frame: BVH `find_nearest` ≥ 0.25 m, `ray_cast`
    between frames) — the unit is new geometry next to the route
  - Verify: still from a temporary camera in the Yoga room to `tmp/details/schrankbett.png` (bed down,
    side cabinets, Blende); `.venv/bin/python -m pytest -q tests/test_blender_parity.py` → green
- [x] [python] Plan sheets re-exported
  - Test first: `tests/test_plans.py` fails after the core change (sheets out of date)
  - Verify: `python3 code/export_plans.py plans/` then `.venv/bin/python -m pytest -q tests/test_plans.py` → green
- [x] [docs] README (component list, script table, Modell entry), CLAUDE.md, `project.md` `--page` list
  - Test first: none — docs
  - Verify: `grep -q schrankbett README.md CLAUDE.md .claude/skills/spec/reference/project.md`

System docs are updated at `/spec:archive`.
