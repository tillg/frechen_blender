---
title: "Decisions"
created: 2026-11-08
edited: 2026-11-15
---

Choices made while nobody was there to ask are logged here
(`.claude/skills/spec/reference/decisions.md`); confirmed ones are removed after review.

**Contents**

- [2026-11-15 16:33 — Implement issues #35 … #30](#run-2026-11-15-1633)
  - [16:40 — Stack the issue branches; open one PR per issue, leave merging to the user](#run-2026-11-15-1633-1)
  - [16:40 — Work the issues strictly one after another, one agent per issue](#run-2026-11-15-1633-2)
  - [16:51 — #35 as a `/spec:tweak` that commits, no change directory](#run-2026-11-15-1633-3)
  - [16:51 — Replace the Blender parity tests by a compile-only guard of the Blender scripts](#run-2026-11-15-1633-4)
  - [17:20 — Rename the former Alternativ objects: `EG_Essen_Schrank`, `EG_Speis_Rueckwand`, `EG_Pendeltuer_S`/`_N`; lamps 13, 14 into `EG_Wandlampen`](#run-2026-11-15-1633-5)
  - [17:20 — The saloon leaves keep a door clock of their own, keyed by the name `_Pendeltuer`](#run-2026-11-15-1633-6)
  - [17:20 — Delete the tests of the switch and of the default layout; port the general ones](#run-2026-11-15-1633-7)

# 2026-11-15 16:33 — Implement issues #35 … #30 {#run-2026-11-15-1633}

- **Started by:** `/autonomous`
- **Task, as given:**

  > implement gh issues
  > Implement github issues. Don't wait fopr my, takes decisions as u think best. 
  > Do the issues in this order: #35, #34, #31, #33, #32, #29, #28, #27, #26, #30
  > Make sure to always commit & push in between. Use agents to save space in your context

  Added during the run:

  > Und ganz am Ende: Den Film neu genieren und publishen

## 16:40 — Stack the issue branches; open one PR per issue, leave merging to the user {#run-2026-11-15-1633-1}

- **Status:** open
- **Overrides:** `CLAUDE.md` › GitHub issues — work on an issue starts from current `main` (here: from the previous issue's branch); `/spec:archive` — archive only after the human's approval and with no `open` decisions (here: archived on the branch after self-review, decisions stay `open`).
- **Context:** ten issues in a fixed order, almost all of them change `code/house_core.py`, the committed `plans/*.svg` and the goldens; the user is away and asked to commit & push in between, not to merge.
- **Question:** how can later issues build on earlier ones while nothing is merged without the user?
- **Decision:** each issue gets its branch `issue/<n>-<slug>` from the previous issue's branch (#35 from `main`); per issue: final check green → `/spec:adversarial-code-review` → archive on the branch → push → PR with base = the previous issue's branch (`Closes #n`), label `[under review]`. No merge.
- **Why:** later issues build on earlier ones (#34's layout under #27/#26, #33/#29 next to #30's wall); merging to `main` (which deploys Pages) is the user's call.
- **Alternatives:** merge each PR after self-review (simpler history, but bypasses the human gate and deploys unreviewed); independent branches from `main` (conflicts on plans and goldens).
- **Consequences:** merge the PRs in order (#35 first); with "delete branch on merge" GitHub retargets the next PR to `main`. A change requested in an early PR has to be carried up the stack (rebase/merge the later branches).
  #35: branch issue/35-nur-noch-threejs from main, PR https://github.com/tillg/frechen_blender/pull/36 (a tweak: no change directory, so no archive step; `specs/system/` updated in place).

## 16:40 — Work the issues strictly one after another, one agent per issue {#run-2026-11-15-1633-2}

- **Status:** open
- **Context:** the user asked to use agents to save context; the repo allows exactly one dev server (5377), which serves one working tree.
- **Question:** parallel worktrees per issue, or sequential?
- **Decision:** sequential, one `worker` agent per issue (on the issue branch in the main checkout); extra agents only inside an issue (exploration, review axes).
- **Why:** shared core, plan sheets and goldens would conflict; worktree work can't be shown on the one dev server.
- **Alternatives:** parallel worktrees (faster wall clock, but conflicts and no Show).
- **Consequences:** slower; each issue starts from the merged result of the one before.

## 16:51 — #35 as a `/spec:tweak` that commits, no change directory {#run-2026-11-15-1633-3}

- **Status:** open
- **Overrides:** `/spec:tweak` — unattended: don't commit, leave changes unstaged (here: committed and pushed on the issue branch, as the run's brief asks).
- **Context:** issue #35 "Nur noch threejs": drop the Blender tests and the rebuild/save steps from the workflow, keep the Blender scripts.
- **Question:** tweak or propose + apply?
- **Decision:** tweak: three steps (guard test, remove the Blender tests, docs); no code in `code/`, no new domain term, no ADR change (ADR-001-XEWL still holds: the Blender backend stays, it is only no longer checked). Review and archive run against the branch diff; with no change directory the review's Spec axis checks against the issue text.
- **Why:** mechanical change; a change directory would only repeat the issue.
- **Alternatives:** propose + apply (a proposal/plan for a deletion and doc edits).
- **Consequences:** no `specs/changes/35-*`; `specs/system/` updated in place.

## 16:51 — Replace the Blender parity tests by a compile-only guard of the Blender scripts {#run-2026-11-15-1633-4}

- **Status:** open
- **Context:** #35; `tests/test_blender_parity.py` (2 `slow` tests, start Blender), `tests/blender/snapshot.py` and `tests/golden/blender_snapshot.json` are the only tests that launch Blender. Last full check with parity green: `main` at 7805879 (pytest 195 passed in 67 s, Vitest 60, Playwright 106).
- **Question:** what stays to keep re-enabling Blender cheap?
- **Decision:** delete those three; add `tests/test_blender_scripts.py`, which compiles the six Blender scripts (`build_house`, `fire`, `paint`, `windrose`, `garden`, `film`) with the standard Python (no `bpy` needed). Keep `tests/fixtures/garden_blender.json` (read by `test_core.py`, no Blender), `test_film_release.py`, `test_tour.py` and `tests/golden/tour.json` (the three.js Rundgang uses the keys). `frechenlehen.blend` stays, frozen at 7805879.
- **Why:** faster dev cycles (the issue's motivation); a syntax check costs milliseconds and catches the cheapest kind of rot.
- **Alternatives:** keep parity as an opt-in marker (still drifts, golden goes stale); no guard at all.
- **Consequences:** the guard checks syntax only: the scripts can drift from the core's API unnoticed. The Blender BVH camera-clearance check of the route is dormant too; only the pure-Python route tests (`test_tour.py`: Wandlampen, Alternativ furniture) remain — a gap against all other geometry. To re-enable: restore `git show 7805879:tests/test_blender_parity.py`, `tests/blender/snapshot.py`, `tests/golden/blender_snapshot.json`, rebuild (CLAUDE.md › Blender backend), regenerate the golden, save the `.blend`.

## 17:20 — Rename the former Alternativ objects: `EG_Essen_Schrank`, `EG_Speis_Rueckwand`, `EG_Pendeltuer_S`/`_N`; lamps 13, 14 into `EG_Wandlampen` {#run-2026-11-15-1633-5}

- **Status:** open
- **Context:** `specs/changes/34-alternativ-layout-standard/` (issue #34): with Alternativ the only EG layout, the `EG_Alt_*` names name an alternative that no longer exists.
- **Question:** keep `EG_Alt_*`, rename, or reuse the names of the deleted default objects?
- **Decision:** `EG_Alt_Schrank` → `EG_Essen_Schrank` (cabinet C on the Essen's west wall), `EG_Alt_Speis` → `EG_Speis_Rueckwand` (B's board back), `EG_Alt_Pendeltuer_S`/`_N` → `EG_Pendeltuer_S`/`_N`; `EG_Alt_Wandlampen` (lamps 13, 14) folds into `EG_Wandlampen`; `speis_alt()` → `speis_essen()`.
- **Why:** "Alt" would mean nothing any more; the lamps had their own object only to carry the layout flag. `EG_Schrank` is taken (`bad.py`); reusing `EG_Speis_C` / `EG_Wandlampen_Essen` for different geometry would mislead readers of history and tests.
- **Alternatives:** keep `EG_Alt_*` (no churn, but misleading); reuse the deleted names (shorter diff in tests, but the same name for other geometry).
- **Consequences:** workers of #27 (Garderobe) and #26 (Küche hood) use the new names; old view URLs with `cut=eg_alt` fall back to the last/whole-house entry.

## 17:20 — The saloon leaves keep a door clock of their own, keyed by the name `_Pendeltuer` {#run-2026-11-15-1633-6}

- **Status:** open
- **Context:** `specs/changes/34-alternativ-layout-standard/`: `slides.js` gave the leaves of a layout variant (`extras.variant`) their own swing clock; without the flag they would join the back hall's clock.
- **Question:** fold the saloon leaves into the back hall's clock or keep their own?
- **Decision:** keep their own clock, keyed by name like the Büro door's (`_Buerotuer`).
- **Why:** five leaves on one clock would make each back-hall door move less often (and `gaeste_wc.spec.js`'s wait for a back-hall door flaky); the rhythm stays as it was in Alternativ.
- **Alternatives:** one shared clock (simpler code, but a visible change and a flaky e2e).
- **Consequences:** a name rule in `slides.js`; a renamed leaf would silently join the shared clock (`slides.test.js` pins it).

## 17:20 — Delete the tests of the switch and of the default layout; port the general ones {#run-2026-11-15-1633-7}

- **Status:** open
- **Context:** `specs/changes/34-alternativ-layout-standard/`: the issue asks to delete the default layout; several tests pin it or the switch.
- **Question:** which tests go, which are ported?
- **Decision:** deleted: `test_core.py` › `test_variant_main_objects` (default-only objects) and `test_default_layout_leaves_the_variant_out` (`default_layout()`); `test_plans.py` › `test_sheets_leave_the_variant_out`; `test_gltf.py` › `test_variant_extras`; `test_show.py` › `test_variant_objects_are_shown_in_their_entry`; `web/e2e/variant.spec.js` (entry `eg_alt`, `?layout=alt`, Skizze per variant); `lighting.test.js`'s per-layout cases. Ported: `test_variant_alt_objects` → `test_speis_essen` (same geometry asserts, new names, plus a check that no default-only object and no flag remain); the Wandlampen, lamp-clearance, swing, Speis-C geometry, route-clearance, light-count, Modell-list and door-clock tests to the one layout (counts 71 → 69 wall lights; EG lamps 35 → 33).
- **Why:** the switch and the default layout no longer exist; the general properties (lamp places, clearances, route) still hold and keep their tests.
- **Alternatives:** keep the switch tests skipped (dead weight).
- **Consequences:** none beyond the deleted code.
