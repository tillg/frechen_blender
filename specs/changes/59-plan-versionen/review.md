---
feature: 59-plan-versionen
title: "Review: Planversionen im Viewer"
status: applied
order: 5
created: 2026-11-25
edited: 2026-11-25
---
# Review: Planversionen im Viewer

**Scope:** `git diff main` (working tree, uncommitted) · **Reviewed:** 2026-11-25

## Defects

- [MEDIUM] Old versions are not fully frozen: textures and images (desk screens) load from the live
  `web/public/` (`main.js` `textureBase: BASE_URL`). Risk: renaming or deleting one breaks old
  versions. Fix: name the limit in ADR-005-JXWL, or copy referenced images into `v/<id>/`.
- [MEDIUM] Every `code/*.py` save in dev re-runs `npm run blueprint`, and `build()` removes and
  re-copies all of `public/v/` (`code/versionen.py` `build`). Risk: 404s on `v/<id>/` during the
  copy, and churn in `public/`. Fix: copy a version only when it is missing or changed, and remove
  only unlisted ones.
- [MEDIUM] `extractall(filter="data")` needs Python ≥ 3.11.4 (or a backport). The plain `python3`
  of `npm run blueprint` fails with an older interpreter; CI 3.13 and local 3.13 are fine. Fix:
  document it, or fall back.
- [LOW] A failed install leaves its new caches until a later worker activates (storage only).
- [LOW] The badge total counts files skipped as already stored (cosmetic).
- [LOW] Only one freeze per day; `just version` cannot pass `--id`.
- [LOW] Test gaps:
  - `test_versionen.py` hard-codes the 2026-11-25 entry.
  - `build()` runs only in the full tier (`slow`).
  - `sw.js` routing is covered by preview e2e only.
- [LOW] The snapshot `versionen/2026-11-25.tar.gz` is not yet staged and must be in the commit.
- [LOW] The saved view is kept per entry, not per version.
- [LOW] Sub-model links drop `v` (intended: sub-models are not versioned).
- Security: `build()` does not validate ids from `versionen.json` (a hand-edited path-like id could
  escape `public/v`). Fix: `re.fullmatch` the id in `build()`.
- Checked and fine:
  - Tar extraction is filtered.
  - The UI uses `textContent`.
  - An unknown `?v=` falls back to Aktuell.
  - A missing list gives `[]`.
  - Interrupted builds are atomic.
  - The exported `.glb` is byte-identical across hash seeds and Python 3.13/3.15.

## Standards

- **Existing tests changed** (CLAUDE.md: not without explicit permission):
  - `web/src/precache.test.js`: two tests rewritten for the `VERSION`/`FILES` → `CACHES` format.
  - `web/e2e-preview/offline.spec.js`:
    - The deploy simulations now rename the live cache instead of `VERSION`.
    - `keys()` ignores version caches.
    - The 404 injection was rewritten.
    - Button texts were renamed; the user approved "Update laden".
  - Nothing was deleted or skipped; the asserted behaviour is the same.
- CLAUDE.md's `web/` bullet does not list `versions.js` (minor).
- The `offline.js` header line carries change history (minor).
- Judgement calls:
  - The version-cache naming (`v/<id>/`, `frechenlehen-v-<id>-`) is spelled out in both
    `precache.js` and `sw.js`.
  - `LIVE` is found by what it is not.
  - `offline.spec.js` repeats its `keys()` setup.
  - The CLI's `freeze --id X name` order is fragile.
  - The title drop-down CSS repeats the toolbar's.

## Spec

- All 8 steps are implemented and their tests exist; the pytest, Vitest and grep Verify commands
  pass when re-run.
- The test is named `test_freeze_refuses_existing_id_bad_id_and_dirty_sources`, not
  `…_existing_id` as the plan says (widened).
- The build test is marked `slow` (project tiers).
- The compatibility rule ("defaults for missing extras") has no code yet: nothing is missing so far;
  the e2e loop is the guard.
- The new e2e case "a deploy keeps a stored version" is not in the plan but covers the proposal's
  outcome.
- The snapshot must be committed.

## Verdict

- Defects: 3 MEDIUM, 7 LOW, 1 security note; worst: old versions depend on live textures.
- Standards: 1 hard point (existing tests changed, awaiting the user's OK), 2 minor; worst: test
  edits.
- Spec: no missing step; worst: the snapshot is not yet staged.
- Fixed (2026-11-25, with the user's OK):
  - `build()` copies only changed versions and removes only unlisted ones (test: the inode stays).
  - It refuses non-date ids (test).
  - The live textures and the Python ≥ 3.11.4 need are named in ADR-005-JXWL; the textures also in
    the README.
  - CLAUDE.md lists `versions.js`.
  - The `offline.js` header is trimmed.
  - The snapshot is committed.
- The user approved the changed existing tests.
- Accepted as is (LOW, no user impact now):
  - orphan caches after a failed install;
  - the badge total;
  - one freeze per day (`--id` via the CLI);
  - per-entry saved views;
  - hard-coded first id in the tests;
  - `sw.js` routing covered by e2e only;
  - the naming smells.
