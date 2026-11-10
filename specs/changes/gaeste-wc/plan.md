---
feature: gaeste-wc
title: "Plan: Gäste-WC und Garderobe am Hintereingang"
status: applied
order: 4
created: 2026-11-10
edited: 2026-11-10
---
# Plan: Gäste-WC und Garderobe am Hintereingang

Baseline: `check.sh full` and the camera clearance pass before step 1 (frame 3953 is a known bug).

## Steps

- [x] [python] `gaeste_wc.py` + `build_gaeste_wc()`: partition, north wall with the new WC door
  (outward, 90°) and the open Garderobe passage, toilet centred, WC tiles, Flur basin with tiles and
  framed mirror, Garderobe bench / hook board / hooks / hat shelf, dimension lines; built into the
  house at `WC_AT` instead of the old north wall, WC toilet and WC tiles
  - Test first: `tests/test_core.py` › `test_gaeste_wc_submodel` (the drawing's numbers: 101/10/94,
    17/76, axis 50/50, 40 (drawing 41: the model's toilet 1 cm deeper) / 59 / 83 free, basin 14/40/14 at 85, tiles to ≈112 behind it only on
    the 69 wall piece, mirror 54 × 74 from 120, bench 35 × 110 at 45, hooks 165, shelf 185; WC leaf
    in `LEAVES` opening into the Flur; no slab under the partition) and
    `test_gaeste_wc_in_house` (every part of the sub-model is in the house, shifted by `WC_AT`); the
    pinned `WCS` entry for the back-hall WC changes to the new WC (0.31–1.319, door 0.48–1.24),
    assertions unchanged — fails today: no module
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "gaeste or wcs"` → green, then
    `bash scripts/check.sh quick`; Show `EG_Sanitaer` from above
- [x] [python] glTF export `--gaeste-wc` and `show.py --page gaeste_wc`
  - Test first: `tests/test_gltf.py` › `test_gaeste_wc_export` (node names, dims, no tour);
    `tests/test_show.py` › page `gaeste_wc` — fails today: unknown flag / page
  - Verify: `.venv/bin/python -m pytest -q tests/test_gltf.py tests/test_show.py` → green
- [x] [web] Page `gaeste_wc.html` (submodel.js) in the "Teilmodell" drop-down, `shot.js` hook
  - Test first: `web/e2e/gaeste_wc.spec.js` › page draws with the core dimensions, no errors; the
    drop-down lists in `kueche.spec.js` / `preview.spec.js` gain "Gäste-WC" — fails today: no page
  - Verify: `cd web && npx playwright test e2e/gaeste_wc.spec.js` → green; screenshots read at 1×
- [x] [blender] Rebuild, save, still of WC/Garderobe/basin; camera clearance along the Rundgang;
  parity golden regenerated (`UPDATE_GOLDEN=1`)
  - Test first: clearance pass headless (MCP not connected; BVH `find_nearest` ≥ 0.25 m, `ray_cast`
    between frames) — must show no new grazing frames against the baseline
  - Verify: stills `tmp/details/gaeste_wc_*.png` read; `pytest tests/test_blender_parity.py` green
- [x] [docs] README (Teilmodell, `--page`), `CLAUDE.md`, `project.md`
  - Test first: none — docs
  - Verify: `grep -n "gaeste_wc" README.md CLAUDE.md .claude/skills/spec/reference/project.md`

Added on request (2026-11-10, mid-apply): the three doors of the back hall swing at random.

- [x] [python] `SWING` registry → `Blueprint.swing` → glTF `extras.swing`; Hintertür, WC door and
  Windfang door as objects of their own with `PIVOT` at the hinge; back door and Windfang door
  built by `gaeste_wc_neu` (so the sub-model has all three)
  - Test first: `tests/test_core.py` › `test_gaeste_wc_doors_swing` (angles, pivots, the other
    state lies in the lining / in the Flur clear of the jamb); `test_gltf.py` › swing extras —
    fails today: no `swing`. `test_back_windfang_door_glazed_like_the_front_one` reads the leaf
    from its new object `EG_Windfangtuer` (assertions unchanged)
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_gltf.py -k "gaeste or windfang or back_door"`
- [x] [web] `slides.js` `swingingNodes` (every 3 s one random door, 3 s per swing), in `submodel.js`
  and `main.js` (Eingerichtet, not in the Rundgang); the film keeps them as built
  - Test first: `web/src/slides.test.js` › swingingNodes; `web/e2e/gaeste_wc.spec.js` › doors swing
    on the page and in the house, not in the Rundgang — fails today: no `swingingNodes` / `doors` hook
  - Verify: `cd web && npx vitest run src/slides.test.js && npx playwright test e2e/gaeste_wc.spec.js --project dev`

- [x] [python] Hintertür hinged on the south jamb (request 2026-11-10): lock and levers on the north
  side, `SWING` −90° (opens into the Flur beside the Windfang door's open leaf)
  - Test first: `test_back_door_has_lever_handles_inside_and_outside` (lock north),
    `test_gaeste_wc_doors_swing` / `test_gaeste_wc_export` (−90°, clear of the south jamb) — failed
    before the flip
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_gltf.py -k "gaeste or back_door"`;
    golden regenerated, `.blend` rebuilt; `check.sh full` green
- [x] [python] Hintertür and Windfang door both hinged north (request 2026-11-10, replaces the step
  above): open, they lie along the back hall's north wall; `SWING` +90° each
  - Test first: lever test (lock south again), `test_gaeste_wc_doors_swing` (+90°, the open
    Windfang leaf in front of the north wall), `test_gaeste_wc_export` — failed before the change
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_gltf.py -k "gaeste or back_door or windfang"`;
    golden regenerated, `.blend` rebuilt, film camera clearance unchanged; `check.sh full` green

System docs are updated at `/spec:archive`.
