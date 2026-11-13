---
feature: 18-gaestebad-og
title: "Plan: Gästebad im 1. Stock"
status: applied
order: 4
created: 2026-11-13
edited: 2026-11-13
---
# Plan: Gästebad im 1. Stock

The existing tests that pin the old layout get the new values as each step's Red. They are
replaced, never dropped: the test-side `WCS` entry for WC 2,26, `test_wc_fixtures_after_the_photo`
(toilet), `test_waschbecken_og_baeder` (basin, mirror, shower), and
`test_bathrooms_have_limestone_like_the_eg_corridor` (new sample points).

## Steps

- [x] [python] Partition over the EG one, WC wall and door removed, WC niche open to the north
  - Test first: `tests/test_core.py` › `test_gaestebad_og_walls` asserts three things. An
    `OG_Waende` part fills x 1.319–1.419. No wall part at (1.62, 6.0) or (1.0, 6.49). No OG door
    or leaf there. The test-side `WCS` entry becomes `(0.31, 1.319, 5.46, 6.54), (0.31, 1.319)`.
    Fails today: the partition is at 1.57 and the door leaf exists.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "gaestebad or wcs"` → green
- [x] [python] Toilet centred on the niche's south wall facing north; shower 115 with 65 glass
  - Test first: in `test_wc_fixtures_after_the_photo` the OG toilet becomes `("OG", zo, 0.8145, 5.46, 0, 1)`.
    `test_gaestebad_og_shower` asserts the tray at x 1.419–2.57 and the glass at x 1.92–2.57.
    Fails today: toilet on the west wall, tray 1.67–2.57.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "wc_fixtures or gaestebad"` → green
- [x] [python] Basin centred on the north wall, wood-framed mirror 140 × 95 above it
  - Test first: in `test_waschbecken_og_baeder` the NW basin wall becomes `(1.44, 8.57, 0, -1)`
    (clear of leaves and both showers). For NW it asserts a `Kiefer` frame 1.40 wide centred at
    1.44 and `Spiegel` glass narrower by 2 × 0.10. Bad S keeps its plain mirror. Fails today: basin
    at 0.96 with a plain mirror.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k waschbecken` → green
- [x] [python] Limestone over the whole Gästebad; "WC" label of the OG NW dropped
  - Test first: `test_bathrooms_have_limestone_like_the_eg_corridor` adds (1.0, 6.49), (1.62, 6.0),
    (1.62, 6.49) and (0.8, 6.0) as `Kalkstein`. A new check confirms no two floor pieces overlap in
    the Gästebad. `tests/test_plans.py` › `test_each_plan_room_is_its_own_region` stays as is.
    Fails today: oak under the old walls.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k limestone && .venv/bin/python -m pytest -q tests/test_plans.py -m "not slow"` → green
- [x] [docs] README: Gästebad in the component list (basin centred, wood-framed mirror, WC niche, walk-in shower)
  - Test first: none, docs only
  - Verify: `grep -n "Gästebad" README.md` matches
- [x] [python] Shower longer: tray to y 6.85, glass on its north edge, 3–7 cm short of the open Flur door's leaf (request 2026-11-13)
  - Test first: `test_gaestebad_og_shower` sets the tray to 1.419–2.57 × 5.46–6.85 and the glass on
    y 6.85. A gap of 0.03–0.07 between glass/rail and the leaf from `BP.doors`. Fails today: tray to 6.54.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k gaestebad` → green
- [x] [python] Module `code/gaestebad.py` and sub-model `build_gaestebad()` with walls and dimensions; the house builds from it
  - Test first: `tests/test_core.py` › `test_gaestebad_submodel` asserts three things:
    - collection `Gaestebad` with `_Waende`, `_Sanitaer`, `_Fliesen` and `_Innentueren`
    - the sub's Sanitaer and Fliesen solids, shifted by `GAESTEBAD_AT` and `Z_OG`, are among the house's, and so is its partition
    - the dimension labels WC 101, Dusche 115 × 139, Glas 65, 50 offen, Waschbecken 120,
      Spiegel 140 × 95 and Tür 81

    `tests/test_gltf.py` › `test_gaestebad_export` checks `--gaestebad` (nodes, dims, nothing
    moving). `tests/test_show.py` › `test_gaestebad_page` checks `--page gaestebad` from above.
    Fails today: no module `gaestebad`.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_gltf.py tests/test_show.py -k gaestebad` → green
- [x] [web] Sub-model page `gaestebad.html` (Modell entry "Gästebad"), wired like the Schrankbett
  - Test first: `web/e2e/gaestebad.spec.js` checks the page draws, the dimensions are visible, and the three
    views × looks have ink. Further checks:
    - `nav.spec.js`, `kueche.spec.js` and `shot.spec.js` list the page
    - `preview.spec.js` checks that the page is part of the build

    Fails today: no page.
  - Verify: `cd web && npx playwright test e2e/gaestebad.spec.js --project dev` → green; screenshots of the three
    views and the Show URL read at 1×
- [x] [docs] README (sub-model section, script table, URLs, `--page`), CLAUDE.md (module, sub-model), project.md (`--page`)
  - Test first: none, docs only
  - Verify: `grep -c gaestebad README.md CLAUDE.md` > 0
- [x] [blender] Rebuild, save, regenerate the parity golden and the plan sheets
  - Test first: `tests/test_blender_parity.py` fails on the changed OG objects
  - Verify: rebuild via MCP (headless if it is down), save, `UPDATE_GOLDEN=1 … test_blender_parity.py`,
    diff the golden. Geometry changes are in the OG bath only, plus the random joints and gravel.
    Then `python3 code/export_plans.py plans/`, and render a still of the Gästebad to
    `tmp/details/gaestebad.png` and read it.

System docs are updated at `/spec:archive`.
