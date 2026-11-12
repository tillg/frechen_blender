---
feature: waschbecken
title: "Plan: Waschbecken on a chrome stand in all six places"
status: applied
order: 4
created: 2026-11-12
edited: 2026-11-12
---
# Plan: Waschbecken on a chrome stand in all six places

The per-step check (`project.md`) runs after every step: the step's own test alone,
`bash scripts/check.sh quick`, and a Show for a visible step. Tests are `.venv/bin/python -m
pytest`. The rewrites of existing test assertions named below were agreed on 2026-11-12. A shared
test helper `_waschbecken(key, region)` in `tests/test_core.py` collects one site's Keramik and
Metall Parts. Each site test asserts:

- the outer size;
- top 85 cm, height 17 cm;
- the hollow bowl: the material at the bowl's centre 5 cm under the top is None, and ≥ 5 Keramik
  Parts;
- the mixer count;
- one drain;
- two Metall legs reaching the floor (+ 0.02) at the front corners;
- a Metall rail at 0.52 between them;
- side rails ending at the wall face;
- a trap below the drain;
- clearance: no basin or Ständer Part's box intersects a door leaf of its storey (`Blueprint.doors`
  `leaf`, and for the back hall also each swinging leaf in its other state), a toilet, a shower
  tray or a window reveal.

## Steps

- [x] [python] Add `waschbecken()` (basin, Ständer, mixers, trap; own `random.Random(16)`) and use it for the OG WC: 50 × 40 einzeln on the east wall at (9.92, 4.95), `tile=WC_TILE_T`; split the black-frame mirror into `wc_mirror()` (unchanged look); `wc_basin()` stays until step 5 (the Gäste-WC still calls it)
  - Test first: `tests/test_core.py` › `test_waschbecken_og_wc` (helper + the assertions above: 50 × 40, one mixer, clear of the door leaf at 90° and the toilet). It fails today: the hand basin is 40 × 28 and overlaps the door leaf (y 5.226…5.4). Rewrite the leg and frame assertions of `test_wc_fixtures_after_the_photo` for the new leg positions (u = ±0.20, v = 0.35) and the mirror frame moved with the basin to y 4.95; it fails today for the old positions
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "waschbecken_og_wc or wc_fixtures"` → green. Show `OG_Sanitaer --at 9.7,4.95,3.5`, shot read at 1×: rectangular basin, chrome legs, rail, balls and trap visible and bright (not black). If chrome renders dark, switch the Ständer to `Stahl` and record it in architecture.md's Key decisions
- [x] [python] OG Bäder: 120 doppelt on Bad NW's north wall (centre x 0.96, y 8.57) and 100 doppelt on Bad S's south wall (centre x 6.14, y 0.40), each with a plain mirror as wide as the basin (`bad_mirror()`); remove `basin()`
  - Test first: `tests/test_core.py` › `test_waschbecken_og_baeder`: sizes, two mixers at u = ±w/4, one drain in the centre, mirror width = basin width, Bad S basin and mirror ≤ 6.84 − 0.15 (window jamb), clear of the door leaves and the showers. It fails today: the basins are 62 × 48 with one tap
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k waschbecken_og_baeder` → green; Show both Bäder (`--at`), read at 1×
- [x] [python] OG Flur: 60 × 47 einzeln at (6.45, 6.35) with `tile=0.02`, in front of the 2 cm slate panel; `flur_sink()` → `flur_panel()` (slate only)
  - Test first: rewrite the sink assertions of `test_og_flur_waschbecken_right_of_the_waschkueche_door` (keep the slate asserts) to the helper's: 60 × 47, top 85, one mixer, on the Ständer. It fails today: the deep trough (≥ 25 cm deep, top 86) has no legs
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k og_flur_waschbecken` → green, including a new assertion that no basin Part reaches y < 6.37 (the panel's face); Show the Flur basin, read at 1×
- [x] [python] Bad Großeltern: 100 × 47 doppelt on the low wall's east face, centred on it, with `rng=random.Random(rng.random())`; `TROG` becomes the basin's (depth 0.47, width 1.00, top 0.85); dimension label "Waschbecken 100"; `web/src/bad.js` header comment "Waschtrog" → "Waschbecken"; the label in `web/e2e/bad.spec.js` and `web/e2e-preview/preview.spec.js` (agreed 2026-11-12)
  - Test first: rewrite the "Waschtrog" block of the Bad Großeltern test in `tests/test_core.py` for the double: x from the wall face + 0.47, y 2.367…3.367, top 0.85, two mixers, one bowl, Ständer to the floor, label "Waschbecken 100" in `build_bad().dims`, the Durchgang dimension unchanged. It fails today: depth 0.50, no legs, label "Waschtrog 100"
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "bad" tests/test_gltf.py` → green; `cd web && npx playwright test e2e/bad.spec.js` → green; Show `--page bad` and the house's Bad, read at 1×
- [x] [python] Back hall: the basin via `hc.waschbecken(..., BW, BD, 1, tile=hc.WC_TILE_T)` with `BW, BD = 0.40, 0.28` unchanged ("as small as possible"); mirror, tiles and dims labels unchanged; then delete `wc_basin()` (no caller left)
  - Test first: in the Gäste-WC test, keep the sizes (14 / 40 / 14, top 85, 83 from the hinge jamb). Add the shape assertions from the helper (hollow bowl, one mixer, one drain, Ständer legs on the floor, rail, side rails to the wall, trap). Add clearance: clear of all three swinging leaves in both states (`SWING`) and of the Windfang leaf's sweep, and ≥ 0.64 m free from x 1.419 (the Garderobe passage's west jamb) to the basin's front. It fails today: the old bowl has no rail at 0.52 and no side rails to the wall. `grep -n "def wc_basin\|def basin(" code/house_core.py` must find nothing
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "gaeste_wc or waschbecken"` → green and the grep is empty; `cd web && npx playwright test e2e/gaeste_wc.spec.js` → green (labels unchanged); Show `--page gaeste_wc`, read at 1×
- [x] [python] Keramik bright neutral white: `MAT_DEF["Keramik"]` rgba (0.90, 0.90, 0.88) → (0.95, 0.95, 0.95) (user, 2026-11-12: the basins looked beige; mostly the warm room light, which stays). All ceramic changes with it: basins, toilets, shower trays
  - Test first: `tests/test_core.py` › `test_keramik_bright_white`: Keramik's rgb is neutral (r = g = b) and ≥ 0.95. It fails today: (0.90, 0.90, 0.88)
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k keramik` → green; Show the Bad page and the house's Bad (same views as step 4), read at 1×: the basin white, not beige, on the page
- [x] [python] Regenerate the plan sheets: `python3 code/export_plans.py plans/`
  - Test first: existing `tests/test_plans.py` (slow); it fails now: the sheets are out of date after steps 1–5
  - Verify: `.venv/bin/python -m pytest -q tests/test_plans.py` → green; `og.svg`/`eg.svg` rendered with `rsvg-convert` and read at the six sites: rectangular basin outlines
