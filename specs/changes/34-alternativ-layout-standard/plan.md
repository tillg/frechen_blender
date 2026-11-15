---
feature: 34-alternativ-layout-standard
title: "Plan: Alternativ becomes the EG layout"
status: applied
order: 4
created: 2026-11-15
edited: 2026-11-15
---
# Plan: Alternativ becomes the EG layout

## Steps

- [x] [python] One EG layout in the core: drop C, stub, sliding leaf, lamps 11/12, `VARIANT`,
  `WALL_LIGHT_VARIANT`, `default_layout()`; rename the Alternativ objects; lamps 13/14 into
  `EG_Wandlampen`; consumers (`kueche.py`, `export_gltf.py`, `export_plans.py`, `show.py`,
  dormant `build_house.py`/`film.py`) and the Python tests ported; plan sheets regenerated
  - Test first: `tests/test_core.py` › `test_one_eg_layout` (no removed object, the new names, no
    `variant` field) and the ported `test_wandlampen_eg_placements` / `test_eg_lamps_clear` — fail
    today: the default objects and `EG_Alt_*` exist
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_gltf.py tests/test_show.py tests/test_tour.py` → green; `python3 code/export_plans.py plans/`
- [x] [web] Viewer without the switch: no `eg_alt` entry, no `?layout`, no layout filter in
  visibility / ink / lights, saloon leaves on their own clock by name; `film.mjs` without
  `FILM_LAYOUT`; `variant.spec.js` removed, other specs ported
  - Test first: `web/src/lighting.test.js` (69 lights, all lit at dusk, no `setLayout`),
    `web/src/slides.test.js` (saloon leaves by name), `web/e2e/nav.spec.js` (Modell list without
    "Erdgeschoss - Alternativ") — fail today
  - Verify: `cd web && npx vitest run src/lighting.test.js src/slides.test.js && npx playwright test e2e/nav.spec.js e2e/kueche.spec.js e2e/gaeste_wc.spec.js e2e/stages.spec.js` → green
- [x] [docs] README, CLAUDE.md, `project.md` grill seed without the variant
  - Test first: none — docs only
  - Verify: `git grep -n -E "eg_alt|layout=alt|FILM_LAYOUT|default_layout|EG_Alt_" -- README.md CLAUDE.md code web/src web/e2e web/film.mjs justfile .claude/skills/spec/reference` → no match

System docs are updated at `/spec:archive`.
