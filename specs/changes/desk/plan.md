---
feature: desk
title: "Plan: Desk sub-model with monitors, MacBook, keyboard and trackpad"
status: applied
order: 4
created: 2026-11-06
edited: 2026-11-06
---
# Plan: Desk sub-model with monitors, MacBook, keyboard and trackpad

## Steps

- [x] [python] `code/desk.py`: move `desk()`, add `desk_neu()` (today's table + chair, monitors,
  MacBook, keyboard, trackpad, dims) and `stuhl()`; `house_core.build_desk()`; image
  materials in `MAT_DEF`
  - Test first: `tests/test_core.py` › `test_desk_submodel` (devices on the top, monitors edge to
    edge at 170°, MacBook closed partly under the left one with the logo, panes with pivot/turn and image materials, dims) and
    `test_desk_built_into_the_bibliothek` (EG_Geraete / EG_Bildschirm_* at today's table position, furniture
    stage) — fail today: no `desk` module
  - Verify: `python3 -m pytest -q tests/test_core.py` → green
- [x] [python] `export_gltf.py --desk`; image + size in material extras
  - Test first: `tests/test_gltf.py` › desk export has the pane nodes with translation and image
    extras — fails today: no `--desk`
  - Verify: `python3 -m pytest -q` (without parity) → green
- [x] [blender] image materials in `build_house.make_materials`, `reload(desk)`; rebuild, regen golden
  - Test first: parity test fails after the core change (golden differs)
  - Verify: `UPDATE_GOLDEN=1 python3 -m pytest -q tests/test_blender_parity.py`, rebuild all six,
    save; still `tmp/details/desk.png` shows both screenshots legible, MacBook, keyboard, trackpad;
    camera clearance check ≥ 0.25 m
- [x] [web] `materials.js` image materials; `desk.html` + `desk.js`; link from the house and back
  - Test first: `web/e2e/desk.spec.js` (page draws, dims, screens show the image), preview spec
    "Desk page is part of the build" — fail today: no page
  - Verify: `cd web && npm test && npx playwright test` → green; screenshots read at 1×
- [x] [python] back door lever handles inside and outside (user request in the session)
  - Test first: `tests/test_core.py` › `test_back_door_has_lever_handles_inside_and_outside` — failed: no handles
  - Verify: `python3 -m pytest -q` → green; stills `tmp/details/backdoor_out.png`, `backdoor_in.png`
- [x] [docs] README component list + script table, CLAUDE.md mentions of the sub-models
  - Test first: none — docs
  - Verify: `grep -n desk.py README.md CLAUDE.md`

System docs are updated at `/spec:archive`.
