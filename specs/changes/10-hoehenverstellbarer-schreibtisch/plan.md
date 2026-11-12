---
feature: 10-hoehenverstellbarer-schreibtisch
title: "Plan: Höhenverstellbarer Schreibtisch"
status: applying
order: 4
created: 2026-11-12
edited: 2026-11-12
---
# Plan: Höhenverstellbarer Schreibtisch

## Steps

- [x] [python] Cherry top 190 × 100 on the Wien crank frame in `desk.desk_neu()`, with `LIFT`/`CRANK`
  - Test first: `tests/test_core.py` › `test_desk_cherry_top_on_the_crank_frame` — top `Kirschbaum`
    190 × 100, 0.71–0.75 in `Desk_Schreibtisch`; frame `Eisen` in `Desk_Moebel` inside the top's
    footprint and below it; `LIFT` = 0.30 for `Desk_Schreibtisch/_Geraete/_Bildschirm_L/_R`;
    `CRANK` + `PIVOT` for `Desk_Handrad`; dimensions "Tisch 190", "100", "75–105". Plus
    `test_desk_lifted_clears_the_room` (house: the lifted objects at +0.30 overlap no Part of any
    other object) and `test_desk_keeps_the_rnd_stream` (every EG object outside the desk keeps its
    `rnd` list). Adapt `test_desk_sub_model…` (object set, top bbox, "Tisch 190") and
    `test_desk_built_into_the_bibliothek` (`DESK_AT` = (10.943, 11.471)). Fails today: no such
    objects/registries.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k desk` → green
- [x] [python] `export_gltf.py` writes `extras.lift` and `extras.crank`
  - Test first: `tests/test_gltf.py` › desk glb: nodes incl. `Desk_Schreibtisch`, `Desk_Handrad`;
    `extras.lift` = 0.30 on the four lifted nodes; `extras.crank` = glTF axis + 8π on the wheel,
    its translation = the pivot. Fails today: no extras.
  - Verify: `.venv/bin/python -m pytest -q tests/test_gltf.py` → green
- [x] [web] `slides.js` `liftingNodes()`: one clock, 3 s up, 4 s rest, 3 s down; the crank turns with it
  - Test first: `web/src/slides.test.js` › `liftingNodes…` — positions at t = 0/5.5/7/10/14/17,
    all nodes at the same fraction, the wheel's quaternion at its full angle when up. Fails today:
    no export.
  - Verify: `cd web && npx vitest run src/slides.test.js` → green
- [x] [web] Wire the lift into `submodel.js` (lines move/turn) and `main.js` (Eingerichtet, not in the Rundgang, draw-on-demand box); `desk.js` views for the new size
  - Test first: `web/e2e/desk.spec.js` › `the desk cranks up 30 cm and down; the wheel turns` and
    `web/e2e/gaeste_wc.spec.js`-style house case in `desk.spec.js` › `in the house the desk lifts in
    Eingerichtet, not in the Rundgang`; `Tisch 194.8` → `Tisch 190`. Fails today: no `lift` hook.
  - Verify: `cd web && npx playwright test e2e/desk.spec.js` → green; screenshots of the desk low
    and high read at 1×; human check: the user looked at it in the viewer and approved it
    (2026-11-12)
- [x] [blender] Rebuild, regenerate the parity golden, save the `.blend`
  - Test first: Rundgang camera clearance check (BVH `find_nearest` ≥ 0.25 m per frame, `ray_cast`
    between frames) — must stay green; golden diff limited to `EG_Moebel`, `EG_Geraete`,
    `EG_Bildschirm_L/R`, `EG_Stuehle`, new `EG_Schreibtisch`, `EG_Handrad` (+ the material).
  - Verify: `UPDATE_GOLDEN=1 .venv/bin/python -m pytest -q tests/test_blender_parity.py`, `git diff
    --stat tests/golden` as expected; still of the desk to `tmp/details/desk_wien.png` read;
    `python3 code/export_plans.py plans/` → only the „Modellstand“ hash line changes (furniture is
    not drawn); done 2026-11-12: golden diff exactly the 7 objects, Rundgang clearance ≥ 0.251 m
    on all 7597 frames, no ray hits (the reference plan planes `Ref_*` excluded)
- [x] [docs] README: desk.py row, Teilmodell Schreibtisch, house furniture list
  - Test first: none — docs
  - Verify: `grep -n "Kirschbaum" README.md` matches in the three places

System docs are updated at `/spec:archive`.
