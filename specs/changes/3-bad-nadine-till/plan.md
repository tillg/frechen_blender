---
feature: 3-bad-nadine-till
title: "Plan: Bad Nadine & Till"
status: applying
order: 4
created: 2026-11-13
edited: 2026-11-13
---
# Plan: Bad Nadine & Till

## Steps

- [x] [python] New `code/elternbad.py` with the layout; `build_og()`, `build_sanitary()` and `BATHS_OG` use it
  - Test first: `tests/test_core.py` › `test_elternbad_layout` — door opening 0.65..1.58 in the
    wall x 8.59..8.72, old span 1.65..2.58 is wall; leaf (LEAVES) at 90° clear of every lamp part, the
    window reveal, toilet, basin; toilet faces south at x 8.14 on the north wall tiles; shower tray
    5.59..7.72 × 1.64..2.62, glass on its south edge 6.19..7.72 and its east edge, open 5.59..6.19;
    tiles on the north wall 7.72..8.59 and the east wall 1.66..2.62, none in the shower; basin and
    wood mirror (110 × 85, frame 10, UK 1.17) on axis 6.19; six Wandlampen where the proposal puts
    them — fails today: no `elternbad` module
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k elternbad` → green; Show from top
- [x] [python] Deliberate updates of tests pinning the old Bad S and 29 lamps
  - Test first: existing `test_waschbecken_og_baeder` (basin axis 6.14 → 6.19, plain mirror → wood
    110, shower box), lamp counts 29 → 35 in `test_core.py` (line 29, `test_wandlampen_og_placements`
    gets the Elternbad's six and matches positions within 1.5 mm: lamps at half mm round either way),
    `test_gltf.py`, `test_tour.py`, `web/src/lighting.test.js` (count; nearest sites from the outside camera now
    include the Elternbad's south-wall lamps; the Elternbad is built last so the other lamps keep their
    indices); with the user's OK (2026-11-13) the two #19 leftovers `e2e/gaestebad.spec.js` ('140 × 95' →
    '140 × 85') and `e2e/stages.spec.js` (hires light count) — fail after step 1 for exactly these numbers
  - Verify: `bash scripts/check.sh quick` → green
- [x] [python] Sub-model: `house_core.build_elternbad()`, `export_gltf.py --elternbad`, `show.py --page elternbad`
  - Test first: `tests/test_core.py` › `test_elternbad_submodel` (collection `Elternbad` at the origin,
    wall pieces, dims, every fixture where the house has it shifted by `ELTERNBAD_AT`, 6 wall lights);
    `tests/test_gltf.py` › `test_elternbad_export`; `tests/test_show.py` › `test_elternbad_page` —
    fail today: no `build_elternbad`
  - Verify: `.venv/bin/python -m pytest -q tests -k elternbad` → green
- [x] [web] Page `web/elternbad.html` (+ `src/elternbad.js`, toolbar, vite input, `blueprint` script, `shot.js`, `.gitignore`)
  - Test first: `web/e2e/elternbad.spec.js` (page renders, edges > 50, both looks); page lists in
    `nav.spec.js`, `kueche.spec.js`, `shot.spec.js`, `e2e-preview/preview.spec.js` get the page —
    fail today: no page
  - Verify: `cd web && npx playwright test e2e/elternbad.spec.js` → green; screenshot read at 1×
- [x] [web] Modell drop-down: sub-models grouped by storey (user request 2026-11-13)
  - Test first: `web/e2e/nav.spec.js` › "Modell lists the house entries, a separator, then the sub-models
    by storey" — headings `Erdgeschoss` (Ofen … Schrank im Büro) and `1. Stock` (Schrankbett, Gästebad,
    Bad Nadine & Till); fails today: no headings
  - Verify: `cd web && npx playwright test e2e/nav.spec.js e2e/kueche.spec.js --project=dev` → green; screenshot of the open list read
- [x] [python] Rundgang: walks into the Bad (user request 2026-11-13)
  - Test first: `tests/test_tour.py` › `test_route_walks_into_the_elternbad_and_back_out` — the route
    enters through the new door, walks to the back (west) wall, turns right (via north: shower, toilet)
    until its back is to that wall, holds ≥ PAUSE facing east there, then walks straight out through the
    door; no frame at the old door; fails today: the route only peeks in at y 2.12
  - Verify: `UPDATE_TOUR_GOLDEN=1 .venv/bin/python -m pytest -q tests/test_tour.py` once, then
    `.venv/bin/python -m pytest -q tests/test_tour.py` → green; `@eye`-style still of the peek read
- [x] [python] Shower walls in limestone like the Bad Großeltern's (user request 2026-11-13)
  - Test first: `test_elternbad_layout` gets limestone slabs on the shower's west and north walls from the
    tray (0.045) to 2.0, none outside the glass or past the tray, the riser on the slabs' face — fails
    today: plain plaster. `bad.stone()`'s slab layout moves into `house_core.limestone()` (refactor:
    `build_bad()` and the house's EG geometry fingerprint identical before and after)
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k elternbad` + `check.sh quick` → green; screenshot
- [x] [docs] README (component list, script table, sub-model page, `--elternbad`, `--page`), CLAUDE.md (module list), `project.md` page list
  - Test first: none — docs
  - Verify: `grep -c elternbad README.md CLAUDE.md .claude/skills/spec/reference/project.md` → each ≥ 1
- [x] [python] Walk-in shower on the room's limestone floor, no tray (user request 2026-11-13)
  - Test first: `test_elternbad_layout`: no Keramik tray, `_floor_at` Kalkstein under the shower, one drain on
    the floor (zo + 0.018), glass and cladding from the floor — failed with the tray; `shower(tray=False)`
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "elternbad or gaestebad"` → green
- [ ] [blender] Rebuild, save, parity golden, plan sheets
  - Test first: `tests/test_blender_parity.py` fails on the changed Bad (slow)
  - Verify: rebuild via MCP in order + save; `UPDATE_GOLDEN=1 .venv/bin/python -m pytest -q tests/test_blender_parity.py`,
    diff read; `python3 code/export_plans.py plans/`; film camera clearance check; a still of the Bad
    to `tmp/details/` read; `bash scripts/check.sh full` → green

System docs are updated at `/spec:archive`.

## Resume here (paused 2026-11-13, user away)

Done, committed and merged to `main` (for the website) on the user's request; branch `issue/3-bad-nadine-till`
kept, issue #3 stays open. Steps 1–8 done; a headless rebuild + save of `frechenlehen.blend`, the parity golden
and `plans/` are current (quick check, `test_plans`, `test_blender_parity` green). Next:

1. Film camera clearance check of the route through the Bad (BVH `find_nearest` ≥ 0.25 m + `ray_cast` between
   frames) in Blender, a still of the Bad to `tmp/details/`; then tick the `[blender]` step.
2. `bash scripts/check.sh full` (baseline had 5 #19 leftovers: parity, plans, gaestebad label, hires light
   count — all addressed here — and the tour frame-rate test, 10.9 fps, environment-dependent).
3. `/spec:adversarial-code-review`, fixes on the branch, then PR `Closes #3` → `[under review]`, archive.
