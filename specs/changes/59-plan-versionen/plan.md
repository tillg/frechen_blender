---
feature: 59-plan-versionen
title: "Plan: Planversionen im Viewer"
status: applied
order: 4
created: 2026-11-25
edited: 2026-11-25
---
# Plan: Planversionen im Viewer

## Steps

- [x] [python] `code/versionen.py freeze <name> [--id]`: snapshot `git archive HEAD code plans` to
  `versionen/<id>.tar.gz`, entry in `versionen/versionen.json`; refuses a dirty `code/`/`plans/` and
  an existing id; `justfile` recipe `version`
  - Test first: `tests/test_versionen.py` › `test_freeze_writes_snapshot_and_entry`,
    `test_freeze_refuses_existing_id` (on a throw-away git repo in `tmp_path` with `code/` and
    `plans/`) — fails today: no `code/versionen.py`
  - Verify: `.venv/bin/python -m pytest -q tests/test_versionen.py` → green
- [x] [config] Freeze the first version: `just version "Nach Vincent & Silvia-Ideen"` (id 2026-11-25)
  - Test first: `tests/test_versionen.py` › `test_listed_versions_are_well_formed` (every entry: id
    `YYYY-MM-DD` unique, name set, its tar.gz holds `code/export_gltf.py` and the six `plans/*.svg`;
    at least one entry) — fails today: no `versionen/versionen.json`
  - Verify: `.venv/bin/python -m pytest -q tests/test_versionen.py` → green
- [x] [python] `code/versionen.py build <public>`: per version `v/<id>/frechenlehen.glb` from the
  snapshot's own exporter and `v/<id>/plans/*.svg`, cached in `tmp/versionen/<id>-<sha12>/`, plus
  `versionen.json` (newest first); last command of `npm run blueprint`; `.gitignore` the outputs
  - Test first: `tests/test_versionen.py` › `test_build_writes_glb_plans_and_list` (a glTF magic,
    the six sheets, the list; a second run takes the cache: no export) — fails today: no `build`
  - Verify: `.venv/bin/python -m pytest -q tests/test_versionen.py` → green; `cd web && npm run
    blueprint` writes `public/v/2026-11-25/`
- [x] [web] `web/src/versions.js`: `pick(list, search)`, `dataBase(base, entry)`,
  `versionHref(search, id)`
  - Test first: `web/src/versions.test.js` › Aktuell without `v`, unknown id → Aktuell, base with
    `v/<id>/`, href sets/removes `v` and keeps `cam=x,y,z` unescaped — fails today: no module
  - Verify: `cd web && npx vitest run src/versions.test.js` → green
- [x] [web] House page: load `versionen.json`, the `.glb` and plan sheets of `?v=`, drop-down
  "Version" in the title box (house page only), choosing reloads with the view kept, a frozen
  version tints the title box, the written URL keeps `v`
  - Test first: `web/e2e/versions.spec.js` › every listed version opens (ready, no page error, its
    `.glb` and plan sheet fetched from `v/<id>/`); the drop-down lists Aktuell + the versions and
    switching keeps `cam`; sub-model pages have no Version drop-down — fails today: no drop-down,
    `?v=` ignored
  - Verify: `cd web && npx playwright test e2e/versions.spec.js --project dev` → green; screenshot
    of `?v=2026-11-25` read at 1× (drop-down open, title)
- [x] [web] Offline: one cache per version (`precache.js` groups, `sw.js` `CACHES`), activate keeps
  only the current names, fetch answers from the URL's group
  - Test first: `web/src/precache.test.js` › files under `v/<id>/` go to
    `frechenlehen-v-<id>-<hash>`, its name does not change when only live files change; the worker
    source holds `CACHES` — fails today: one `FILES` list; `web/e2e-preview/offline.spec.js` ›
    `?v=2026-11-25` opens offline from the worker
  - Verify: `cd web && npx vitest run src/precache.test.js && npx playwright test
    e2e-preview/offline.spec.js` → green
- [x] [web] Update button renamed: "↻ Update laden", "↻ Update bereit – neu laden", "Suche Update …",
  "Lade Update …", "Schon aktuell ✓"
  - Test first: `web/e2e-preview/offline.spec.js` › the button is found by name "Update laden" —
    fails today: it reads "Neue Version nachladen"
  - Verify: `cd web && npx playwright test e2e-preview/offline.spec.js` → green
- [x] [docs] README (Versionen, `just version`, script table), CLAUDE.md (`versionen.py`, the
  compatibility rule), ADR-004-CTPY decision rewritten in place with a History line
  - Test first: none — docs
  - Verify: `grep -q "just version" README.md && grep -q versionen.py CLAUDE.md && grep -q
    "2026-11-25" specs/architecture/adr-004-ctpy-offline-precache-service-worker.md && bash
    .claude/skills/spec/scripts/gen-adr-index.sh --check`

System docs are updated at `/spec:archive`.
