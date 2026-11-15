---
feature: 33-zwei-duschen
title: "Plan: two showers in the Bad Nadine & Till"
status: applied
order: 4
created: 2026-11-15
edited: 2026-11-15
---
# Plan: two showers in the Bad Nadine & Till

## Steps

- [x] [python] New layout in `elternbad.py`: shower strip along the west wall (two showers, two panes, 60 passage), toilet on the north wall, basin + mirror + lamps on the east wall, nothing on the north wall above 1.20
  - Test first: `tests/test_core.py` › `test_elternbad_layout`, `test_elternbad_submodel` rewritten for the new layout (heads in the SW/NW corners, panes, passage ≥ 60 clear, toilet clearances, leaf clear, north wall top metre free, labels, lamp count) and the OG wall-light count — fail today: old layout
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "elternbad or wall_lights"` → green; Show top-down (page + house) and from the door
  - Applied: the lamp count (69 → 66) also pinned in `test_gltf.py`, `test_tour.py` and `web/src/lighting.test.js` (pool indices: the Elternbad's sites are now 64 .. 66); the "Bäder have no tiles" probe on the Bad S west wall now meets the shower's limestone.
- [x] [python] Rundgang stops in front of the glass, every key in the Bad ≥ 0.25 m from its Parts
  - Test first: `tests/test_tour.py` › `test_route_walks_into_the_elternbad_and_back_out` (stop in front of the glass) and new `test_routes_and_spots_clear_the_elternbad` — fail today: the route ends at x 5.95, through the south pane
  - Verify: `UPDATE_TOUR_GOLDEN=1 .venv/bin/python -m pytest -q tests/test_tour.py` then `.venv/bin/python -m pytest -q tests/test_tour.py` → green
- [x] [web] `web/src/elternbad.js`: header comment and the `door` view's target
  - Test first: none — comment and a view target; `web/e2e/elternbad.spec.js` covers the page
  - Verify: `cd web && npx playwright test elternbad` → green
  - Applied: the spec pinned the old dimension labels; now the new ones.
- [x] [docs] README (component list), CLAUDE.md Elternbad bullet, plan sheets re-exported
  - Test first: none — docs; the plan sheets are pinned by `tests/test_plans.py` (slow)
  - Verify: `python3 code/export_plans.py plans/ && .venv/bin/python -m pytest -q tests/test_plans.py` → green

No `elternbad_v2.svg` drawing: the `*_svg.py` generators are hand-laid per drawing, not cheap to adapt; the sub-model page with its core dimensions (`elternbad.html`, "Von oben") is the drawing.

System docs are updated at `/spec:archive`.