- [x] [docs] README (German):
  - in the component list, the Bäder, the WCs' "Waschbecken auf verchromten Konsolenbeinen" and the Flur's "tiefes Keramikbecken" become the Waschbecken einzeln/doppelt on the Waschbeckenständer, with the sizes;
  - in the `bad.py` row, the Waschtrog becomes the Doppelwaschbecken 100;
  - in the `gaeste_wc.py` row, the Handwaschbecken 40/28 stands on the Waschbeckenständer;
  - the sub-model texts at lines ~110/121;
  - `CLAUDE.md`: the `bad.py` and `gaeste_wc.py` bullets (Waschtrog, `wc_basin(mirror=False)`) name `waschbecken()`.
  - Test first: none, docs only
  - Verify: `grep -c "Waschbeckenständer" README.md` ≥ 1 and `grep -n "Waschtrog\|Konsolenbeinen\|tiefes Keramikbecken\|wc_basin" README.md CLAUDE.md` → no match
- [x] [blender] Rebuild in Blender (`build_house`, `fire`, `paint`, `windrose`, `garden`, `film`), save `.blend`, regenerate the parity golden; camera clearance for all routes and inside Standpunkte
  - Test first: `tests/test_blender_parity.py` (slow); it fails now: golden and `.blend` are out of date. Clearance check: every frame of every route and every inside Standpunkt BVH `find_nearest` ≥ 0.25 m plus `ray_cast` between consecutive frames, run via MCP
  - Verify: `UPDATE_GOLDEN=1 .venv/bin/python -m pytest -q tests/test_blender_parity.py`. Then diff the golden: geometry changes only in `*_Sanitaer` and `EG_Bodenbelag` (plank splits, measured), plus `rnd` hashes of later global-stream objects. Then `.venv/bin/python -m pytest -q tests/test_blender_parity.py` → green. Stills in `tmp/details/` of Bad Großeltern, the back hall and OG Bad NW, read: chrome Ständer, rectangular basins. The clearance check reports no frame < 0.25 m
After the last step, the final check (`project.md`): `bash scripts/check.sh full` → green.

System docs are updated at `/spec:archive`.
