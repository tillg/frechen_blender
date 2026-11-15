---
feature: 31-fotos-anzeigen
title: "Plan: Vorlagen — the reference photos by place in the house"
status: applied
order: 4
created: 2026-11-15
edited: 2026-11-15
---
# Plan: Vorlagen — the reference photos by place in the house

## Steps

- [x] [python] Manifest `code/vorlagen.py`: every raster image of `input/` in exactly one Bereich, anchors in free air in their room, the issue's examples in place
  - Test first: `tests/test_vorlagen.py` › `test_every_input_image_is_assigned_once`, `test_anchors_in_free_air_in_their_room`, `test_issue_examples` — fail today: no module
  - Verify: `.venv/bin/python -m pytest -q tests/test_vorlagen.py` → green
- [x] [python] Copies: `python3 code/vorlagen.py --copy` writes `web/public/vorlagen/<key>/<file>.jpg` (≤ 1600 px); JSON writer for the pages
  - Test first: `tests/test_vorlagen.py` › `test_every_copy_exists_and_is_small`, `test_json_manifest` — fail today: no copies, no writer
  - Verify: `.venv/bin/python -m pytest -q tests/test_vorlagen.py` → green
- [x] [python] `export_gltf.py`: `scene.extras.vorlagen` (anchored areas) and `vorlagen_walls`; `npm run blueprint` writes `public/vorlagen.json`
  - Test first: `tests/test_gltf.py` › `test_vorlagen_extras` — fails today: no such extras
  - Verify: `.venv/bin/python -m pytest -q tests/test_gltf.py -k vorlagen` → green
- [x] [web] Photo pages `vorlagen.html` (index, `?b=<key>`), helpers in `src/vorlagen-data.js`, build input
  - Test first: `web/src/vorlagen-data.test.js` (area pick, URLs); `web/e2e/vorlagen.spec.js` › "index lists every Bereich", "Garderobe page shows Garderobe and Toilette Mallnitz"; `web/e2e-preview/preview.spec.js` › "Vorlagen page is part of the build" — fail today: no page
  - Verify: `cd web && npx vitest run src/vorlagen-data.test.js && npx playwright test vorlagen preview` → green
  - Applied: the page signals ready by the dev test hook `window.__vorlagen` (as the sub-model pages do), which `shot.js` also waits for; `test_json_manifest` passed at once with step 1's module (the writer came with it), the copies test was seen red.
- [x] [web] Markers in the house viewer (`src/markers.js`, `markerVisible()`), hidden in route / hires / plan; link "Fotos & Vorlagen" on the house page
  - Test first: `web/src/markers.test.js` › visibility rule; `web/e2e/vorlagen.spec.js` › "Stube marker opens the Stube page", "markers hide in the Rundgang" — fail today: no markers
  - Verify: `cd web && npx vitest run src/markers.test.js && npx playwright test vorlagen` → green; Show: Stube and Garderobe at eye height, screenshots read at 1×
- [x] [docs] README (German): section "Fotos & Vorlagen", component list / script table; CLAUDE.md module list
  - Test first: none — docs
  - Verify: `grep -q "Fotos & Vorlagen" README.md && grep -q "vorlagen.py" CLAUDE.md`

System docs are updated at `/spec:archive`.
